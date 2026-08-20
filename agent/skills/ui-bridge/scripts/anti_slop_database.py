"""
AI UI Slop Database — Complete Forbidden Patterns Registry

Every pattern here has been observed in 70%+ of AI-generated UIs.
Using any of these marks output as AI-generated immediately.
This database is the enforcement layer for ui-bridge quality.
"""

import re
import os
from typing import List, Dict, Optional


FORBIDDEN_COLORS = {

    # ── AI DEFAULT PALETTES ─────────────────────────────────────────
    # These exact hex values appear in 80%+ of AI-generated UIs

    "ai_purple_primary": {
        "values": ["#6366f1", "#6366F1", "#818cf8", "#7c3aed", "#7C3AED",
                   "#8b5cf6", "#8B5CF6", "#a78bfa", "#9333ea", "#9333EA",
                   "#7e22ce", "#6d28d9", "#4f46e5"],
        "description": "Indigo/violet as primary — the #1 AI color tell",
        "severity": "CRITICAL",
        "fix": "Use a color derived from the actual project brand or category preset"
    },

    "ai_gradient_primary_to_secondary": {
        "values": [
            "linear-gradient(135deg, #667eea",
            "linear-gradient(135deg, #6366f1",
            "linear-gradient(to right, #667eea",
            "linear-gradient(135deg, #7c3aed",
            "linear-gradient(135deg, #8b5cf6",
            "linear-gradient(90deg, #6366f1",
            "linear-gradient(135deg, #4f46e5",
        ],
        "description": "Purple-to-blue gradient as hero or button background",
        "severity": "CRITICAL",
        "fix": "Use solid colors or the specific permitted gradients from design-system.json"
    },

    "ai_teal_cyan_accent": {
        "values": ["#06b6d4", "#0ea5e9", "#22d3ee", "#67e8f9",
                   "#00bcd4", "#00acc1"],
        "as_primary": True,
        "description": "Cyan/teal as primary color — extremely AI-associated",
        "severity": "HIGH",
        "fix": "Teal is fine as secondary or accent, never as primary unless Healthcare/Medical"
    },

    "ai_emerald_green_accent": {
        "values": ["#10b981", "#059669"],
        "as_primary": True,
        "description": "Emerald green as primary — very common AI default",
        "severity": "HIGH",
        "fix": "Fine as success state or accent. Never as primary unless explicitly a nature/health brand"
    },

    "ai_gray_backgrounds": {
        "values": ["#f9fafb", "#f3f4f6", "#f8fafc", "#f1f5f9"],
        "as_section_background": True,
        "description": "Cool gray section alternation — every AI tool alternates white and #f9fafb",
        "severity": "HIGH",
        "fix": "Use the actual background colors: white, then primary-subtle, then surface. Or use a border to separate sections instead of background color change"
    },

    "ai_cream_beige": {
        "values": ["#fefce8", "#fef9c3", "#fffbeb", "#fdf6e3",
                   "#faf7f0", "#f5f0e8", "#fdf8f0"],
        "as_page_background": True,
        "description": "Warm cream/beige as default page background — AI taste reflex",
        "severity": "HIGH",
        "fix": "Use white (#ffffff) or derive background from brand palette"
    },

    "gradient_text_heading": {
        "css_pattern": r"background(?:-image)?\s*:[^;}]*linear-gradient[^;}]*;\s*[^}]*-webkit-background-clip\s*:\s*text|background-clip\s*:\s*text",
        "description": "Gradient text on headings — the most recognizable AI tell",
        "severity": "CRITICAL",
        "fix": "Use solid color for ALL heading text. If emphasis needed, use accent color solid."
    },

    "neon_glow_dark": {
        "css_pattern": r"box-shadow\s*:[^;]*0\s+0\s+[2-9][0-9]px",
        "description": "Neon glow effects on dark backgrounds",
        "severity": "CRITICAL",
        "fix": "Use elevation shadows (x/y offset with blur) never radial glow"
    },

    "glassmorphism": {
        "css_pattern": r"backdrop-filter\s*:\s*blur|-webkit-backdrop-filter\s*:\s*blur",
        "description": "Glassmorphism cards — peaked in 2021, now marks AI output",
        "severity": "HIGH",
        "fix": "Use solid surface colors with subtle border and light shadow"
    },
}


