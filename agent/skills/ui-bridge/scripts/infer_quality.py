"""
infer_quality.py â€” Anti-slop and design diversity engine.
Provides type hierarchy, color combinations, hero/section variation, and image integration.
"""
import re
import random
import json

from anti_slop_database import (
    AntiSlopDatabase,
    FORBIDDEN_COLORS,
    FORBIDDEN_TYPOGRAPHY,
    FORBIDDEN_LAYOUT,
    FORBIDDEN_ANIMATIONS,
    FORBIDDEN_CONTENT,
    FORBIDDEN_HEADERS,
    FORBIDDEN_FOOTERS,
    PERMITTED_GRADIENTS,
    PERMITTED_FONTS,
    REQUIRED_IN_EVERY_FILE,
)


class TypeHierarchyEngine:
    TIERS = {
        'editorial_contrast': {
            'display': {'size': 'clamp(3rem,6vw,5rem)', 'weight': 900, 'tracking': '-0.04em', 'leading': 1.0},
            'h1':      {'size': 'clamp(2.25rem,4vw,3.5rem)', 'weight': 800, 'tracking': '-0.03em', 'leading': 1.1},
            'h2':      {'size': 'clamp(1.75rem,3vw,2.5rem)', 'weight': 700, 'tracking': '-0.02em', 'leading': 1.2},
            'h3':      {'size': 'clamp(1.25rem,2vw,1.75rem)', 'weight': 700, 'tracking': '-0.01em', 'leading': 1.3},
            'body':    {'size': '1.0625rem', 'weight': 400, 'tracking': '0',       'leading': 1.65},
            'small':   {'size': '0.875rem',  'weight': 400, 'tracking': '0.01em',  'leading': 1.5},
            'label':   {'size': '0.75rem',   'weight': 600, 'tracking': '0.08em',  'leading': 1.4},
        },
        'geometric_power': {
            'display': {'size': 'clamp(3.5rem,7vw,6rem)', 'weight': 900, 'tracking': '-0.05em', 'leading': 0.95},
            'h1':      {'size': 'clamp(2.5rem,5vw,4rem)', 'weight': 800, 'tracking': '-0.04em', 'leading': 1.05},
            'h2':      {'size': 'clamp(2rem,3.5vw,3rem)', 'weight': 700, 'tracking': '-0.03em', 'leading': 1.15},
            'h3':      {'size': 'clamp(1.5rem,2.5vw,2rem)', 'weight': 600, 'tracking': '-0.02em', 'leading': 1.25},
            'body':    {'size': '1rem',      'weight': 400, 'tracking': '0',       'leading': 1.6},
            'small':   {'size': '0.875rem',  'weight': 400, 'tracking': '0',       'leading': 1.5},
            'label':   {'size': '0.6875rem', 'weight': 700, 'tracking': '0.1em',   'leading': 1.4},
        },
        'humanist_warmth': {
            'display': {'size': 'clamp(2.5rem,5vw,4rem)', 'weight': 700, 'tracking': '-0.02em', 'leading': 1.1},
            'h1':      {'size': 'clamp(2rem,4vw,3rem)',   'weight': 700, 'tracking': '-0.02em', 'leading': 1.2},
            'h2':      {'size': 'clamp(1.5rem,3vw,2.25rem)', 'weight': 600, 'tracking': '-0.01em', 'leading': 1.3},
            'h3':      {'size': 'clamp(1.25rem,2vw,1.75rem)', 'weight': 600, 'tracking': '0',    'leading': 1.4},
            'body':    {'size': '1.0625rem', 'weight': 400, 'tracking': '0',       'leading': 1.7},
            'small':   {'size': '0.9375rem', 'weight': 400, 'tracking': '0',       'leading': 1.6},
            'label':   {'size': '0.8125rem', 'weight': 600, 'tracking': '0.05em',  'leading': 1.4},
        },
        'technical_precision': {
            'display': {'size': 'clamp(2.25rem,4.5vw,3.5rem)', 'weight': 800, 'tracking': '-0.03em', 'leading': 1.05},
            'h1':      {'size': 'clamp(1.875rem,3.5vw,2.75rem)', 'weight': 700, 'tracking': '-0.02em', 'leading': 1.15},
            'h2':      {'size': 'clamp(1.5rem,2.5vw,2rem)',  'weight': 600, 'tracking': '-0.01em', 'leading': 1.25},
            'h3':      {'size': 'clamp(1.125rem,1.5vw,1.5rem)', 'weight': 600, 'tracking': '0',   'leading': 1.35},
            'body':    {'size': '0.9375rem', 'weight': 400, 'tracking': '0',       'leading': 1.6},
            'small':   {'size': '0.8125rem', 'weight': 400, 'tracking': '0.01em',  'leading': 1.5},
            'label':   {'size': '0.75rem',   'weight': 500, 'tracking': '0.06em',  'leading': 1.4},
        },
        'arabic_professional': {
            'display': {'size': 'clamp(2.5rem,5vw,4rem)',    'weight': 800, 'tracking': '0', 'leading': 1.4},
            'h1':      {'size': 'clamp(2rem,4vw,3rem)',      'weight': 700, 'tracking': '0', 'leading': 1.5},
            'h2':      {'size': 'clamp(1.5rem,3vw,2.25rem)', 'weight': 600, 'tracking': '0', 'leading': 1.6},
            'h3':      {'size': 'clamp(1.25rem,2vw,1.75rem)', 'weight': 600, 'tracking': '0', 'leading': 1.7},
            'body':    {'size': '1.125rem',  'weight': 400, 'tracking': '0', 'leading': 1.9},
            'small':   {'size': '1rem',      'weight': 400, 'tracking': '0', 'leading': 1.8},
            'label':   {'size': '0.875rem',  'weight': 600, 'tracking': '0', 'leading': 1.6},
        },
        'arabic_bilingual': {
            'display': {'size': 'clamp(2.25rem,4.5vw,3.5rem)', 'weight': 700, 'tracking': '0', 'leading': 1.45},
            'h1':      {'size': 'clamp(1.875rem,3.5vw,2.75rem)', 'weight': 700, 'tracking': '0', 'leading': 1.55},
            'h2':      {'size': 'clamp(1.375rem,2.5vw,2rem)',  'weight': 600, 'tracking': '0', 'leading': 1.65},
            'h3':      {'size': 'clamp(1.125rem,1.75vw,1.5rem)', 'weight': 600, 'tracking': '0', 'leading': 1.75},
            'body':    {'size': '1.0625rem', 'weight': 400, 'tracking': '0', 'leading': 1.85},
            'small':   {'size': '0.9375rem', 'weight': 400, 'tracking': '0', 'leading': 1.75},
            'label':   {'size': '0.8125rem', 'weight': 600, 'tracking': '0', 'leading': 1.6},
        },
    }

    TIER_BY_CATEGORY = {
        'EdTech':           'humanist_warmth',
        'EdTech_Arabic':    'arabic_professional',
        'SaaS Dashboard':   'technical_precision',
        'E-commerce':       'editorial_contrast',
        'Booking Platform': 'humanist_warmth',
        'Healthcare':       'humanist_warmth',
        'Fintech':          'technical_precision',
        'Travel/Hospitality': 'editorial_contrast',
        'Food & Beverage':  'humanist_warmth',
        'Real Estate':      'editorial_contrast',
        'Creative Agency':  'geometric_power',
        'Marketing/CRM':    'editorial_contrast',
    }

    def get_tier(self, category, is_arabic):
        if is_arabic and category == 'EdTech':
            return 'arabic_professional'
        return self.TIER_BY_CATEGORY.get(category, 'humanist_warmth')

    def generate_css(self, tier_name):
        tier = self.TIERS.get(tier_name, self.TIERS['humanist_warmth'])
        lines = [':root {']
        for level, props in tier.items():
            lines.append('  --type-%s-size:     %s;' % (level, props['size']))
            lines.append('  --type-%s-weight:   %s;' % (level, props['weight']))
            lines.append('  --type-%s-tracking: %s;' % (level, props['tracking']))
            lines.append('  --type-%s-leading:  %s;' % (level, props['leading']))
        lines.append('}')
        return '\n'.join(lines)


