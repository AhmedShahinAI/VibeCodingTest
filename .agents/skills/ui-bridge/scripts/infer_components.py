"""
infer_components.py â€” Generates all reusable component HTML for the project.
Outputs: .ui-bridge/components.json + .ui-bridge/component-library.html
"""
import json
import sys
import argparse
from pathlib import Path

from infer_engine import (
    ProjectTypeInferrer, LanguageInferrer, BrandColorInferrer,
    FontInferrer, collect_text_lines, collect_file_contents,
)
from ui_bridge_core import ApprovalStore, ensure_bridge, read_json


class ComponentLibraryBuilder:

    def _btn(self, text, variant, icon=''):
        styles = {
            'primary':   'background:var(--color-primary);color:var(--color-text-inverse);border:2px solid var(--color-primary)',
            'secondary': 'background:var(--color-surface);color:var(--color-primary);border:2px solid var(--color-primary)',
            'ghost':     'background:transparent;color:var(--color-text-secondary);border:2px solid var(--color-border)',
            'danger':    'background:var(--color-error);color:var(--color-text-inverse);border:2px solid var(--color-error)',
        }
        s = styles.get(variant, styles['primary'])
        return ('<button style="%s;padding:.625rem 1.25rem;border-radius:8px;'
                'font-size:.875rem;font-weight:600;cursor:pointer;display:inline-flex;'
                'align-items:center;gap:.5rem;transition:opacity .15s" '
                'onmouseenter="this.style.opacity=\'.85\'" '
                'onmouseleave="this.style.opacity=\'1\'">%s%s</button>'
                % (s, icon, text))

    def _input(self, label, type_='text', placeholder='', required=False):
        req = 'required' if required else ''
        return ('<div style="display:flex;flex-direction:column;gap:.375rem">'
                '<label style="font-size:.875rem;font-weight:500;'
                'color:var(--color-text-primary)">%s%s</label>'
                '<input type="%s" placeholder="%s" %s '
                'style="padding:.625rem .875rem;border:1.5px solid var(--color-border);'
                'border-radius:8px;font-size:.9375rem;outline:none;'
                'transition:border-color .15s;width:100%%;box-sizing:border-box" '
                'onfocus="this.style.borderColor=\'var(--color-primary)\'" '
                'onblur="this.style.borderColor=\'var(--color-border)\'"/></div>'
                % (label, ' *' if required else '', type_, placeholder, req))

    def _badge(self, text, variant):
        colors = {
            'success': ('var(--color-accent)', 'var(--color-surface)'),
            'warning': ('var(--color-warning)', 'var(--color-surface)'),
            'error':   ('var(--color-error)', 'var(--color-surface)'),
            'info':    ('var(--color-primary)', 'var(--color-surface)'),
            'neutral': ('var(--color-bg-subtle)', 'var(--color-text-secondary)'),
        }
        bg, fg = colors.get(variant, colors['neutral'])
        return ('<span style="background:%s;color:%s;padding:.1875rem .625rem;'
                'border-radius:9999px;font-size:.75rem;font-weight:600">%s</span>'
                % (bg, fg, text))

    def _card(self, title, content, footer=None):
        foot = ('<div style="padding:.875rem 1rem;border-top:1px solid '
                'var(--color-border);font-size:.8125rem;'
                'color:var(--color-text-tertiary)">%s</div>' % footer) if footer else ''
        return ('<div style="background:var(--color-surface);border:1px solid var(--color-border);'
                'border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.06)">'
                '<div style="padding:1.25rem 1rem">'
                '<h3 style="margin:0 0 .5rem;font-size:1rem;font-weight:600;'
                'color:var(--color-text-primary)">%s</h3>'
                '<p style="margin:0;font-size:.875rem;color:var(--color-text-secondary);line-height:1.6">%s</p></div>%s</div>'
                % (title, content, foot))

    def _stat_card(self, value, label, change=None, icon=''):
        chg_html = ''
        if change:
            color = 'var(--color-success)' if '+' in str(change) else 'var(--color-error)'
            chg_html = '<span style="font-size:.8125rem;color:%s;font-weight:500">%s</span>' % (color, change)
        return ('<div style="background:var(--color-surface);border:1px solid var(--color-border);'
                'border-radius:12px;padding:1.25rem;box-shadow:0 1px 3px rgba(0,0,0,.06)">'
                '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.75rem">'
                '<span style="font-size:.8125rem;font-weight:500;color:var(--color-text-secondary)">%s</span>'
                '<span style="font-size:1.25rem">%s</span></div>'
                '<div style="font-size:1.875rem;font-weight:700;color:var(--color-text-primary);margin-bottom:.25rem">%s</div>'
                '%s</div>' % (label, icon, value, chg_html))

    def _pagination(self, current, total):
        pages = ''.join(
            '<button style="width:36px;height:36px;border-radius:8px;border:1.5px solid %s;'
            'background:%s;color:%s;font-size:.875rem;font-weight:500;cursor:pointer">%d</button>'
            % (
                'var(--color-primary)' if i == current else 'var(--color-border)',
                'var(--color-primary)' if i == current else 'var(--color-surface)',
                'var(--color-surface)' if i == current else 'var(--color-text-primary)',
                i
            ) for i in range(1, min(total+1, 8))
        )
        return ('<nav style="display:flex;align-items:center;gap:.375rem;justify-content:center">'
                '<button style="padding:.5rem 1rem;border-radius:8px;border:1.5px solid '
                'var(--color-border);background:var(--color-surface);cursor:pointer;font-size:.875rem">'
                'Previous</button>%s'
                '<button style="padding:.5rem 1rem;border-radius:8px;border:1.5px solid '
                'var(--color-border);background:var(--color-surface);cursor:pointer;font-size:.875rem">'
                'Next</button></nav>' % pages)

    def _skeleton_card(self):
        return ('<div style="background:var(--color-surface);border:1px solid var(--color-border);'
                'border-radius:12px;overflow:hidden">'
                '<div style="height:180px;background:linear-gradient(90deg,'
                'var(--color-border) 25%,var(--color-bg-subtle) 50%,'
                'var(--color-border) 75%);background-size:200%%;'
                'animation:skeleton 1.5s ease-in-out infinite"></div>'
                '<div style="padding:1rem"><div style="height:16px;width:70%;border-radius:4px;'
                'margin-bottom:.75rem;background:linear-gradient(90deg,'
                'var(--color-border) 25%,var(--color-bg-subtle) 50%,'
                'var(--color-border) 75%);background-size:200%%;'
                'animation:skeleton 1.5s ease-in-out infinite"></div>'
                '<div style="height:12px;width:90%;border-radius:4px;background:linear-gradient('
                '90deg,var(--color-border) 25%,var(--color-bg-subtle) 50%,'
                'var(--color-border) 75%);background-size:200%%;'
                'animation:skeleton 1.5s ease-in-out infinite"></div></div></div>')

    def _empty_state(self, icon, title, description, cta=None):
        cta_html = ''
        if cta:
            cta_html = ('<a href="#" style="display:inline-flex;align-items:center;gap:.5rem;'
                        'background:var(--color-primary);color:var(--color-text-inverse);padding:.625rem 1.25rem;'
                        'border-radius:8px;text-decoration:none;font-size:.875rem;font-weight:600;'
                        'margin-top:.75rem">%s</a>' % cta)
        return ('<div style="text-align:center;padding:3rem 1.5rem">'
                '<div style="font-size:3rem;margin-bottom:1rem">%s</div>'
                '<h3 style="margin:0 0 .5rem;font-size:1.125rem;font-weight:600;'
                'color:var(--color-text-primary)">%s</h3>'
                '<p style="margin:0;font-size:.875rem;color:var(--color-text-secondary)'
                ';max-width:360px;margin-inline:auto">%s</p>%s</div>'
                % (icon, title, description, cta_html))

    # Category-specific components

    def _course_card(self, title, instructor, duration, level, price, rating, image_url):
        stars = ''.join(['&#9733;' if i < int(rating) else '&#9734;' for i in range(5)])
        return ('<div style="background:var(--color-surface);border:1px solid var(--color-border);'
                'border-radius:12px;overflow:hidden;transition:box-shadow .2s,transform .2s" '
                'onmouseenter="this.style.boxShadow=\'0 8px 25px rgba(0,0,0,.1)\';'
                'this.style.transform=\'translateY(-2px)\'" '
                'onmouseleave="this.style.boxShadow=\'\';this.style.transform=\'\'">'
                '<div style="aspect-ratio:16/9;overflow:hidden">'
                '<img src="%s" alt="%s" style="width:100%%;height:100%%;object-fit:cover;'
                'transition:transform .3s" loading="lazy"/></div>'
                '<div style="padding:1rem">'
                '<div style="display:flex;justify-content:space-between;align-items:center;'
                'margin-bottom:.5rem">'
                '<span style="font-size:.75rem;font-weight:600;color:var(--color-primary);'
                'background:var(--color-primary-subtle);padding:.125rem .625rem;'
                'border-radius:9999px">%s</span>'
                '<span style="color:var(--color-warning);font-size:.875rem">%s %.1f</span></div>'
                '<h3 style="margin:0 0 .375rem;font-size:1rem;font-weight:700;'
                'color:var(--color-text-primary);line-height:1.4">%s</h3>'
                '<p style="margin:0 0 .75rem;font-size:.8125rem;'
                'color:var(--color-text-secondary)">%s</p>'
                '<div style="display:flex;justify-content:space-between;align-items:center">'
                '<span style="font-size:.8125rem;color:var(--color-text-tertiary)">%s</span>'
                '<span style="font-size:1.125rem;font-weight:700;'
                'color:var(--color-text-primary)">%s</span></div></div></div>'
                % (image_url, title, level, stars, rating, title, instructor, duration, price))

    def _expert_card(self, name, title, avatar, rating, availability):
        return ('<div style="background:var(--color-surface);border:1px solid var(--color-border);'
                'border-radius:12px;padding:1.5rem;text-align:center">'
                '<img src="%s" alt="%s" style="width:80px;height:80px;border-radius:50%%;'
                'object-fit:cover;margin:0 auto .75rem;display:block"/>'
                '<h3 style="margin:0 0 .25rem;font-size:1rem;font-weight:700">%s</h3>'
                '<p style="margin:0 0 .75rem;font-size:.8125rem;'
                'color:var(--color-text-secondary)">%s</p>'
                '<div style="display:flex;justify-content:center;gap:.25rem;margin-bottom:.75rem">'
                '<span style="color:var(--color-warning)">&#9733;&#9733;&#9733;&#9733;&#9734;</span>'
                '<span style="font-size:.8125rem;color:var(--color-text-tertiary)">%.1f</span></div>'
                '<span style="font-size:.75rem;padding:.25rem .625rem;border-radius:9999px;'
                'background:%s;color:%s;font-weight:500">%s</span></div>'
                % (avatar, name, name, title, rating,
                   'var(--color-success-subtle)' if availability == 'Available' else 'var(--color-warning-subtle)',
                   'var(--color-success)' if availability == 'Available' else 'var(--color-warning)',
                   availability))

    def build_all_components(self, category, colors, fonts, is_arabic):
        palette = colors.get('palette', {})
        components = {}

        # Universal components
        components['button_primary']   = self._btn('Primary Button', 'primary')
        components['button_secondary'] = self._btn('Secondary', 'secondary')
        components['button_ghost']     = self._btn('Ghost Button', 'ghost')
        components['button_danger']    = self._btn('Delete', 'danger')
        components['input_text']       = self._input('Email Address', 'email', 'name@example.com', True)
        components['input_password']   = self._input('Password', 'password', 'â€¢â€¢â€¢â€¢â€¢â€¢â€¢â€¢', True)
        components['badge_success']    = self._badge('Active', 'success')
        components['badge_warning']    = self._badge('Pending', 'warning')
        components['badge_error']      = self._badge('Inactive', 'error')
        components['badge_info']       = self._badge('New', 'info')
        components['badge_neutral']    = self._badge('Draft', 'neutral')
        components['card_basic']       = self._card('Card Title', 'Card content goes here.', 'Footer info')
        components['stat_card']        = self._stat_card('12,450', 'Total Users', '+12.5%', '&#128100;')
        components['skeleton_card']    = self._skeleton_card()
        components['empty_state']      = self._empty_state('&#128269;', 'No results found',
                                                            'Try adjusting your search filters.', 'Clear filters')
        components['pagination']       = self._pagination(3, 10)

        # Category-specific
        if category == 'EdTech':
            components['course_card'] = self._course_card(
                'Advanced Arabic Typography', 'Ahmed Hassan', '12 hours', 'Intermediate',
                '1,200 EGP', 4.8,
                'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=225&q=80&auto=format&fit=crop')
            components['expert_card'] = self._expert_card(
                'Dr. Sara Ahmed', 'Senior Instructor',
                'https://i.pravatar.cc/150?img=5', 4.9, 'Available')

        elif category == 'Booking Platform':
            components['expert_card'] = self._expert_card(
                'Ahmed Al-Rashid', 'Business Consultant',
                'https://i.pravatar.cc/150?img=3', 4.7, 'Available')

        return components

    def generate_component_library_html(self, components, category, is_arabic):
        dir_attr = 'rtl' if is_arabic else 'ltr'
        items = []
        for name, html in components.items():
            items.append('<div style="padding:1.5rem;border:1px solid var(--color-border);border-radius:12px">'
                         '<p style="margin:0 0 1rem;font-size:.75rem;font-weight:600;'
                         'color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:.08em">%s</p>'
                         '%s</div>' % (name.replace('_', ' '), html))

        return ('<!DOCTYPE html><html dir="%s" lang="%s"><head>'
                '<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                '<title>Component Library â€” %s</title>'
                '<style>@keyframes skeleton{0%%{background-position:-200%% 0}100%%{background-position:200%% 0}}</style>'
                '</head><body style="padding:2rem;font-family:sans-serif;background:var(--color-bg-subtle)">'
                '<h1 style="margin:0 0 .5rem;font-size:1.5rem">Component Library</h1>'
                '<p style="margin:0 0 2rem;color:var(--color-text-secondary)">Category: %s</p>'
                '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1.5rem">'
                '%s</div></body></html>'
                % (dir_attr, 'ar' if is_arabic else 'en', category, category, ''.join(items)))

    def get_component(self, name, **kwargs):
        method_map = {
            'course_card': self._course_card,
            'expert_card': self._expert_card,
            'stat_card':   self._stat_card,
            'card':        self._card,
            'badge':       self._badge,
            'pagination':  self._pagination,
            'empty_state': self._empty_state,
        }
        if name in method_map:
            return method_map[name](**kwargs)
        return ''