FORBIDDEN_TYPOGRAPHY = {

    "inter_only": {
        "css_pattern": r"font-family\s*:\s*['\"]?Inter['\"]?\s*;",
        "description": "Inter as the only font with no display/heading font contrast",
        "severity": "HIGH",
        "fix": "Always pair Inter body with a distinct display font (Playfair, Space Grotesk, Barlow Condensed etc.)"
    },

    "geist_only": {
        "css_pattern": r"font-family\s*:[^;]*Geist",
        "description": "Geist is the Next.js/Vercel default — immediately signals AI",
        "severity": "HIGH",
        "fix": "Geist is acceptable only for SaaS/dev tools with deliberate choice"
    },

    "system_ui_fallback_only": {
        "css_pattern": r"font-family\s*:\s*(-apple-system|system-ui|BlinkMacSystemFont)\s*[,;]",
        "description": "System UI stack with no actual font choice",
        "severity": "HIGH",
        "fix": "Always load a specific Google Font appropriate to the project"
    },

    "gradient_text": {
        "css_pattern": r"background[^;]*linear-gradient[^;]*;\s*[^}]*-webkit-background-clip\s*:\s*text",
        "description": "Gradient text on any element",
        "severity": "CRITICAL",
        "fix": "Solid color only for all text"
    },

    "oversized_emoji_as_icon": {
        "html_pattern": r"<(?:span|div|p)[^>]*>\s*[\U0001F300-\U0001F9FF☀-⛿✀-➿]\s*</(?:span|div|p)>",
        "description": "Emoji used as section icons or feature icons",
        "severity": "CRITICAL",
        "fix": "Use inline SVG icons from the assigned icon set (Lucide, Heroicons, Phosphor)"
    },

    "all_caps_body": {
        "css_pattern": r"text-transform\s*:\s*uppercase",
        "description": "Uppercase text applied broadly — check if used on body/paragraph content",
        "severity": "MEDIUM",
        "fix": "Uppercase only on labels/badges at 11-12px with letter-spacing"
    },

    "tight_tracking_body": {
        "css_pattern": r"letter-spacing\s*:\s*-0\.[1-9]em",
        "description": "Negative letter spacing — check if applied to body text",
        "severity": "MEDIUM",
        "fix": "Negative tracking only on display (48px+) and heading (30px+) text"
    },

    "numbered_section_markers": {
        "html_pattern": r"<(?:span|div)[^>]*>\s*0[1-6]\s*</(?:span|div)>",
        "description": "01 / 02 / 03 display numbers above section headings",
        "severity": "HIGH",
        "fix": "Use the section heading directly. Numbers only when content is genuinely sequential"
    },
}


