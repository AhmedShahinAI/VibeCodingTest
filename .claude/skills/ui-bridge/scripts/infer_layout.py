"""
infer_layout.py â€” Recommends header, footer, and page layout patterns.
Outputs: .ui-bridge/layout.json
"""
import json
import sys
import argparse
from pathlib import Path

from infer_engine import ProjectTypeInferrer, LanguageInferrer, collect_text_lines


class LayoutRecommender:

    HEADER_PATTERNS = {
        'EdTech': {
            'style': 'standard-with-cta', 'height': '72px', 'position': 'sticky',
            'background': 'white with subtle shadow', 'logo_position': 'right',
            'nav_position': 'center', 'cta_position': 'left',
            'cta_text_ar': 'Ø§Ø¨Ø¯Ø£ Ø§Ù„Ø¢Ù†', 'cta_text_en': 'Get Started',
            'nav_links_ar': ['Ø§Ù„Ø¯ÙˆØ±Ø§Øª', 'Ø§Ù„Ø®Ø¨Ø±Ø§Ø¡', 'Ø¹Ù† Ø§Ù„Ù…Ù†ØµØ©', 'ØªÙˆØ§ØµÙ„ Ù…Ø¹Ù†Ø§'],
            'nav_links_en': ['Courses', 'Experts', 'About', 'Contact'],
            'mobile_pattern': 'hamburger-drawer',
            'special_features': ['user avatar if logged in', 'notification bell'],
        },
        'SaaS Dashboard': {
            'style': 'sidebar-layout', 'sidebar_width': '240px',
            'sidebar_collapsed': '64px', 'top_bar_height': '60px',
            'logo_position': 'sidebar-top', 'nav_position': 'sidebar',
            'user_menu': 'top-bar-right', 'mobile_pattern': 'overlay-drawer',
            'special_features': ['workspace selector', 'search command palette'],
        },
        'E-commerce': {
            'style': 'mega-nav', 'height': '64px', 'position': 'sticky',
            'background': 'white with border-bottom',
            'logo_position': 'left', 'nav_position': 'center',
            'right_section': 'search + wishlist + cart + account',
            'mobile_pattern': 'full-screen-menu',
            'special_features': ['cart item count badge', 'search overlay'],
        },
        'Booking Platform': {
            'style': 'clean-with-phone', 'height': '72px', 'position': 'sticky',
            'logo_position': 'left', 'nav_position': 'center',
            'cta_position': 'right', 'cta_type': 'phone number + book now button',
            'mobile_pattern': 'hamburger-drawer',
        },
        'Healthcare': {
            'style': 'trustworthy-simple', 'height': '72px', 'position': 'sticky',
            'background': 'white with strong border-bottom',
            'logo_position': 'left', 'nav_position': 'right',
            'cta_text_en': 'Book Appointment',
            'trust_bar': 'above header â€” certifications and awards',
            'mobile_pattern': 'hamburger-drawer',
        },
        'Fintech': {
            'style': 'professional-dark', 'height': '68px', 'position': 'sticky',
            'background': 'primary-dark or white',
            'logo_position': 'left', 'nav_position': 'right',
            'cta_text_en': 'Open Account', 'mobile_pattern': 'hamburger-drawer',
            'special_features': ['login button', 'language switcher'],
        },
        'Travel/Hospitality': {
            'style': 'transparent-hero-overlay', 'height': '80px',
            'position': 'absolute over hero',
            'background': 'transparent, becomes white on scroll',
            'logo_position': 'left', 'nav_position': 'right',
            'cta_text_en': 'Book Now', 'mobile_pattern': 'hamburger-drawer',
        },
        'Food & Beverage': {
            'style': 'warm-simple', 'height': '70px', 'position': 'sticky',
            'background': 'primary-subtle or warm white',
            'logo_position': 'left', 'nav_position': 'center',
            'cta_text_en': 'Reserve Table', 'mobile_pattern': 'hamburger-drawer',
        },
        'Real Estate': {
            'style': 'premium-clean', 'height': '76px', 'position': 'sticky',
            'background': 'white with bottom border',
            'logo_position': 'left', 'nav_position': 'right',
            'cta_text_en': 'Search Properties', 'mobile_pattern': 'hamburger-drawer',
        },
        'Creative Agency': {
            'style': 'minimal-split', 'height': '64px', 'position': 'fixed',
            'background': 'white or transparent',
            'logo_position': 'left', 'nav_position': 'right',
            'cta_text_en': "Let's Talk", 'mobile_pattern': 'full-screen-overlay',
            'special_features': ['animated menu icon'],
        },
        'Marketing/CRM': {
            'style': 'standard-with-cta', 'height': '72px', 'position': 'sticky',
            'background': 'white with subtle shadow',
            'logo_position': 'left', 'nav_position': 'center',
            'cta_text_en': 'Get Started Free', 'mobile_pattern': 'hamburger-drawer',
        },
    }

    FOOTER_PATTERNS = {
        'EdTech': {
            'style': 'four-column',
            'columns_en': ['Company', 'Courses', 'Support', 'Follow Us'],
            'columns_ar': ['Ø§Ù„Ø´Ø±ÙƒØ©', 'Ø§Ù„Ø¯ÙˆØ±Ø§Øª', 'Ø§Ù„Ø¯Ø¹Ù…', 'ØªØ§Ø¨Ø¹Ù†Ø§'],
            'bottom_bar': 'copyright + privacy + terms',
            'background': 'bg-subtle', 'newsletter': True,
        },
        'SaaS Dashboard': {
            'style': 'three-column',
            'columns_en': ['Product', 'Company', 'Legal'],
            'bottom_bar': 'copyright + status page link',
            'background': 'bg-subtle', 'newsletter': False,
        },
        'E-commerce': {
            'style': 'five-column',
            'columns_en': ['Shop', 'Customer Service', 'Company', 'Follow Us', 'Payment'],
            'bottom_bar': 'copyright + payment icons + security badges',
            'background': 'bg-subtle', 'newsletter': True,
        },
        'Booking Platform': {
            'style': 'three-column-with-cta',
            'columns_en': ['Services', 'Company', 'Contact'],
            'bottom_bar': 'copyright + privacy',
            'background': 'primary-subtle', 'newsletter': False,
        },
        'Healthcare': {
            'style': 'four-column-with-disclaimer',
            'columns_en': ['Services', 'Doctors', 'Patients', 'About'],
            'disclaimer': 'Medical disclaimer text',
            'bottom_bar': 'copyright + privacy + terms + accreditations',
            'background': 'bg-subtle', 'newsletter': False,
        },
        'Travel/Hospitality': {
            'style': 'three-column-dark',
            'columns_en': ['Destinations', 'Services', 'Company'],
            'bottom_bar': 'copyright + payment icons',
            'background': 'dark (primary-dark)', 'newsletter': True,
        },
        'Food & Beverage': {
            'style': 'simple-warm',
            'columns_en': ['Menu', 'About', 'Find Us'],
            'bottom_bar': 'copyright + social icons',
            'background': 'warm bg-subtle', 'newsletter': True,
        },
        'Real Estate': {
            'style': 'four-column',
            'columns_en': ['Properties', 'Services', 'Company', 'Contact'],
            'bottom_bar': 'copyright + privacy',
            'background': 'bg-subtle', 'newsletter': False,
        },
        'Creative Agency': {
            'style': 'minimal-dark',
            'columns_en': ['Work', 'Studio', 'Contact'],
            'bottom_bar': 'copyright',
            'background': 'dark', 'newsletter': False,
            'special': 'large footer CTA â€” full width',
        },
        'Marketing/CRM': {
            'style': 'four-column',
            'columns_en': ['Product', 'Solutions', 'Resources', 'Company'],
            'bottom_bar': 'copyright + privacy + terms',
            'background': 'bg-subtle', 'newsletter': True,
        },
    }

    PAGE_STRUCTURE_STANDARDS = {
        'landing_page': [
            'hero (full viewport height or 80vh)',
            'social proof / logos strip',
            'features or benefits (3 or 4 items)',
            'how it works (3 steps)',
            'testimonials',
            'pricing or CTA section',
            'FAQ accordion',
            'final CTA',
            'footer',
        ],
        'listing_page': [
            'page header (title + breadcrumb + filter count)',
            'filter sidebar or filter bar',
            'results grid (with skeleton loading states)',
            'pagination or infinite scroll indicator',
            'empty state design',
            'footer',
        ],
        'detail_page': [
            'breadcrumb navigation',
            'hero section (image + key info + primary CTA)',
            'tabs or sections navigation',
            'main content area',
            'sidebar (related items or key actions)',
            'reviews or social proof',
            'related items grid',
            'footer',
        ],
        'dashboard_page': [
            'top stats bar (4 KPI cards)',
            'primary chart or visualization',
            'data table with actions',
            'secondary metrics',
            'activity feed or notifications',
        ],
        'auth_page': [
            'centered card layout',
            'logo at top',
            'form with labels above inputs',
            'primary action button (full width)',
            'alternative action link',
            'social proof below card',
        ],
        'profile_page': [
            'cover image or gradient header',
            'avatar + name + title',
            'key stats strip',
            'tab navigation',
            'content sections per tab',
            'sidebar (contact or related actions)',
        ],
    }

    PAGE_TYPE_KEYWORDS = {
        'landing_page':  ['home', 'landing', 'index', 'main'],
        'listing_page':  ['list', 'listing', 'courses', 'products', 'search', 'browse'],
        'detail_page':   ['detail', 'single', 'profile', 'show', 'view'],
        'dashboard_page':['dashboard', 'admin', 'analytics', 'metrics'],
        'auth_page':     ['login', 'signup', 'register', 'auth', 'forgot'],
        'profile_page':  ['profile', 'account', 'user', 'instructor', 'expert'],
    }

    def recommend_header(self, project_category, is_arabic):
        pattern = dict(self.HEADER_PATTERNS.get(
            project_category, self.HEADER_PATTERNS['Marketing/CRM']))
        if is_arabic:
            pattern['logo_position']  = 'right'
            pattern['nav_position']   = 'center'
            pattern['cta_position']   = 'left'
            pattern['direction'] = 'rtl'
        else:
            pattern['direction'] = 'ltr'
        return pattern

    def recommend_footer(self, project_category, is_arabic):
        pattern = dict(self.FOOTER_PATTERNS.get(
            project_category, self.FOOTER_PATTERNS.get('Marketing/CRM', {})))
        if is_arabic:
            cols = pattern.get('columns_ar', pattern.get('columns_en', []))
            pattern['columns'] = cols
            pattern['direction'] = 'rtl'
        else:
            pattern['columns'] = pattern.get('columns_en', [])
            pattern['direction'] = 'ltr'
        return pattern

    def get_page_structure(self, page_type):
        return self.PAGE_STRUCTURE_STANDARDS.get(page_type, self.PAGE_STRUCTURE_STANDARDS['detail_page'])

    def detect_page_type(self, page_name, page_sections=None):
        name = page_name.lower().replace('-', ' ').replace('_', ' ')
        for ptype, keywords in self.PAGE_TYPE_KEYWORDS.items():
            if any(kw in name for kw in keywords):
                return ptype
        return 'detail_page'

    def generate_header_html(self, pattern, colors, fonts, is_arabic):
        dir_attr  = 'rtl' if is_arabic else 'ltr'
        lang_attr = 'ar' if is_arabic else 'en'
        logo_text = 'Ø´Ø¹Ø§Ø± Ø§Ù„Ù…Ù†ØµØ©' if is_arabic else 'Brand Logo'
        cta_text  = pattern.get('cta_text_ar' if is_arabic else 'cta_text_en', 'Get Started')
        nav_links = pattern.get('nav_links_ar' if is_arabic else 'nav_links_en', ['Home', 'About'])

        nav_items = ''.join('<a href="#" style="color:var(--color-text-secondary,'
                            'var(--color-text-secondary));text-decoration:none;font-size:.9375rem;'
                            'font-weight:500;padding:.25rem .75rem;border-radius:6px;'
                            'transition:color .15s">%s</a>' % link for link in nav_links)

        return '''\
<header style="position:sticky;top:0;height:%s;background:#fff;
  border-bottom:1px solid var(--color-border);
  display:flex;align-items:center;padding:0 1.5rem;gap:1.5rem;
  z-index:100;direction:%s" dir="%s" lang="%s">
  <a href="#" style="font-weight:700;font-size:1.125rem;color:var(--color-text-primary);
    text-decoration:none;margin-inline-end:auto">%s</a>
  <nav style="display:flex;align-items:center;gap:.25rem">%s</nav>
  <a href="#" style="background:var(--color-primary);color:#fff;
    padding:.5rem 1.25rem;border-radius:8px;text-decoration:none;
    font-size:.875rem;font-weight:600;transition:opacity .15s">%s</a>
  <button class="mobile-menu-btn" onclick="document.querySelector('.mobile-nav').classList.toggle('open')"
    style="display:none;background:none;border:none;cursor:pointer;padding:.5rem"
    aria-label="Toggle menu">
    <span style="display:block;width:20px;height:2px;background:currentColor;margin:4px 0"></span>
    <span style="display:block;width:20px;height:2px;background:currentColor;margin:4px 0"></span>
    <span style="display:block;width:20px;height:2px;background:currentColor;margin:4px 0"></span>
  </button>
</header>
<style>
@media(max-width:768px){
  header nav{display:none}
  header .mobile-menu-btn{display:block!important}
}
</style>''' % (pattern.get('height', '72px'), dir_attr, dir_attr, lang_attr, logo_text,
               nav_items, cta_text)

    def generate_footer_html(self, pattern, colors, fonts, is_arabic):
        dir_attr = 'rtl' if is_arabic else 'ltr'
        cols = pattern.get('columns', ['Company', 'Links', 'Contact'])
        copy = '2025 Your Company. All rights reserved.'

        col_html = ''
        for col in cols[:4]:
            col_html += ('<div><h4 style="font-size:.875rem;font-weight:700;'
                         'margin:0 0 1rem;color:var(--color-text-primary)">'
                         '%s</h4><ul style="list-style:none;padding:0;margin:0;'
                         'display:flex;flex-direction:column;gap:.5rem">'
                         '<li><a href="#" style="color:var(--color-text-secondary,'
                         'var(--color-text-secondary));text-decoration:none;font-size:.875rem">Link 1</a></li>'
                         '<li><a href="#" style="color:var(--color-text-secondary,'
                         'var(--color-text-secondary));text-decoration:none;font-size:.875rem">Link 2</a></li>'
                         '</ul></div>' % col)

        return '''\
<footer style="background:var(--color-bg-subtle);
  border-top:1px solid var(--color-border);
  padding:3rem 1.5rem 1.5rem;direction:%s" dir="%s">
  <div style="max-width:1200px;margin:0 auto">
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:2rem;margin-bottom:2.5rem">
      %s
    </div>
    <div style="border-top:1px solid var(--color-border);
      padding-top:1.5rem;text-align:center;
      color:var(--color-text-tertiary);font-size:.8125rem">
      &copy; %s
    </div>
  </div>
</footer>''' % (dir_attr, dir_attr, col_html, copy)


def main():
    parser = argparse.ArgumentParser(description='Infer layout patterns')
    parser.add_argument('--root', default='.')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    text_lines  = collect_text_lines(root)
    category    = ProjectTypeInferrer().infer(text_lines).get('category', 'Generic Professional')
    is_arabic   = LanguageInferrer().infer(text_lines).get('is_arabic', False)

    rec = LayoutRecommender()
    header  = rec.recommend_header(category, is_arabic)
    footer  = rec.recommend_footer(category, is_arabic)

    result = {
        'category':   category,
        'is_arabic':  is_arabic,
        'header':     header,
        'footer':     footer,
        'page_structures': rec.PAGE_STRUCTURE_STANDARDS,
    }

    out_dir = root / '.ui-bridge'
    out_dir.mkdir(exist_ok=True)
    (out_dir / 'layout.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

    if not args.quiet:
        print('Layout: %s header, %s footer for %s' % (
            header['style'], footer.get('style', 'standard'), category), file=sys.stderr)
        print('Saved: .ui-bridge/layout.json', file=sys.stderr)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