def main():
    parser = argparse.ArgumentParser(description='Build component library')
    parser.add_argument('--root', default='.')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    text_lines   = collect_text_lines(root)
    file_content = collect_file_contents(
        root, {'.css', '.scss', '.vue', '.jsx', '.tsx', '.html', '.ts', '.js'})

    pt      = ProjectTypeInferrer().infer(text_lines)
    lang    = LanguageInferrer().infer(text_lines)
    colors  = BrandColorInferrer().infer(file_content)
    fonts   = FontInferrer().infer(file_content)
    if not ApprovalStore(root).is_approved("design_system"):
        raise RuntimeError("Component generation requires an approved design_system gate.")
    design_system = read_json(ensure_bridge(root) / "design-system.json", default={}) or {}
    palette = design_system.get("colors", {}).get("palette", {})
    if not palette:
        raise RuntimeError("Approved design-system.json is missing colors.palette.")

    category  = pt['category']
    is_arabic = lang['is_arabic']

    builder    = ComponentLibraryBuilder()
    components = builder.build_all_components(category, {'palette': palette}, fonts, is_arabic)

    result = {
        'category':  category,
        'is_arabic': is_arabic,
        'components': {k: v for k, v in components.items()},
    }

    out_dir = root / '.ui-bridge'
    out_dir.mkdir(exist_ok=True)
    (out_dir / 'components.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

    html = builder.generate_component_library_html(components, category, is_arabic)
    (out_dir / 'component-library.html').write_text(html, encoding='utf-8')

    if not args.quiet:
        print('Components: %d built for %s' % (len(components), category), file=sys.stderr)
        print('Saved: .ui-bridge/components.json + component-library.html', file=sys.stderr)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()