FORBIDDEN_LAYOUT = {

    "card_inside_card": {
        "html_pattern": r'class="[^"]*card[^"]*"[^>]*>[\s\S]{0,2000}?class="[^"]*card[^"]*"',
        "description": "Cards nested inside cards — the AI layout default",
        "severity": "CRITICAL",
        "fix": "Use spacing, dividers, and typography to create hierarchy inside a single card"
    },

    "icon_tile_above_every_heading": {
        "html_pattern": r'(?:<div[^>]*class="[^"]*icon[^"]*"[^>]*>[\s\S]{0,300}<(?:h[2-6]|p)[^>]*>[\s\S]{0,300}</(?:h[2-6]|p)>\s*</div>\s*){3,}',
        "description": "Rounded square icon container above every feature heading — universal AI pattern",
        "severity": "CRITICAL",
        "fix": "Use icon LEFT of heading inline, or use icon in ONE hero feature, not all"
    },

    "hero_eyebrow_chip": {
        "html_pattern": r'<(?:span|div|p)[^>]*class="[^"]*(?:eyebrow|chip|badge-sm|label-top)[^"]*"[^>]*>[^<]{1,60}</[^>]+>\s*<h1',
        "description": "Small pill/chip immediately above H1 hero headline — AI hero signature",
        "severity": "HIGH",
        "fix": "Start hero with a strong H1 directly. Context belongs BELOW the headline."
    },

    "side_tab_card_border": {
        "css_pattern": r"border-(?:left|inline-start)\s*:\s*[3-9]px\s+solid",
        "description": "Thick colored left border on card — the most recognizable AI card tell",
        "severity": "CRITICAL",
        "fix": "Use a top accent line (2px max) OR a colored dot OR a badge. Never a thick side border."
    },

    "stat_card_four_identical": {
        "html_pattern": r'(?:<div[^>]*class="[^"]*(?:stat|metric|kpi)[^"]*"[^>]*>[\s\S]{20,400}</div>\s*){4}',
        "description": "4 identical stat cards with same background — AI dashboard signature",
        "severity": "MEDIUM",
        "fix": "Make one stat card the hero metric (larger, different treatment)"
    },

    "testimonial_three_cards": {
        "html_pattern": r'(?:<div[^>]*class="[^"]*(?:testimonial|review|quote)[^"]*"[^>]*>[\s\S]{50,800}</div>\s*){3}',
        "description": "Exactly 3 equal testimonial cards side by side — universal AI pattern",
        "severity": "MEDIUM",
        "fix": "Use carousel with one large quote, masonry layout, or 2-column with featured quote"
    },

    "pricing_three_tiers": {
        "html_pattern": r'(?:<div[^>]*class="[^"]*(?:pricing|plan|tier)[^"]*"[^>]*>[\s\S]{100,1200}</div>\s*){3}',
        "description": "3 pricing tiers with middle highlighted — in literally every AI pricing page",
        "severity": "MEDIUM",
        "fix": "Use 2 tiers for simplicity OR 4 tiers for enterprise OR a monthly/annual toggle"
    },

    "hero_avatar_stack": {
        "html_pattern": r'(?:<img[^>]*class="[^"]*avatar[^"]*"[^>]*>\s*){3,5}',
        "description": "Stack of overlapping avatars + 'trusted by X users' text — AI hero signature",
        "severity": "HIGH",
        "fix": "Use a named testimonial quote, logo strip, or award badges instead"
    },

    "six_equal_feature_cards": {
        "html_pattern": r'(?:<div[^>]*class="[^"]*(?:feature|feature-card)[^"]*"[^>]*>[\s\S]{50,500}</div>\s*){6}',
        "description": "Exactly 6 identical feature cards in a grid — the most common AI layout",
        "severity": "HIGH",
        "fix": "Use 3 or 4 features. Or alternating split layout. Or tabs. Vary the count."
    },

    "full_width_cta_section": {
        "html_pattern": r'<section[^>]*class="[^"]*cta[^"]*"[^>]*>[\s\S]{0,100}<h[23][^>]*>[\s\S]{0,100}</h[23]>[\s\S]{0,200}<a[^>]*class="[^"]*btn',
        "description": "Full-width primary-color CTA section with H2 + paragraph + single button",
        "severity": "MEDIUM",
        "fix": "Use split CTA (text left, form right) or float a card above footer or text-only CTA"
    },

    "feature_check_list": {
        "html_pattern": r'(?:<li[^>]*>[\s\S]{0,30}(?:✓|✅|check-icon)[\s\S]{0,120}</li>\s*){5,}',
        "description": "Long check-mark feature list as primary feature section",
        "severity": "MEDIUM",
        "fix": "Use feature cards with description OR alternating split sections OR comparison table"
    },

    "three_step_how_it_works": {
        "content_pattern": r'(?:Step\s+1|Step\s+One|01\.)[\s\S]{0,300}(?:Step\s+2|Step\s+Two|02\.)[\s\S]{0,300}(?:Step\s+3|Step\s+Three|03\.)',
        "description": "3-step numbered How It Works section — in every AI-generated landing page",
        "severity": "MEDIUM",
        "fix": "Only numbered steps if genuinely sequential. Otherwise use feature section."
    },
}


