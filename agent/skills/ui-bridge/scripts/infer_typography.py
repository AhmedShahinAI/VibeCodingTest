"""
infer_typography.py — Discovers and recommends the complete typography system.
Outputs: .ui-bridge/typography.json
"""
import json
import sys
import argparse
from pathlib import Path

from infer_engine import (
    FontInferrer, ProjectTypeInferrer, LanguageInferrer,
    collect_file_contents, collect_text_lines,
)


class TypographyRecommender:

    TYPE_SCALE = {
        'display':  '4rem',
        'h1':       '3rem',
        'h2':       '2.25rem',
        'h3':       '1.875rem',
        'h4':       '1.5rem',
        'h5':       '1.25rem',
        'h6':       '1.125rem',
        'body_lg':  '1.125rem',
        'body':     '1rem',
        'body_sm':  '0.875rem',
        'caption':  '0.75rem',
        'label':    '0.6875rem',
    }

    LINE_HEIGHT = {
        'display':      1.1,
        'heading':      1.25,
        'subheading':   1.35,
        'body':         1.6,
        'body_compact': 1.4,
        'caption':      1.4,
    }

    LETTER_SPACING = {
        'display':          '-0.03em',
        'heading':          '-0.02em',
        'subheading':       '-0.01em',
        'body':             '0em',
        'label_uppercase':  '0.08em',
        'caption_uppercase':'0.1em',
    }

    FONT_WEIGHT = {
        'black':    900,
        'extrabold':800,
        'bold':     700,
        'semibold': 600,
        'medium':   500,
        'regular':  400,
        'light':    300,
    }

    def recommend(self, project_category, is_arabic, existing_fonts):
        high = [f for f in existing_fonts if f.get('confidence') == 'high']
        if len(high) < 2:
            raise RuntimeError(
                'No approved or explicit font pair found. Typography cannot use category font defaults.'
            )
        heading = next((f['name'] for f in high if f.get('role') in ('heading', 'display')), high[0]['name'])
        body = next((f['name'] for f in high if f.get('role') == 'body' and f['name'] != heading), high[-1]['name'])
        return {
            'heading': heading,
            'body': body,
            'mono': 'monospace',
            'rationale': 'Explicit project font signals only',
            'google_url': '',
        }

    def generate_css_variables(self, pair):
        lines = ['/* Typography System */', ':root {']
        lines.append("  --font-heading: '%s', sans-serif;" % pair['heading'])
        lines.append("  --font-body: '%s', sans-serif;" % pair['body'])
        lines.append("  --font-mono: '%s', monospace;" % pair['mono'])
        lines.append('')
        for name, val in self.TYPE_SCALE.items():
            lines.append('  --text-%s: %s;' % (name.replace('_', '-'), val))
        lines.append('')
        for name, val in self.LINE_HEIGHT.items():
            lines.append('  --leading-%s: %s;' % (name.replace('_', '-'), val))
        lines.append('')
        for name, val in self.LETTER_SPACING.items():
            lines.append('  --tracking-%s: %s;' % (name.replace('_', '-'), val))
        lines.append('')
        for name, val in self.FONT_WEIGHT.items():
            lines.append('  --weight-%s: %d;' % (name, val))
        lines.append('}')
        return '\n'.join(lines)

    def generate_google_fonts_import(self, pair):
        return "@import url('%s');" % pair['google_url']

    def check_existing_fonts(self, found_fonts):
        if not found_fonts:
            return {'override': False, 'reason': 'no existing fonts found'}
        high_confidence = [f for f in found_fonts if f['confidence'] == 'high']
        if high_confidence:
            return {'override': True, 'fonts': high_confidence,
                    'reason': 'existing high-confidence fonts detected'}
        return {'override': False, 'reason': 'found fonts are low confidence'}

    def generate_type_specimen_html(self, pair):
        return '''<div class="type-specimen" style="padding:2rem;font-family:\'%s\',sans-serif">
  <h1 style="font-size:3rem;font-weight:700;margin:0 0 .5rem">Display Heading</h1>
  <h2 style="font-size:2.25rem;font-weight:600;margin:0 0 .5rem">Section Heading</h2>
  <h3 style="font-size:1.875rem;font-weight:600;margin:0 0 .5rem">Subsection Heading</h3>
  <h4 style="font-size:1.5rem;font-weight:600;margin:0 0 1rem">Card Title</h4>
  <p style="font-size:1.125rem;line-height:1.6;margin:0 0 1rem;font-family:\'%s\',sans-serif">
    Body large: For introductory paragraphs and important descriptions.
  </p>
  <p style="font-size:1rem;line-height:1.6;margin:0 0 1rem;font-family:\'%s\',sans-serif">
    Body regular: The main reading text. Comfortable and clear.
  </p>
  <code style="font-size:.875rem;font-family:\'%s\',monospace">code snippet example</code>
</div>''' % (pair['heading'], pair['body'], pair['body'], pair['mono'])


def main():
    parser = argparse.ArgumentParser(description='Infer typography system')
    parser.add_argument('--root', default='.')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()

    root = Path(args.root).resolve()

    text_lines   = collect_text_lines(root)
    file_content = collect_file_contents(
        root, {'.css', '.scss', '.vue', '.jsx', '.tsx', '.html'})

    pt_result   = ProjectTypeInferrer().infer(text_lines)
    lang_result = LanguageInferrer().infer(text_lines)
    font_result = FontInferrer().infer(file_content)

    category   = pt_result.get('category', 'Generic Professional')
    is_arabic  = lang_result.get('is_arabic', False)
    ex_fonts   = font_result.get('fonts', [])

    rec = TypographyRecommender()
    pair = rec.recommend(category, is_arabic, ex_fonts)
    check = rec.check_existing_fonts(ex_fonts)

    result = {
        'category':          category,
        'is_arabic':         is_arabic,
        'recommended_pair':  pair,
        'existing_check':    check,
        'type_scale':        rec.TYPE_SCALE,
        'line_height':       rec.LINE_HEIGHT,
        'letter_spacing':    rec.LETTER_SPACING,
        'font_weight':       rec.FONT_WEIGHT,
        'css_variables':     rec.generate_css_variables(pair),
        'google_fonts_import': rec.generate_google_fonts_import(pair),
    }

    out_dir = root / '.ui-bridge'
    out_dir.mkdir(exist_ok=True)
    (out_dir / 'typography.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

    if not args.quiet:
        print('Typography: %s / %s (%s)' % (
            pair['heading'], pair['body'], category), file=sys.stderr)
        print('Saved: .ui-bridge/typography.json', file=sys.stderr)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