class ColorCombinationEngine:
    COLOR_USAGE_RULES = {
        'primary_max_coverage': '15%',
        'white_min_coverage': '40%',
        'text_on_white': 'var(--color-text-primary)',
        'text_on_primary': 'var(--color-text-inverse)',
        'accent_usage': 'CTAs, highlights, badges only â€” never large sections',
        'gray_range_allowed': 'none unless explicitly approved in brand direction',
        'background_default': 'var(--color-bg)',
        'border_token': 'var(--color-border)',
    }

    FORBIDDEN_COMBINATIONS = [
        ('error text on success background', 'var(--color-error)', 'var(--color-success)'),
        ('warning text on white', 'var(--color-warning)', 'var(--color-bg)'),
        ('muted text on white below AA contrast', 'var(--color-text-tertiary)', 'var(--color-bg)'),
        ('primary on accent â€” same saturation clash', None, None),
        ('all-caps body text blocks', None, None),
        ('more than 3 distinct background colors on one page', None, None),
    ]

    def get_gradients(self, category):
        return [
            'Use approved brand tokens only; no category gradient presets.',
            'Image overlay gradients may use rgba(0,0,0,...) only when needed for readability.',
            'Section backgrounds should use approved surface tokens, not generic gray alternation.',
        ]

    def is_forbidden(self, fg_hex, bg_hex):
        for _, fg, bg in self.FORBIDDEN_COMBINATIONS:
            if fg and bg and fg.lower() == fg_hex.lower() and bg.lower() == bg_hex.lower():
                return True
        return False