FORBIDDEN_ANIMATIONS = {

    "bounce_easing": {
        "css_pattern": r"animation[^;]*(?:bounce|elastic|spring)|cubic-bezier\([^)]*[2-9]\.[0-9]",
        "description": "Bounce or elastic CSS easing on UI elements",
        "severity": "CRITICAL",
        "fix": "Use ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1) or standard ease-in-out"
    },

    "spin_logo": {
        "css_pattern": r"animation\s*:[^;]*spin[^;]*linear\s+infinite",
        "description": "Infinitely spinning decorative element",
        "severity": "HIGH",
        "fix": "Static logo. Animate only on hover, not continuously."
    },

    "floating_animation": {
        "css_pattern": r"@keyframes\s+float[\s\S]{0,200}translateY",
        "description": "Continuously floating/bobbing elements",
        "severity": "HIGH",
        "fix": "Use hover-lift with CSS transition instead of continuous animation"
    },

    "pulse_on_cta": {
        "css_pattern": r"animation\s*:[^;]*pulse[^;]*;[\s\S]{0,300}class=\"[^\"]*btn",
        "description": "Pulsing glow animation on CTA buttons",
        "severity": "HIGH",
        "fix": "Strong color + solid hover state is more effective than pulsing"
    },

    "parallax_heavy": {
        "html_pattern": r"data-parallax|parallax-speed|parallax-ratio",
        "description": "Heavy parallax scrolling effects",
        "severity": "MEDIUM",
        "fix": "Subtle fade-in on scroll via IntersectionObserver only. No parallax."
    },

    "stagger_all_elements": {
        "css_pattern": r"(?:animation-delay\s*:\s*0\.[1-5]s[^}]*){4,}",
        "description": "Staggered animation on every card in a grid",
        "severity": "MEDIUM",
        "fix": "Max 3 elements staggered. Default: all fade in together."
    },

    "count_up_numbers_everywhere": {
        "html_pattern": r"data-count|countUp\(|animateCounter|data-target=\"\d",
        "description": "JavaScript number counting animation applied broadly",
        "severity": "MEDIUM",
        "fix": "Use count-up only on the ONE primary KPI section."
    },
}


FORBIDDEN_CONTENT = {

    "lorem_ipsum": {
        "content_pattern": r"[Ll]orem\s+ipsum|consectetur adipiscing",
        "description": "Lorem ipsum placeholder text anywhere",
        "severity": "CRITICAL",
        "fix": "Use realistic content specific to the project category"
    },

    "generic_feature_text": {
        "patterns": [
            "Streamline your workflow",
            "Boost your productivity",
            "Supercharge your",
            "Empower your team",
            "Next-generation platform",
            "World-class solution",
            "Enterprise-grade",
            "Cutting-edge technology",
            "Seamlessly integrate",
            "Robust and scalable",
            "Leverage the power of",
            "Transform your business",
            "Unlock your potential",
            "Take your business to the next level",
            "All-in-one solution",
            "Your success is our mission",
            "We help businesses",
            "Trusted by thousands",
            "Join our community of",
            "Start your journey",
            "The future of",
            "Revolutionize your",
        ],
        "description": "Generic AI marketing copy — identical across every AI-generated site",
        "severity": "CRITICAL",
        "fix": "Specific, concrete language: 'Reduce course creation from 3 days to 4 hours' not 'Streamline your workflow'"
    },

    "generic_cta_text": {
        "patterns": [
            "Get Started Today",
            "Start Your Free Trial",
            "Sign Up Now",
            "Click Here",
            "Try For Free",
            "Get Started For Free",
            "Start For Free",
            "Contact Us Today",
        ],
        "description": "Generic CTA button text with no specificity",
        "severity": "HIGH",
        "fix": "Specific CTAs: 'Start Building Your Course', 'Book Your First Session', 'Browse 120 Courses'"
    },

    "placeholder_names": {
        "patterns": [
            "John Doe", "Jane Doe", "John Smith", "Jane Smith",
            "User Name", "First Last", "Full Name",
            "example@email.com", "user@example.com", "email@domain.com",
            "Company Name", "Your Company", "Acme Corp", "XYZ Company",
            "Title Here", "Heading Here", "Description Here",
        ],
        "description": "Placeholder names, emails, and company names",
        "severity": "CRITICAL",
        "fix": "Use realistic names: 'Ahmed Hassan', 'Sarah Mitchell', 'TechFlow Solutions'"
    },

    "emoji_section_headers": {
        "html_pattern": r"<h[1-6][^>]*>[^<]*[\U0001F300-\U0001F9FF☀-⛿][^<]*</h[1-6]>",
        "description": "Emoji in section headings or feature titles",
        "severity": "CRITICAL",
        "fix": "Use inline SVG icons from the assigned icon set. Never emoji in headings."
    },

    "aphorism_copy": {
        "patterns": [
            "Not just a platform. A",
            "Not just a tool. A",
            "More than software. Much more",
            "Stop wasting time. Start",
            "This isn't just",
        ],
        "description": "Manufactured-contrast aphorism copy — AI writing signature",
        "severity": "HIGH",
        "fix": "State directly what the product does. No rhetorical contrasts."
    },
}


