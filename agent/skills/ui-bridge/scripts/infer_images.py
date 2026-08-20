"""
infer_images.py — Recommends image strategy for the project.
Outputs: .ui-bridge/images.json
"""
import json
import sys
import argparse
from pathlib import Path

from infer_engine import (
    ProjectTypeInferrer, LanguageInferrer,
    collect_text_lines,
)


class ImageStrategyRecommender:

    IMAGE_STRATEGY_BY_CATEGORY = {
        'EdTech': {
            'hero': {
                'style': 'illustration or photography',
                'subjects': ['diverse students learning', 'online learning setup',
                             'instructor teaching', 'course completion celebration'],
                'mood': 'aspirational, focused, warm',
                'aspect_ratio': '16:9 or 4:3',
                'unsplash_id': '1522202176988-66273c2fd55f',
                'unsplash_query': 'online learning education student',
            },
            'course_card': {
                'style': 'abstract or topic illustration',
                'aspect_ratio': '16:9',
                'unsplash_id': '1516321318423-f06f85e504b3',
                'unsplash_query': 'technology learning course',
            },
            'instructor': {
                'style': 'professional headshot',
                'aspect_ratio': '1:1 (circle crop)',
                'pravatar_seed': 10,
                'unsplash_query': 'professional teacher portrait',
            },
            'background_patterns': 'subtle grid or dot pattern, very light opacity',
        },
        'E-commerce': {
            'hero': {
                'style': 'product photography',
                'subjects': ['product on clean background', 'lifestyle product shot', 'flat lay'],
                'mood': 'clean, aspirational, product-forward',
                'aspect_ratio': '21:9 or 16:9',
                'unsplash_id': '1441986300917-64674bd600d8',
                'unsplash_query': 'product ecommerce shopping',
            },
            'product_card': {
                'style': 'product on white background',
                'aspect_ratio': '1:1 or 4:3',
                'unsplash_id': '1523275335684-37898b6baf30',
                'unsplash_query': 'product white background',
            },
            'background_patterns': 'none — keep backgrounds clean white or very light gray',
        },
        'SaaS Dashboard': {
            'hero': {
                'style': 'product screenshot or UI mockup',
                'subjects': ['dashboard screenshot', 'app interface mockup'],
                'mood': 'professional, efficient, modern',
                'aspect_ratio': '16:9',
                'unsplash_id': '1551288049-bebda4e38f71',
                'unsplash_query': 'dashboard analytics software',
            },
            'feature_image': {
                'style': 'UI screenshot in device frame',
                'aspect_ratio': '4:3',
                'unsplash_id': '1460925895917-afdab827c52f',
                'unsplash_query': 'software interface screen',
            },
            'background_patterns': 'subtle noise texture or very light geometric pattern',
        },
        'Booking Platform': {
            'hero': {
                'style': 'service environment photography',
                'subjects': ['consultation setting', 'professional meeting'],
                'mood': 'trustworthy, professional, welcoming',
                'aspect_ratio': '16:9',
                'unsplash_id': '1573496359142-b8d87734a5a2',
                'unsplash_query': 'professional consultation meeting',
            },
            'expert_photo': {
                'style': 'professional headshot',
                'aspect_ratio': '3:4',
                'pravatar_seed': 20,
                'unsplash_query': 'professional consultant portrait',
            },
            'background_patterns': 'soft wave or organic blob shapes, primary color tint',
        },
        'Healthcare': {
            'hero': {
                'style': 'clean medical photography',
                'subjects': ['doctor patient interaction', 'modern clinic'],
                'mood': 'trustworthy, clean, caring',
                'aspect_ratio': '16:9',
                'unsplash_id': '1559757148-5c350d0d3c56',
                'unsplash_query': 'healthcare doctor clinic professional',
            },
            'doctor_photo': {
                'style': 'professional medical portrait',
                'aspect_ratio': '1:1',
                'pravatar_seed': 30,
                'unsplash_query': 'doctor medical professional portrait',
            },
            'background_patterns': 'very subtle cross pattern, light green tint',
        },
        'Fintech': {
            'hero': {
                'style': 'abstract data visualization',
                'subjects': ['city skyline', 'abstract numbers', 'growth charts'],
                'mood': 'authoritative, modern, trustworthy',
                'aspect_ratio': '16:9',
                'unsplash_id': '1611974789855-9c2a0a7236a3',
                'unsplash_query': 'finance technology investment',
            },
            'background_patterns': 'dark gradient with subtle grid, or light geometric',
        },
        'Travel/Hospitality': {
            'hero': {
                'style': 'destination photography — full bleed',
                'subjects': ['scenic destination', 'travel experience'],
                'mood': 'aspirational, wanderlust, vivid',
                'aspect_ratio': '21:9 or 16:9',
                'unsplash_id': '1506929562872-bb421503ef21',
                'unsplash_query': 'travel destination scenic landscape',
            },
            'destination_card': {
                'style': 'full-bleed destination photo with text overlay',
                'aspect_ratio': '4:3',
                'unsplash_id': '1476514525535-07fb3b4ae5f1',
                'unsplash_query': 'beautiful destination travel',
            },
            'background_patterns': 'none — photos ARE the background',
        },
        'Food & Beverage': {
            'hero': {
                'style': 'food photography — hero dish',
                'subjects': ['signature dish', 'restaurant ambiance'],
                'mood': 'appetizing, warm, inviting',
                'aspect_ratio': '16:9',
                'unsplash_id': '1504674900247-0877df9cc836',
                'unsplash_query': 'food restaurant dish cuisine',
            },
            'menu_item': {
                'style': 'overhead dish photography',
                'aspect_ratio': '1:1',
                'unsplash_id': '1565299624946-b28f40a0ae38',
                'unsplash_query': 'food dish meal overhead',
            },
            'background_patterns': 'subtle grain texture, warm cream tones',
        },
        'Real Estate': {
            'hero': {
                'style': 'architectural photography — premium',
                'subjects': ['exterior architecture', 'interior living space'],
                'mood': 'aspirational, sophisticated, premium',
                'aspect_ratio': '16:9 or 21:9',
                'unsplash_id': '1560448204-e02f11c3d0e2',
                'unsplash_query': 'real estate property architecture interior',
            },
            'property_card': {
                'style': 'exterior front view',
                'aspect_ratio': '4:3',
                'unsplash_id': '1570129477492-45c003edd2be',
                'unsplash_query': 'house property exterior real estate',
            },
            'background_patterns': 'none — clean white, photos carry the weight',
        },
        'Creative Agency': {
            'hero': {
                'style': 'portfolio work or abstract creative',
                'subjects': ['creative work showcase', 'design process'],
                'mood': 'bold, creative, distinctive',
                'aspect_ratio': '16:9',
                'unsplash_id': '1558655146-d09347e92766',
                'unsplash_query': 'creative design agency portfolio',
            },
            'portfolio_item': {
                'style': 'full-bleed project screenshot or mockup',
                'aspect_ratio': '4:3 or 16:9',
                'unsplash_id': '1626785774573-4b799315345d',
                'unsplash_query': 'design project creative work',
            },
            'background_patterns': 'bold full-color sections, no patterns needed',
        },
    }

    CSS_IMAGE_HELPERS = """\
/* Image utilities */
.img-cover     { width:100%; height:100%; object-fit:cover; }
.img-contain   { width:100%; height:100%; object-fit:contain; }
.img-circle    { border-radius:50%; aspect-ratio:1; object-fit:cover; }
.img-card      { aspect-ratio:16/9; object-fit:cover; width:100%; }
.img-card-sq   { aspect-ratio:1; object-fit:cover; width:100%; }
.img-portrait  { aspect-ratio:3/4; object-fit:cover; width:100%; }
.img-hero      { width:100%; aspect-ratio:16/9; object-fit:cover; }
.img-avatar-sm { width:32px; height:32px; border-radius:50%; object-fit:cover; }
.img-avatar-md { width:48px; height:48px; border-radius:50%; object-fit:cover; }
.img-avatar-lg { width:80px; height:80px; border-radius:50%; object-fit:cover; }
.img-avatar-xl { width:120px; height:120px; border-radius:50%; object-fit:cover; }
.img-overlay   { position:relative; overflow:hidden; }
.img-overlay::after {
  content:''; position:absolute; inset:0;
  background:linear-gradient(to bottom,transparent 40%,rgba(0,0,0,.7) 100%);
}"""

    def recommend(self, project_category):
        return self.IMAGE_STRATEGY_BY_CATEGORY.get(
            project_category,
            self.IMAGE_STRATEGY_BY_CATEGORY['SaaS Dashboard'])

    def get_unsplash_url(self, photo_id, width=800, height=500, quality=80):
        return ('https://images.unsplash.com/photo-%s'
                '?w=%d&h=%d&q=%d&auto=format&fit=crop' % (photo_id, width, height, quality))

    def get_avatar_placeholder(self, seed=1, size=150):
        return 'https://i.pravatar.cc/%d?img=%d' % (size, seed)

    def generate_placeholder_html(self, image_type, unsplash_id, alt, css_class,
                                   width=800, height=500, lazy=True):
        url = self.get_unsplash_url(unsplash_id, width, height)
        loading = 'lazy' if lazy else 'eager'
        return ('<img src="%s" alt="%s" class="%s" '
                'width="%d" height="%d" loading="%s">'
                % (url, alt, css_class, width, height, loading))

    def generate_css_helpers(self):
        return self.CSS_IMAGE_HELPERS

    def generate_avatar_stack_html(self, count=5, size=40):
        imgs = []
        for i in range(count):
            url = self.get_avatar_placeholder(i + 1, size)
            imgs.append('<img src="%s" alt="User %d" '
                        'style="width:%dpx;height:%dpx;border-radius:50%%'
                        ';border:2px solid #fff;margin-inline-start:-%dpx">'
                        % (url, i + 1, size, size, size // 4 if i > 0 else 0))
        return '<div style="display:flex;align-items:center">%s</div>' % ''.join(imgs)


def main():
    parser = argparse.ArgumentParser(description='Infer image strategy')
    parser.add_argument('--root', default='.')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    text_lines = collect_text_lines(root)
    category = ProjectTypeInferrer().infer(text_lines).get('category', 'Generic Professional')

    rec = ImageStrategyRecommender()
    strategy = rec.recommend(category)

    result = {
        'category': category,
        'strategy': strategy,
        'css_helpers': rec.CSS_IMAGE_HELPERS,
    }

    out_dir = root / '.ui-bridge'
    out_dir.mkdir(exist_ok=True)
    (out_dir / 'images.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

    if not args.quiet:
        print('Images: strategy for %s' % category, file=sys.stderr)
        print('Saved: .ui-bridge/images.json', file=sys.stderr)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