class HeroVariationEngine:
    HERO_PATTERNS = [
        {
            'id': 'split-image-right',
            'description': '50/50 split â€” text left, image right',
            'structure': lambda is_arabic, gradient, image_url, h1, sub, cta: (
                '<section style="min-height:90vh;display:grid;'
                'grid-template-columns:1fr 1fr;align-items:center;'
                'background:%s;direction:%s">'
                '<div style="padding:4rem clamp(2rem,5vw,5rem)">'
                '<h1 style="font-size:var(--type-display-size,clamp(2.5rem,5vw,4rem));'
                'font-weight:var(--type-display-weight,800);line-height:1.05;margin:0 0 1.25rem">%s</h1>'
                '<p style="font-size:1.125rem;color:var(--color-text-secondary);'
                'max-width:480px;line-height:1.7;margin:0 0 2rem">%s</p>'
                '<a href="#" style="display:inline-block;background:var(--color-primary);'
                'color:#fff;padding:.875rem 2rem;border-radius:10px;font-weight:700;'
                'text-decoration:none;font-size:1rem">%s</a></div>'
                '<div style="height:100%%;overflow:hidden">'
                '<img src="%s" style="width:100%%;height:100%%;object-fit:cover" alt="Hero"/>'
                '</div></section>' % ('white', 'rtl' if is_arabic else 'ltr', h1, sub, cta, image_url)
            ),
        },
        {
            'id': 'full-bleed-image',
            'description': 'Full-viewport image with centered overlay text',
            'structure': lambda is_arabic, gradient, image_url, h1, sub, cta: (
                '<section style="position:relative;min-height:100vh;display:flex;'
                'align-items:center;justify-content:center;overflow:hidden">'
                '<img src="%s" style="position:absolute;inset:0;width:100%%;'
                'height:100%%;object-fit:cover" alt="Hero"/>'
                '<div style="position:absolute;inset:0;background:rgba(0,0,0,.55)"></div>'
                '<div style="position:relative;z-index:1;text-align:center;color:#fff;'
                'padding:2rem;max-width:800px">'
                '<h1 style="font-size:var(--type-display-size,clamp(2.5rem,5vw,4rem));'
                'font-weight:900;margin:0 0 1.25rem;line-height:1.05">%s</h1>'
                '<p style="font-size:1.25rem;opacity:.9;margin:0 0 2.5rem;line-height:1.6">%s</p>'
                '<a href="#" style="display:inline-block;background:#fff;'
                'color:var(--color-primary);padding:.875rem 2.5rem;border-radius:10px;'
                'font-weight:700;text-decoration:none">%s</a>'
                '</div></section>' % (image_url, h1, sub, cta)
            ),
        },
        {
            'id': 'gradient-mesh-abstract',
            'description': 'Gradient background with abstract shapes, centered content',
            'structure': lambda is_arabic, gradient, image_url, h1, sub, cta: (
                '<section style="min-height:90vh;background:%s;display:flex;'
                'align-items:center;justify-content:center;text-align:center;'
                'padding:4rem 1.5rem;position:relative;overflow:hidden">'
                '<div style="position:absolute;inset:0;opacity:.06;background:radial-gradient('
                'circle at 20%% 50%%,#fff 0,transparent 50%%)"></div>'
                '<div style="position:relative;z-index:1;max-width:720px">'
                '<h1 style="font-size:var(--type-display-size,clamp(2.5rem,5vw,4rem));'
                'font-weight:900;color:#fff;margin:0 0 1.25rem;line-height:1.05">%s</h1>'
                '<p style="font-size:1.25rem;color:rgba(255,255,255,.85);'
                'margin:0 0 2.5rem;line-height:1.6">%s</p>'
                '<a href="#" style="display:inline-block;background:#fff;'
                'color:var(--color-primary);padding:.875rem 2.5rem;border-radius:10px;'
                'font-weight:700;text-decoration:none">%s</a>'
                '</div></section>' % (gradient, h1, sub, cta)
            ),
        },
        {
            'id': 'centered-minimal-white',
            'description': 'Clean white background, centered headline, large subtitle',
            'structure': lambda is_arabic, gradient, image_url, h1, sub, cta: (
                '<section style="min-height:80vh;background:#fff;display:flex;'
                'align-items:center;justify-content:center;text-align:center;padding:5rem 1.5rem">'
                '<div style="max-width:680px">'
                '<h1 style="font-size:var(--type-display-size,clamp(2.5rem,5vw,4rem));'
                'font-weight:900;color:var(--color-text-primary);'
                'margin:0 0 1.25rem;line-height:1.05">%s</h1>'
                '<p style="font-size:1.25rem;color:var(--color-text-secondary);'
                'margin:0 0 2.5rem;line-height:1.6">%s</p>'
                '<div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap">'
                '<a href="#" style="background:var(--color-primary);color:#fff;'
                'padding:.875rem 2rem;border-radius:10px;font-weight:700;text-decoration:none">%s</a>'
                '<a href="#" style="background:transparent;color:var(--color-primary);'
                'border:2px solid var(--color-primary);padding:.875rem 2rem;'
                'border-radius:10px;font-weight:600;text-decoration:none">Learn more</a>'
                '</div></div></section>' % (h1, sub, cta)
            ),
        },
        {
            'id': 'dark-hero-light-text',
            'description': 'Dark gradient background with light text and accent CTA',
            'structure': lambda is_arabic, gradient, image_url, h1, sub, cta: (
                '<section style="min-height:90vh;background:linear-gradient(135deg,'
                'var(--color-primary) 0%%,var(--color-primary-dark) 100%%);display:flex;align-items:center;'
                'justify-content:center;text-align:center;padding:4rem 1.5rem">'
                '<div style="max-width:720px">'
                '<h1 style="font-size:var(--type-display-size,clamp(2.5rem,5vw,4rem));'
                'font-weight:900;color:#fff;margin:0 0 1.25rem;line-height:1.05">%s</h1>'
                '<p style="font-size:1.25rem;color:rgba(255,255,255,.75);'
                'margin:0 0 2.5rem;line-height:1.6">%s</p>'
                '<a href="#" style="display:inline-block;background:var(--color-primary);'
                'color:#fff;padding:.875rem 2.5rem;border-radius:10px;'
                'font-weight:700;text-decoration:none">%s</a>'
                '</div></section>' % (h1, sub, cta)
            ),
        },
        {
            'id': 'asymmetric-blob-shape',
            'description': 'White background with colored blob shape on one side',
            'structure': lambda is_arabic, gradient, image_url, h1, sub, cta: (
                '<section style="min-height:88vh;display:grid;grid-template-columns:1fr 1fr;'
                'align-items:center;position:relative;overflow:hidden;background:#fff">'
                '<div style="position:absolute;inset-inline-end:-200px;top:-100px;'
                'width:600px;height:600px;border-radius:50%%;'
                'background:var(--color-primary-subtle);z-index:0"></div>'
                '<div style="position:relative;z-index:1;padding:4rem clamp(2rem,5vw,5rem)">'
                '<h1 style="font-size:var(--type-display-size,clamp(2.5rem,5vw,4rem));'
                'font-weight:900;color:var(--color-text-primary);'
                'margin:0 0 1.25rem;line-height:1.05">%s</h1>'
                '<p style="font-size:1.125rem;color:var(--color-text-secondary);'
                'margin:0 0 2rem;line-height:1.7">%s</p>'
                '<a href="#" style="background:var(--color-primary);color:#fff;'
                'padding:.875rem 2rem;border-radius:10px;font-weight:700;'
                'text-decoration:none;display:inline-block">%s</a></div>'
                '<div style="position:relative;z-index:1;padding:2rem">'
                '<img src="%s" style="width:100%%;border-radius:16px;'
                'box-shadow:0 20px 60px rgba(0,0,0,.15)" alt="Hero"/>'
                '</div></section>' % (h1, sub, cta, image_url)
            ),
        },
        {
            'id': 'video-background',
            'description': 'Muted looping video background with text overlay',
            'structure': lambda is_arabic, gradient, image_url, h1, sub, cta: (
                '<section style="position:relative;min-height:100vh;display:flex;'
                'align-items:center;justify-content:center;overflow:hidden">'
                '<img src="%s" style="position:absolute;inset:0;width:100%%;'
                'height:100%%;object-fit:cover" alt="Background"/>'
                '<div style="position:absolute;inset:0;background:rgba(0,0,0,.6)"></div>'
                '<div style="position:relative;z-index:1;text-align:center;color:#fff;'
                'padding:2rem;max-width:800px">'
                '<h1 style="font-size:var(--type-display-size,clamp(2.5rem,5vw,4rem));'
                'font-weight:900;margin:0 0 1.25rem;line-height:1.05">%s</h1>'
                '<p style="font-size:1.25rem;opacity:.9;margin:0 0 2.5rem">%s</p>'
                '<a href="#" style="display:inline-block;background:var(--color-primary);'
                'color:#fff;padding:.875rem 2.5rem;border-radius:10px;'
                'font-weight:700;text-decoration:none">%s</a>'
                '</div></section>' % (image_url, h1, sub, cta)
            ),
        },
        {
            'id': 'card-grid-hero',
            'description': 'Hero text above a grid of floating cards',
            'structure': lambda is_arabic, gradient, image_url, h1, sub, cta: (
                '<section style="background:var(--color-bg-subtle);'
                'padding:5rem 1.5rem 0;text-align:center">'
                '<h1 style="font-size:var(--type-display-size,clamp(2.5rem,5vw,4rem));'
                'font-weight:900;color:var(--color-text-primary);'
                'margin:0 0 1.25rem;line-height:1.05">%s</h1>'
                '<p style="font-size:1.25rem;color:var(--color-text-secondary);'
                'margin:0 0 2.5rem;line-height:1.6;max-width:600px;margin-inline:auto">%s</p>'
                '<a href="#" style="display:inline-block;background:var(--color-primary);'
                'color:#fff;padding:.875rem 2.5rem;border-radius:10px;'
                'font-weight:700;text-decoration:none;margin-bottom:3rem">%s</a>'
                '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;'
                'max-width:900px;margin:0 auto;transform:translateY(2rem)">'
                '<div style="background:#fff;border-radius:12px;height:160px;'
                'box-shadow:0 4px 20px rgba(0,0,0,.08)"></div>'
                '<div style="background:var(--color-primary);border-radius:12px;height:200px;'
                'box-shadow:0 8px 30px rgba(37,99,235,.3)"></div>'
                '<div style="background:#fff;border-radius:12px;height:160px;'
                'box-shadow:0 4px 20px rgba(0,0,0,.08)"></div>'
                '</div></section>' % (h1, sub, cta)
            ),
        },
        {
            'id': 'stats-hero',
            'description': 'Hero with large stats numbers to establish credibility',
            'structure': lambda is_arabic, gradient, image_url, h1, sub, cta: (
                '<section style="background:var(--color-primary);'
                'padding:5rem 1.5rem;color:#fff;text-align:center">'
                '<h1 style="font-size:var(--type-display-size,clamp(2.5rem,5vw,4rem));'
                'font-weight:900;margin:0 0 1.25rem;line-height:1.05">%s</h1>'
                '<p style="font-size:1.25rem;opacity:.85;margin:0 0 2.5rem;line-height:1.6;'
                'max-width:600px;margin-inline:auto">%s</p>'
                '<a href="#" style="display:inline-block;background:#fff;'
                'color:var(--color-primary);padding:.875rem 2.5rem;'
                'border-radius:10px;font-weight:700;text-decoration:none;margin-bottom:4rem">%s</a>'
                '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:2rem;'
                'max-width:700px;margin:0 auto">'
                '<div><div style="font-size:3rem;font-weight:900">+5K</div>'
                '<div style="opacity:.75;font-size:.9rem">Students</div></div>'
                '<div><div style="font-size:3rem;font-weight:900">98%%</div>'
                '<div style="opacity:.75;font-size:.9rem">Satisfaction</div></div>'
                '<div><div style="font-size:3rem;font-weight:900">120+</div>'
                '<div style="opacity:.75;font-size:.9rem">Courses</div></div>'
                '</div></section>' % (h1, sub, cta)
            ),
        },
        {
            'id': 'angled-split',
            'description': 'Diagonal divider between content and image halves',
            'structure': lambda is_arabic, gradient, image_url, h1, sub, cta: (
                '<section style="position:relative;min-height:90vh;overflow:hidden;background:#fff">'
                '<div style="position:absolute;inset:0;background:%s;'
                'clip-path:polygon(0 0,55%% 0,45%% 100%%,0 100%%)"></div>'
                '<div style="position:absolute;inset-inline-start:55%%;inset:0;overflow:hidden">'
                '<img src="%s" style="width:100%%;height:100%%;object-fit:cover" alt=""/></div>'
                '<div style="position:relative;z-index:1;padding:5rem clamp(2rem,5vw,5rem);'
                'max-width:50%%">'
                '<h1 style="font-size:var(--type-display-size,clamp(2rem,4vw,3.5rem));'
                'font-weight:900;color:#fff;margin:0 0 1.25rem;line-height:1.1">%s</h1>'
                '<p style="font-size:1.125rem;color:rgba(255,255,255,.85);'
                'margin:0 0 2rem;line-height:1.7">%s</p>'
                '<a href="#" style="display:inline-block;background:#fff;'
                'color:var(--color-primary);padding:.875rem 2rem;'
                'border-radius:10px;font-weight:700;text-decoration:none">%s</a>'
                '</div></section>' % (gradient, image_url, h1, sub, cta)
            ),
        },
        {
            'id': 'mobile-screenshot-hero',
            'description': 'App/product screenshot mockup hero for SaaS',
            'structure': lambda is_arabic, gradient, image_url, h1, sub, cta: (
                '<section style="background:var(--color-bg-subtle);'
                'padding:5rem 1.5rem;display:grid;grid-template-columns:1fr 1fr;'
                'gap:4rem;align-items:center;max-width:1200px;margin:0 auto">'
                '<div>'
                '<h1 style="font-size:var(--type-display-size,clamp(2.5rem,5vw,4rem));'
                'font-weight:900;color:var(--color-text-primary);'
                'margin:0 0 1.25rem;line-height:1.05">%s</h1>'
                '<p style="font-size:1.125rem;color:var(--color-text-secondary);'
                'margin:0 0 2rem;line-height:1.7">%s</p>'
                '<a href="#" style="background:var(--color-primary);color:#fff;'
                'padding:.875rem 2rem;border-radius:10px;font-weight:700;'
                'text-decoration:none;display:inline-block">%s</a></div>'
                '<div style="background:#fff;border-radius:20px;padding:1.5rem;'
                'box-shadow:0 20px 60px rgba(0,0,0,.12)">'
                '<img src="%s" style="width:100%%;border-radius:12px" alt="Product"/>'
                '</div></section>' % (h1, sub, cta, image_url)
            ),
        },
        {
            'id': 'text-only-typographic',
            'description': 'Bold typography only â€” no images, pure type design',
            'structure': lambda is_arabic, gradient, image_url, h1, sub, cta: (
                '<section style="background:var(--color-primary);padding:6rem 1.5rem;text-align:center">'
                '<p style="font-size:.875rem;font-weight:700;letter-spacing:.15em;'
                'color:var(--color-primary);text-transform:uppercase;'
                'margin:0 0 1.5rem">Welcome</p>'
                '<h1 style="font-size:var(--type-display-size,clamp(3rem,7vw,5.5rem));'
                'font-weight:900;color:#fff;margin:0 0 1.5rem;line-height:0.95;'
                'letter-spacing:-0.04em">%s</h1>'
                '<p style="font-size:1.25rem;color:rgba(255,255,255,.6);'
                'margin:0 0 3rem;line-height:1.6;max-width:540px;margin-inline:auto">%s</p>'
                '<a href="#" style="display:inline-block;background:var(--color-primary);'
                'color:#fff;padding:1rem 3rem;border-radius:10px;'
                'font-weight:700;text-decoration:none;font-size:1.0625rem">%s</a>'
                '</section>' % (h1, sub, cta)
            ),
        },
    ]

    def assign_to_pages(self, pages, category, is_arabic, gradients):
        assignments = {}
        patterns = list(self.HERO_PATTERNS)

        CATEGORY_PREFERRED = {
            'EdTech':           ['split-image-right', 'gradient-mesh-abstract', 'stats-hero'],
            'SaaS Dashboard':   ['mobile-screenshot-hero', 'centered-minimal-white', 'card-grid-hero'],
            'E-commerce':       ['full-bleed-image', 'split-image-right', 'angled-split'],
            'Healthcare':       ['centered-minimal-white', 'split-image-right', 'asymmetric-blob-shape'],
            'Fintech':          ['dark-hero-light-text', 'stats-hero', 'text-only-typographic'],
            'Travel/Hospitality':['full-bleed-image', 'video-background', 'angled-split'],
            'Food & Beverage':  ['full-bleed-image', 'split-image-right', 'gradient-mesh-abstract'],
            'Real Estate':      ['full-bleed-image', 'split-image-right', 'stats-hero'],
            'Creative Agency':  ['text-only-typographic', 'angled-split', 'gradient-mesh-abstract'],
            'Marketing/CRM':    ['split-image-right', 'centered-minimal-white', 'card-grid-hero'],
            'Booking Platform': ['asymmetric-blob-shape', 'split-image-right', 'stats-hero'],
        }

        preferred = CATEGORY_PREFERRED.get(category, ['centered-minimal-white', 'split-image-right'])
        preferred_patterns  = [p for p in patterns if p['id'] in preferred]
        remaining_patterns  = [p for p in patterns if p['id'] not in preferred]
        ordered = preferred_patterns + remaining_patterns

        used = set()
        for i, page in enumerate(pages):
            slug  = page.get('slug', 'page')
            name  = page.get('name', 'Page')
            pattern = ordered[i % len(ordered)]
            if pattern['id'] in used and len(used) < len(ordered):
                pattern = next((p for p in ordered if p['id'] not in used), ordered[i % len(ordered)])
            used.add(pattern['id'])

            grad = gradients[i % len(gradients)] if gradients else 'approved-token-gradient-only'
            assignments[slug] = {
                'page_name':   name,
                'hero_pattern': pattern['id'],
                'description': pattern['description'],
                'gradient':    grad,
            }
        return assignments