FORBIDDEN_HEADERS = {

    "transparent_with_blur": {
        "css_pattern": r"(?:position\s*:\s*(?:fixed|sticky)[\s\S]{0,200}backdrop-filter\s*:\s*blur|backdrop-filter\s*:\s*blur[\s\S]{0,200}position\s*:\s*(?:fixed|sticky))",
        "description": "Frosted glass sticky header with backdrop blur",
        "severity": "HIGH",
        "fix": "Solid background: var(--color-surface) with border-bottom: 1px solid var(--color-border)"
    },

    "mega_tall_header": {
        "css_pattern": r"(?:header|\.nav|\.navbar)[^}]*height\s*:\s*(?:[89][0-9]|[1-9]\d{2})px",
        "description": "Header taller than 80px wastes space",
        "severity": "MEDIUM",
        "fix": "Header height: 64px default, 72px maximum, 56px for compact"
    },

    "too_many_nav_items": {
        "html_pattern": r'(?:<(?:li|a)[^>]*class="[^"]*nav[^"]*"[^>]*>[\s\S]{0,120}</(?:li|a)>\s*){8,}',
        "description": "More than 7 navigation items in main nav",
        "severity": "HIGH",
        "fix": "Maximum 5 nav links. Move secondary links to a mega menu or footer."
    },

    "announcement_bar_gradient": {
        "css_pattern": r"(?:announcement|topbar|top-bar|notice-bar)[^{]*\{[^}]*background[^}]*gradient",
        "description": "Gradient announcement/notice bar above header — AI tell",
        "severity": "HIGH",
        "fix": "Announcement bar: solid primary-subtle background with primary text."
    },
}


FORBIDDEN_FOOTERS = {

    "dark_footer_with_gradient_bg": {
        "css_pattern": r"footer[^{]*\{[^}]*background[^}]*linear-gradient",
        "description": "Gradient footer background",
        "severity": "HIGH",
        "fix": "Footer background: var(--color-bg-subtle) for light sites, solid dark for dark footers."
    },

    "newsletter_in_footer_primary_bg": {
        "css_pattern": r"footer[\s\S]{0,2000}background[^}]*var\(--color-primary\)[\s\S]{0,500}input",
        "description": "Newsletter signup with primary background color in footer",
        "severity": "MEDIUM",
        "fix": "Newsletter form with neutral background. Or put newsletter in own section above footer."
    },
}


FORBIDDEN_SECTIONS = {

    "hero_blurred_orbs": {
        "css_pattern": r"border-radius\s*:\s*50%[^}]*filter\s*:\s*blur|filter\s*:\s*blur[^}]*border-radius\s*:\s*50%",
        "description": "Blurred circular orb decorations in hero",
        "severity": "HIGH",
        "fix": "Use geometric shapes or abstract SVG paths, not blurred circles"
    },

    "five_star_all_testimonials": {
        "html_pattern": r"(?:★★★★★|&#9733;&#9733;&#9733;&#9733;&#9733;|5/5|5\.0[\s\S]{0,200}){3,}",
        "description": "All testimonials showing 5 stars — looks fake",
        "severity": "MEDIUM",
        "fix": "Mix 4 and 5 star reviews. Include one 4-star to appear genuine."
    },

    "generic_testimonial_text": {
        "patterns": [
            "This product changed my life",
            "I can't imagine working without",
            "Best decision I ever made",
            "Highly recommend to everyone",
            "Amazing product, amazing team",
            "Game changer for our business",
            "We love this tool",
            "5 stars, would recommend",
        ],
        "description": "Generic testimonial copy",
        "severity": "HIGH",
        "fix": "Specific outcome quotes: 'Reduced our client onboarding from 2 weeks to 3 days'"
    },

    "sparkle_emoji_features": {
        "html_pattern": r"[✨⚡🔥💡🎯][\s\S]{0,100}[✨⚡🔥💡🎯][\s\S]{0,100}[✨⚡🔥💡🎯]",
        "description": "Sparkle/lightning emoji as feature icons",
        "severity": "CRITICAL",
        "fix": "Use inline SVG icons from the assigned icon set"
    },
}


