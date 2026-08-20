"""
infer_colors.py — Discovers existing colors and generates the complete color system.
Outputs: .ui-bridge/colors.json
"""
import json
import math
import re
import sys
import argparse
from pathlib import Path

from infer_engine import (
    BrandColorInferrer, ProjectTypeInferrer, LanguageInferrer,
    collect_file_contents, collect_text_lines,
)


def _hex_to_hsl(hex_color):
    h = hex_color.lstrip('#')
    if len(h) == 3:
        h = ''.join(c*2 for c in h)
    r, g, b = int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2
    if mx == mn:
        return 0, 0, l
    d = mx - mn
    s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
    if mx == r:
        hue = (g - b) / d + (6 if g < b else 0)
    elif mx == g:
        hue = (b - r) / d + 2
    else:
        hue = (r - g) / d + 4
    return hue * 60, s, l


def _hsl_to_hex(h, s, l):
    s = max(0.0, min(1.0, s))
    l = max(0.0, min(1.0, l))
    if s == 0:
        v = int(round(l * 255))
        return '#%02x%02x%02x' % (v, v, v)
    def f(n):
        k = (n + h/30) % 12
        a = s * min(l, 1 - l)
        return l - a * max(-1, min(k - 3, 9 - k, 1))
    r, g, b = int(round(f(0)*255)), int(round(f(8)*255)), int(round(f(4)*255))
    return '#%02x%02x%02x' % (r, g, b)


def _relative_luminance(hex_color):
    h = hex_color.lstrip('#')
    if len(h) == 3:
        h = ''.join(c*2 for c in h)
    def chan(c):
        v = int(c, 16) / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = chan(h[0:2]), chan(h[2:4]), chan(h[4:6])
    return 0.2126*r + 0.7152*g + 0.0722*b