class SectionVariationEngine:
    SECTION_VARIANTS = {
        'features': [
            {'id': 'icon-grid-3col',   'description': '3-column icon + title + text grid'},
            {'id': 'alternating-rows', 'description': 'Image + text alternating rows'},
            {'id': 'tab-switcher',     'description': 'Tabbed feature exploration'},
            {'id': 'numbered-steps',   'description': 'How-it-works numbered progression'},
        ],
        'testimonials': [
            {'id': 'card-carousel',    'description': 'Horizontal scrolling testimonial cards'},
            {'id': 'quote-spotlight',  'description': 'Large single quote with person photo'},
            {'id': 'grid-mosaic',      'description': '3-column asymmetric quote grid'},
            {'id': 'video-testimonial','description': 'Video thumbnail with quote below'},
        ],
        'pricing': [
            {'id': 'three-tier-cards', 'description': '3 pricing tier cards, middle highlighted'},
            {'id': 'comparison-table', 'description': 'Feature comparison table rows'},
            {'id': 'toggle-annual',    'description': 'Monthly/annual toggle with savings badge'},
        ],
        'faq': [
            {'id': 'accordion',        'description': 'Expandable accordion items'},
            {'id': 'two-column',       'description': 'Two-column Q&A grid'},
            {'id': 'chat-bubble',      'description': 'Q&A styled as chat bubbles'},
        ],
        'stats': [
            {'id': 'number-row',       'description': 'Large numbers in a horizontal strip'},
            {'id': 'infographic',      'description': 'Visual icons with animated counters'},
            {'id': 'dark-contrast',    'description': 'Dark background section with light stats'},
        ],
        'cta': [
            {'id': 'centered-banner',  'description': 'Centered CTA in a colored band'},
            {'id': 'split-with-image', 'description': 'CTA text left, decorative image right'},
            {'id': 'email-capture',    'description': 'Email input + submit on dark background'},
        ],
    }

    def assign(self, pages, category):
        assignments = {}
        for page in pages:
            slug  = page.get('slug', 'page')
            sects = page.get('estimated_sections', 4)
            page_variants = {}
            for section_type, variants in self.SECTION_VARIANTS.items():
                idx = hash(slug + section_type) % len(variants)
                page_variants[section_type] = variants[idx]['id']
            assignments[slug] = page_variants
        return assignments