PERMITTED_GRADIENTS = {
    "image_overlay_only": [
        "linear-gradient(to top, rgba(0,0,0,0.8) 0%, transparent 60%)",
        "linear-gradient(to bottom, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0.7) 100%)",
        "linear-gradient(to right, rgba(0,0,0,0.7) 0%, transparent 60%)",
    ],
    "subtle_section_tint": [
        "radial-gradient(ellipse 80% 50% at 20% 40%, rgba(PRIMARY_RGB, 0.08) 0%, transparent 60%)",
    ],
    "card_top_accent_only": [
        "linear-gradient(90deg, PRIMARY 0%, SECONDARY 100%) — max 4px height top border only",
    ],
    "status_indicators_only": [
        "linear-gradient(135deg, SUCCESS 0%, SUCCESS_DARK 100%) — max 100px wide badge",
    ],
}


PERMITTED_FONTS = {
    "display": [
        "Playfair Display", "Cormorant Garamond", "Libre Baskerville",
        "Space Grotesk", "Syne", "Barlow Condensed", "Oswald",
        "Plus Jakarta Sans", "Nunito", "Manrope", "Cabinet Grotesk",
    ],
    "body": [
        "Inter", "DM Sans", "Lato", "Source Sans 3", "Nunito Sans",
        "Barlow", "IBM Plex Sans", "Instrument Sans", "Outfit",
    ],
    "arabic": ["Cairo", "Tajawal", "Almarai", "IBM Plex Sans Arabic"],
    "mono":   ["JetBrains Mono", "Fira Code", "Space Mono", "IBM Plex Mono"],
}


REQUIRED_IN_EVERY_FILE = [
    "<!DOCTYPE html>",
    'charset="UTF-8"',
    'name="viewport"',
    ":root {",
    "--color-primary:",
    "--color-bg:",
    "--font-heading:",
    "--font-body:",
    "--text-h1:",
    "--space-4:",
    "--radius-md:",
    "--duration-base:",
    "--ease-primary:",
    'class="container"',
    'class="prototype-nav"',
    "@media (max-width: 768px)",
    "prefers-reduced-motion",
]