class ColorSystemBuilder:
    def extract_existing(self, file_contents):
        return BrandColorInferrer().infer(file_contents)

    def generate_full_palette(self, category, existing_colors):
        color_list = existing_colors if isinstance(existing_colors, list) else existing_colors.get('colors', [])
        base = {}
        for col in color_list:
            if col['role'] == 'primary' and col['confidence'] in ('high', 'medium'):
                base['primary'] = col['value']
                h, s, l = _hex_to_hsl(col['value'])
                base['primary_dark']   = _hsl_to_hex(h, s, max(0, l - 0.08))
                base['primary_light']  = _hsl_to_hex(h, s, min(1, l + 0.08))
                base['primary_subtle'] = _hsl_to_hex(h, s * 0.2, 0.97)
                break
        if "primary" not in base:
            raise RuntimeError("No explicit primary color found. Approve brand direction before generating colors.")
        for col in color_list:
            if col['role'] in ('secondary', 'accent') and col['confidence'] in ('high', 'medium'):
                base.setdefault(col['role'], col['value'])
        base.setdefault('secondary', base['primary_dark'])
        base.setdefault('accent', base['primary_light'])
        h, s, l = _hex_to_hsl(base['primary'])
        base.update({
            'accent_subtle': _hsl_to_hex(h + 151, max(0.15, s * 0.35), 0.96),
            'warning': _hsl_to_hex(h + 82, max(0.35, s), 0.34),
            'error': _hsl_to_hex(h + 134, max(0.35, s), 0.34),
            'success': _hsl_to_hex(h + 206, max(0.35, s), 0.30),
            'bg': '#FFFFFF',
            'bg_subtle': _hsl_to_hex(h, s * 0.08, 0.98),
            'surface': '#FFFFFF',
            'border': _hsl_to_hex(h, s * 0.10, 0.86),
            'border_strong': _hsl_to_hex(h, s * 0.14, 0.72),
            'text_primary': _hsl_to_hex(h, s * 0.24, 0.13),
            'text_secondary': _hsl_to_hex(h, s * 0.16, 0.30),
            'text_tertiary': _hsl_to_hex(h, s * 0.12, 0.46),
            'text_inverse': '#FFFFFF',
        })
        return base

    def generate_css_variables(self, palette):
        lines = ['/* Color System */', ':root {']
        for key, val in palette.items():
            css_key = key.replace('_', '-')
            lines.append('  --color-%s: %s;' % (css_key, val))
        lines.append('}')
        return '\n'.join(lines)

    def generate_shade_variants(self, hex_color):
        h, s, l = _hex_to_hsl(hex_color)
        steps = {
            50:  (max(0, l * 0.7 + 0.3), s * 0.7),
            100: (max(0, l * 0.6 + 0.35), s * 0.75),
            200: (max(0, l * 0.5 + 0.4), s * 0.8),
            300: (max(0, l * 0.35 + 0.45), s * 0.85),
            400: (max(0, l * 0.2 + 0.5), s * 0.9),
            500: (l, s),
            600: (max(0, l - 0.08), min(1, s * 1.05)),
            700: (max(0, l - 0.16), min(1, s * 1.1)),
            800: (max(0, l - 0.24), min(1, s * 1.15)),
            900: (max(0, l - 0.32), min(1, s * 1.2)),
        }
        return {step: _hsl_to_hex(h, vals[1], vals[0]) for step, vals in steps.items()}

    def check_contrast(self, fg_hex, bg_hex):
        l1 = _relative_luminance(fg_hex)
        l2 = _relative_luminance(bg_hex)
        lighter, darker = max(l1, l2), min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)

    def validate_palette(self, palette):
        failures = []
        pairs = [
            ('text_primary',   'bg',         4.5, 'AA body'),
            ('text_secondary', 'bg',         4.5, 'AA body'),
            ('text_primary',   'bg_subtle',  4.5, 'AA body'),
            ('text_inverse',   'primary',    3.0, 'AA large'),
        ]
        for fg_key, bg_key, min_ratio, label in pairs:
            fg = palette.get(fg_key, '#000000')
            bg = palette.get(bg_key, '#ffffff')
            ratio = self.check_contrast(fg, bg)
            if ratio < min_ratio:
                failures.append({'pair': '%s on %s' % (fg_key, bg_key),
                                  'ratio': round(ratio, 2), 'required': min_ratio,
                                  'standard': label})
        return failures

    def generate_dark_mode_palette(self, light_palette):
        h, s, l = _hex_to_hsl(light_palette.get('primary'))
        dark = {}
        dark['bg']           = _hsl_to_hex(h, s * 0.28, 0.10)
        dark['bg_subtle']    = _hsl_to_hex(h, s * 0.24, 0.16)
        dark['surface']      = _hsl_to_hex(h, s * 0.22, 0.18)
        dark['border']       = _hsl_to_hex(h, s * 0.20, 0.28)
        dark['border_strong']= _hsl_to_hex(h, s * 0.18, 0.38)
        dark['text_primary'] = _hsl_to_hex(h, s * 0.06, 0.94)
        dark['text_secondary']= _hsl_to_hex(h, s * 0.08, 0.80)
        dark['text_tertiary']= _hsl_to_hex(h, s * 0.10, 0.66)
        dark['text_inverse'] = dark['bg']
        dark['primary']      = light_palette.get('primary_light', light_palette.get('primary'))
        dark['primary_light']= light_palette.get('primary_light')
        dark['primary_dark'] = light_palette.get('primary')
        dark['primary_subtle']= _hsl_to_hex(h, s * 0.30, 0.20)
        for k in ('secondary', 'accent', 'accent_subtle',
                  'warning', 'error', 'success'):
            dark[k] = light_palette.get(k)
        return dark

    def generate_css_output(self, palette):
        light_css = self.generate_css_variables(palette)
        dark = self.generate_dark_mode_palette(palette)
        dark_lines = ['@media (prefers-color-scheme: dark) {', '  :root {']
        for key, val in dark.items():
            dark_lines.append('    --color-%s: %s;' % (key.replace('_', '-'), val))
        dark_lines.append('  }')
        dark_lines.append('}')
        return light_css + '\n\n' + '\n'.join(dark_lines)


def main():
    parser = argparse.ArgumentParser(description='Infer color system')
    parser.add_argument('--root', default='.')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()

    root = Path(args.root).resolve()

    text_lines   = collect_text_lines(root)
    file_content = collect_file_contents(
        root, {'.css', '.scss', '.vue', '.jsx', '.tsx', '.html', '.ts', '.js'})

    category = ProjectTypeInferrer().infer(text_lines).get('category', 'Generic Professional')
    existing = BrandColorInferrer().infer(file_content)

    builder = ColorSystemBuilder()
    palette = builder.generate_full_palette(category, existing)
    failures = builder.validate_palette(palette)
    shades = builder.generate_shade_variants(palette['primary'])

    result = {
        'category':       category,
        'palette':        palette,
        'shade_variants': {'primary': shades},
        'contrast_failures': failures,
        'css_variables':  builder.generate_css_variables(palette),
        'css_with_dark':  builder.generate_css_output(palette),
        'existing_signals': existing,
    }

    out_dir = root / '.ui-bridge'
    out_dir.mkdir(exist_ok=True)
    (out_dir / 'colors.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

    if not args.quiet:
        print('Colors: primary=%s, %d contrast checks, %d failures' % (
            palette['primary'], 4, len(failures)), file=sys.stderr)
        print('Saved: .ui-bridge/colors.json', file=sys.stderr)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