class AntiSlopEnforcer:
    """
    Delegates all pattern checking to AntiSlopDatabase.
    Keeps the original enforce() API for backward compatibility.
    """

    def __init__(self):
        self.db = AntiSlopDatabase()
        # Expose for legacy callers
        self.SLOP_PATTERNS_CSS  = [(v, d.get('fix', ''))
                                   for d in FORBIDDEN_COLORS.values()
                                   if isinstance(d, dict) and d.get('css_pattern')
                                   for v in [d['css_pattern']]]
        self.SLOP_PATTERNS_HTML = [(p, 'Replace with real content')
                                   for patterns in [FORBIDDEN_CONTENT]
                                   for d in patterns.values()
                                   if isinstance(d, dict)
                                   for p in d.get('patterns', [])]
        self.REQUIRED_ELEMENTS  = {'every_page': REQUIRED_IN_EVERY_FILE}

    def check(self, html_content, filename='output.html'):
        return self.db.check_html(html_content, filename)

    def report(self, check_result):
        return self.db.generate_report(check_result)

    def must_pass(self, html_content, filename):
        result = self.check(html_content, filename)
        if not result['passes']:
            print(self.report(result))
            return False, result
        return True, result

    # Legacy API kept for backward compatibility
    def check_html(self, html_str):
        result = self.db.check_html(html_str, 'inline')
        return [{'pattern': v['id'], 'message': v['description']}
                for v in result['violations']]

    def check_css(self, css_str):
        result = self.db.check_html(css_str, 'inline-css')
        return [{'pattern': v['id'], 'message': v['description']}
                for v in result['violations']]

    def enforce(self, html_str, css_str=''):
        combined = html_str + '\n' + css_str
        result = self.db.check_html(combined, 'combined')
        return {
            'html_violations': result['violations'],
            'css_violations':  [],
            'pass':            result['passes'],
        }