class AntiSlopDatabase:
    """
    Main enforcement class.
    Import this in infer_quality.py AntiSlopEnforcer.
    """

    def __init__(self):
        self.patterns = {
            "colors":     FORBIDDEN_COLORS,
            "typography": FORBIDDEN_TYPOGRAPHY,
            "layout":     FORBIDDEN_LAYOUT,
            "animations": FORBIDDEN_ANIMATIONS,
            "content":    FORBIDDEN_CONTENT,
            "headers":    FORBIDDEN_HEADERS,
            "footers":    FORBIDDEN_FOOTERS,
            "sections":   FORBIDDEN_SECTIONS,
        }
        self.permitted = {
            "gradients": PERMITTED_GRADIENTS,
            "fonts":     PERMITTED_FONTS,
        }
        self.required = REQUIRED_IN_EVERY_FILE

    def check_html(self, html_content: str, filename: str) -> Dict:
        """
        Run complete check against all forbidden patterns.
        Returns structured report with violations and warnings.
        """
        violations = []
        warnings = []

        for category, patterns in self.patterns.items():
            for pattern_id, pattern_data in patterns.items():
                if not isinstance(pattern_data, dict):
                    continue
                result = self._check_pattern(html_content, pattern_id, pattern_data)
                if result:
                    severity = result.get("severity", "MEDIUM")
                    if severity in ("CRITICAL", "HIGH"):
                        violations.append(result)
                    else:
                        warnings.append(result)

        missing_required = [r for r in self.required if r not in html_content]

        content_issues = self._check_content(html_content)
        violations.extend([i for i in content_issues if i.get("severity") == "CRITICAL"])
        warnings.extend([i for i in content_issues if i.get("severity") != "CRITICAL"])

        return {
            "filename":        filename,
            "passes":          len(violations) == 0 and len(missing_required) == 0,
            "violations":      violations,
            "warnings":        warnings,
            "missing_required": missing_required,
            "violation_count": len(violations),
            "warning_count":   len(warnings),
        }

    def _check_pattern(self, html: str, pid: str, pdata: dict) -> Optional[Dict]:
        triggered = False

        for key in ("css_pattern", "html_pattern", "content_pattern"):
            val = pdata.get(key)
            if val:
                try:
                    if re.search(val, html, re.IGNORECASE | re.DOTALL):
                        triggered = True
                        break
                except re.error:
                    pass

        if not triggered:
            for p in pdata.get("patterns", []):
                if p.lower() in html.lower():
                    triggered = True
                    break

        if not triggered:
            for v in pdata.get("values", []):
                if v.lower() in html.lower():
                    triggered = True
                    break

        if triggered:
            return {
                "id":          pid,
                "description": pdata.get("description", ""),
                "severity":    pdata.get("severity", "MEDIUM"),
                "fix":         pdata.get("fix", ""),
            }
        return None

    def _check_content(self, html: str) -> List[Dict]:
        issues = []

        if re.search(r'[Ll]orem\s+ipsum', html):
            issues.append({
                "id":          "lorem_ipsum_direct",
                "description": "Lorem ipsum found in content",
                "severity":    "CRITICAL",
                "fix":         "Replace with realistic project-specific content",
            })

        placeholders = [
            "Title Here", "Heading Here", "Description Here",
            "Your text here", "Add content here",
            "John Doe", "Jane Doe", "example@email.com",
            "Company Name", "Your Company",
        ]
        for p in placeholders:
            if p in html:
                issues.append({
                    "id":          "placeholder_" + re.sub(r"\W", "_", p.lower()),
                    "description": "Placeholder content found: '%s'" % p,
                    "severity":    "CRITICAL",
                    "fix":         "Replace with realistic content",
                })

        if re.search(r'<h[1-6][^>]*>[^<]*[\U0001F300-\U0001F9FF☀-⛿][^<]*</h[1-6]>', html):
            issues.append({
                "id":          "emoji_heading",
                "description": "Emoji found in heading tag",
                "severity":    "CRITICAL",
                "fix":         "Use inline SVG icon from the assigned icon set",
            })

        return issues

    def generate_report(self, check_result: Dict) -> str:
        lines = [
            "Anti-Slop Check: %s" % check_result["filename"],
            "-" * 50,
        ]

        if check_result["passes"]:
            lines.append("PASSED -- No violations found")
        else:
            lines.append("FAILED -- %d violations, %d warnings" % (
                check_result["violation_count"], check_result["warning_count"]))

        if check_result["missing_required"]:
            lines.append("\nMissing required elements (%d):" % len(check_result["missing_required"]))
            for m in check_result["missing_required"]:
                lines.append("  MISSING: %s" % m)

        if check_result["violations"]:
            lines.append("\nViolations (%d):" % len(check_result["violations"]))
            for v in check_result["violations"]:
                lines.append("  [%s] %s" % (v["severity"], v["description"]))
                if v.get("fix"):
                    lines.append("         Fix: %s" % v["fix"])

        if check_result["warnings"]:
            lines.append("\nWarnings (%d):" % len(check_result["warnings"]))
            for w in check_result["warnings"]:
                lines.append("  [WARN] %s" % w["description"])

        return "\n".join(lines)

    def get_css_forbidden_values(self) -> List[str]:
        values = []
        for data in FORBIDDEN_COLORS.values():
            if isinstance(data, dict) and "values" in data:
                values.extend(data["values"])
        return values

    def get_permitted_gradient_css(self) -> str:
        lines = ["/* PERMITTED GRADIENTS -- only these are allowed */"]
        for use_case, examples in PERMITTED_GRADIENTS.items():
            lines.append("/* %s: */" % use_case)
            for ex in examples:
                lines.append("/*   %s */" % ex)
        return "\n".join(lines)

    def count_patterns(self) -> Dict:
        totals = {cat: len(patterns) for cat, patterns in self.patterns.items()}
        totals["total"] = sum(totals.values())
        totals["required_elements"] = len(self.required)
        return totals


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python anti_slop_database.py <html_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    with open(filepath, "r", encoding="utf-8") as fh:
        content = fh.read()

    db = AntiSlopDatabase()
    result = db.check_html(content, filepath)
    print(db.generate_report(result))

    os.makedirs(".ui-bridge", exist_ok=True)
    report_path = os.path.join(".ui-bridge", "slop-check-" + os.path.basename(filepath) + ".json")
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)
    print("\nReport saved: %s" % report_path)

    sys.exit(0 if result["passes"] else 1)