class ImageIntegrationHelper:
    UNSPLASH_IDS = [
        '1522202176988-66273c2fd55f',  # 1  â€” online learning / students at laptops
        '1516321318423-f06f85e504b3',  # 2  â€” course notebook and coffee
        '1434030216411-0b793f4b6210',  # 3  â€” student writing
        '1507003211169-0a1dd7228f2d',  # 4  â€” instructor at whiteboard
        '1573496359142-b8d87734a5a2',  # 5  â€” professional consultation
        '1504674900247-0877df9cc836',  # 6  â€” food / meal
        '1476514525535-07fb3b4ae5f1',  # 7  â€” travel destination aerial
        '1506929562872-bb421503ef21',  # 8  â€” beach sunset travel
        '1551288049-bebda4e38f71',     # 9  â€” dashboard analytics screen
        '1460925895917-afdab827c52f',  # 10 â€” SaaS graphs on laptop
        '1441986300917-64674bd600d8',  # 11 â€” e-commerce product shelf
        '1523275335684-37898b6baf30',  # 12 â€” product on white
        '1559757148-5c350d0d3c56',     # 13 â€” healthcare doctor
        '1538108149393-dbfd739db8aa',  # 14 â€” hospital corridor
        '1611974789855-9c2a0a7236a3',  # 15 â€” finance / charts
        '1560448204-e02f11c3d0e2',     # 16 â€” real estate building exterior
        '1570129477492-45c003edd2be',  # 17 â€” house property exterior
        '1558655146-d09347e92766',     # 18 â€” creative design tools
        '1626785774573-4b799315345d',  # 19 â€” design mockup on screen
        '1565299624946-b28f40a0ae38',  # 20 â€” food overhead dish
        '1506126613408-eca07ce68773',  # 21 â€” yoga wellness
        '1497366216548-37526070297c',  # 22 â€” modern office space
        '1497366811353-6870744d04b2',  # 23 â€” people in meeting
        '1448387473223-5c37a5ad22d2',  # 24 â€” business handshake
        '1528702748617-c9f85b0b40da',  # 25 â€” team collaboration
        '1519389950473-47ba0277781c',  # 26 â€” abstract technology
        '1580894732444-8ecded7900cd',  # 27 â€” fintech mobile app
        '1485827404703-89b55fcc595e',  # 28 â€” robot / AI concept
        '1555255707-c07966088b7b',     # 29 â€” coding on keyboard
        '1547306843-d0574d979104',     # 30 â€” healthy meal prep
        '1470770841072-f978cf4d019e',  # 31 â€” mountain landscape travel
        '1542744094-3a31f272c490',     # 32 â€” real estate interior living
        '1497366752353-35792d523a8c',  # 33 â€” agency creative team
        '1556742031-c6961e8560b0',     # 34 â€” mobile UX design
        '1581091226825-a6a2a5aee158',  # 35 â€” tech entrepreneur
    ]

    def get_photo_url(self, index_0based, width=1200, height=675, quality=80):
        photo_id = self.UNSPLASH_IDS[index_0based % len(self.UNSPLASH_IDS)]
        return ('https://images.unsplash.com/photo-%s'
                '?w=%d&h=%d&q=%d&auto=format&fit=crop' % (photo_id, width, height, quality))

    def get_by_category_and_type(self, category, image_type='hero'):
        INDEX_MAP = {
            'EdTech':            {'hero': 0, 'card': 1, 'instructor': 3},
            'Booking Platform':  {'hero': 4, 'expert': 4},
            'Food & Beverage':   {'hero': 5, 'menu': 19},
            'Travel/Hospitality':{'hero': 6, 'destination': 7},
            'SaaS Dashboard':    {'hero': 8, 'feature': 9},
            'E-commerce':        {'hero': 10, 'product': 11},
            'Healthcare':        {'hero': 12, 'doctor': 13},
            'Fintech':           {'hero': 14},
            'Real Estate':       {'hero': 15, 'property': 16},
            'Creative Agency':   {'hero': 17, 'portfolio': 18},
            'Marketing/CRM':     {'hero': 20, 'team': 24},
        }
        category_map = INDEX_MAP.get(category, {'hero': 0})
        idx = category_map.get(image_type, 0)
        return self.get_photo_url(idx)


def run_quality_checks(design_system, pages):
    engine     = TypeHierarchyEngine()
    colors_eng = ColorCombinationEngine()
    hero_eng   = HeroVariationEngine()
    section_eng = SectionVariationEngine()
    anti_slop  = AntiSlopEnforcer()

    category   = design_system.get('category', 'EdTech')
    is_arabic  = design_system.get('is_arabic', False)

    tier_name  = engine.get_tier(category, is_arabic)
    type_css   = engine.generate_css(tier_name)
    gradients  = colors_eng.get_gradients(category)

    hero_assignments    = hero_eng.assign_to_pages(pages, category, is_arabic, gradients)
    section_assignments = section_eng.assign(pages, category)

    return {
        'type_tier':           tier_name,
        'type_css':            type_css,
        'gradients':           gradients,
        'hero_assignments':    hero_assignments,
        'section_assignments': section_assignments,
        'anti_slop_rules':     list(FORBIDDEN_COLORS.keys()) + list(FORBIDDEN_LAYOUT.keys()),
    }



