"""
infer_engine.py — Single source of truth for all UI Bridge inference logic.

Every other script imports from this file.
Stdlib only — no pip dependencies.
"""
import os
import re
import json
import math
from pathlib import Path
from ui_bridge_core import BLOCKED_DIRS, SpecKitResolver, iter_real_source_files


# ── Shared constants ──────────────────────────────────────────────────────────

SKIP_DIRS = frozenset([
    '.git', 'node_modules', '.nuxt', 'dist', 'build', '__pycache__',
    'ui-prototypes', '.specify', 'coverage', '.ui-bridge', '.output',
    '.claude', '.codex', 'ui-gernreate-from-plan', 'references', 'templates',
])

SKIP_EXTENSIONS = frozenset(['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
                              '.woff', '.woff2', '.ttf', '.eot', '.mp4', '.webm',
                              '.zip', '.tar', '.gz', '.pdf', '.lock'])

GENERIC_COLORS = frozenset([
    '#fff', '#ffffff', '#000', '#000000', '#333', '#333333',
    '#666', '#666666', '#999', '#999999', '#eee', '#eeeeee',
    '#ccc', '#cccccc', '#ddd', '#dddddd', '#f0f0f0', '#f5f5f5',
])

GENERIC_FONTS = frozenset([
    'arial', 'helvetica', 'times new roman', 'georgia', 'verdana',
    'sans-serif', 'serif', 'monospace', 'system-ui', '-apple-system',
    'tahoma', 'trebuchet ms', 'courier new', 'courier',
])


# ══════════════════════════════════════════════════════════════════════════════
# CLASS 1 — ProjectTypeInferrer
# ══════════════════════════════════════════════════════════════════════════════

class ProjectTypeInferrer:

    KEYWORDS = {
        'EdTech': [
            'course', 'courses', 'lesson', 'lessons', 'learning', 'learn',
            'student', 'students', 'teacher', 'teachers', 'instructor', 'trainer',
            'training', 'curriculum', 'module', 'quiz', 'exam', 'certificate',
            'enrollment', 'enroll', 'lms', 'elearning', 'e-learning',
            'دورة', 'دورات',
            'طالب', 'معلم',
            'تدريب', 'شهادة',
            'امتحان',
        ],
        'E-commerce': [
            'product', 'products', 'cart', 'checkout', 'shop', 'store',
            'order', 'orders', 'inventory', 'sku', 'catalog', 'wishlist',
            'payment', 'shipping', 'delivery', 'refund', 'discount', 'coupon',
            'منتج', 'سلة',
            'متجر', 'طلب',
            'شحن', 'خصم',
        ],
        'SaaS Dashboard': [
            'dashboard', 'analytics', 'metrics', 'chart', 'graph', 'report',
            'kpi', 'insight', 'subscription', 'workspace', 'team', 'organization',
            'api key', 'webhook', 'saas', 'b2b',
            'لوحة', 'تحليل',
            'تقرير', 'إحصاء',
        ],
        'Booking Platform': [
            'booking', 'appointment', 'schedule', 'calendar', 'slot', 'availability',
            'reservation', 'session', 'consultation', 'therapist',
            'حجز', 'موعد',
            'جدول', 'استشارة',
        ],
        'Healthcare': [
            'clinic', 'hospital', 'patient', 'doctor', 'medical', 'health',
            'prescription', 'diagnosis', 'treatment', 'pharmacy', 'nurse',
            'عيادة', 'مريض',
            'طبيب', 'صحة', 'دواء',
        ],
        'Fintech': [
            'finance', 'financial', 'invest', 'investment', 'bank', 'banking',
            'wallet', 'transaction', 'transfer', 'loan', 'credit', 'debit',
            'portfolio', 'stock', 'trading', 'accounting', 'invoice', 'payroll',
            'مالي', 'استثمار',
            'بنك', 'محفظة',
            'معاملة',
        ],
        'Travel/Hospitality': [
            'hotel', 'travel', 'tour', 'trip', 'destination', 'flight',
            'accommodation', 'resort', 'itinerary', 'visa', 'passport', 'tourism',
            'فندق', 'سفر',
            'رحلة', 'سياحة',
        ],
        'Food & Beverage': [
            'restaurant', 'menu', 'food', 'meal', 'recipe', 'cuisine', 'chef',
            'delivery', 'catering', 'ingredient',
            'مطعم', 'قائمة',
            'وجبة', 'طعام',
            'شيف',
        ],
        'Real Estate': [
            'property', 'real estate', 'apartment', 'house', 'rent', 'lease',
            'mortgage', 'listing', 'agent', 'broker',
            'عقار', 'شقة',
            'إيجار', 'بيع',
            'وحدة',
        ],
        'Creative Agency': [
            'agency', 'portfolio', 'creative', 'brand', 'campaign',
            'client project', 'artwork', 'motion', 'production',
            'وكالة',
            'محفظة أعمال',
            'تصميم', 'إبداع',
        ],
        'Marketing/CRM': [
            'marketing', 'crm', 'lead', 'leads', 'contact', 'campaign',
            'funnel', 'conversion', 'newsletter', 'landing', 'registration',
            'registrations',
            'تسويق',
            'عملاء محتملون',
            'حملة',
        ],
    }

    def infer(self, texts):
        combined = ' '.join(texts).lower()
        scores = {}
        all_signals = {}
        for category, keywords in self.KEYWORDS.items():
            found = [kw for kw in keywords if kw in combined]
            scores[category] = len(found)
            all_signals[category] = found

        if not scores or max(scores.values()) < 2:
            return {
                'category': 'Generic Professional',
                'confidence': 'low',
                'signals_found': 0,
                'all_signals': {},
            }

        best = max(scores, key=scores.get)
        top_score = scores[best]
        confidence = 'high' if top_score >= 5 else ('medium' if top_score >= 3 else 'low')

        return {
            'category': best,
            'confidence': confidence,
            'signals_found': top_score,
            'matched_keywords': all_signals[best],
        }


# ══════════════════════════════════════════════════════════════════════════════
# CLASS 2 — LanguageInferrer
# ══════════════════════════════════════════════════════════════════════════════

class LanguageInferrer:

    ARABIC_RANGE = re.compile(r'[؀-ۿ]')
    RTL_SIGNALS  = re.compile(
        r'rtl|dir=["\']rtl["\']|direction:\s*rtl|lang=["\']ar["\']', re.IGNORECASE
    )
    LATIN_RANGE  = re.compile(r'[A-Za-z]{3,}')

    def infer(self, texts):
        combined = ' '.join(texts)

        arabic_chars = len(self.ARABIC_RANGE.findall(combined))
        latin_words  = len(self.LATIN_RANGE.findall(combined))
        rtl_explicit = bool(self.RTL_SIGNALS.search(combined))

        is_arabic = arabic_chars > 10
        is_rtl    = is_arabic or rtl_explicit

        if is_arabic and latin_words > 50:
            primary = 'bilingual'
        elif is_arabic:
            primary = 'arabic'
        else:
            primary = 'english'

        return {
            'is_arabic':          is_arabic,
            'is_rtl':             is_rtl,
            'primary_language':   primary,
            'detected_languages': ['arabic', 'latin'] if primary == 'bilingual' else [primary],
            'arabic_char_count':  arabic_chars,
            'rtl_explicit':       rtl_explicit,
        }


# ══════════════════════════════════════════════════════════════════════════════
# CLASS 3 — BrandColorInferrer
# ══════════════════════════════════════════════════════════════════════════════

class BrandColorInferrer:

    HEX6     = re.compile(r'#[0-9A-Fa-f]{6}\b')
    HEX3     = re.compile(r'#[0-9A-Fa-f]{3}\b')
    CSS_VAR  = re.compile(
        r'--(color|primary|secondary|accent|brand|main)[\w-]*\s*:\s*([#\w(),%\s]+?)(?:;|})',
        re.IGNORECASE,
    )
    TW_COLOR = re.compile(
        r'["\'](?:primary|secondary|accent|brand)["\'][^:]*:\s*["\']([#\w]+)["\']',
        re.IGNORECASE,
    )

    def infer(self, file_contents):
        colors = []
        seen = set()

        # CSS custom properties (highest confidence)
        for m in self.CSS_VAR.finditer(file_contents):
            val = m.group(2).strip()
            hex_m = self.HEX6.search(val) or self.HEX3.search(val)
            if hex_m:
                h = hex_m.group().lower()
                if h not in GENERIC_COLORS and h not in seen:
                    seen.add(h)
                    role = self._guess_role(m.group(0))
                    colors.append({'value': h, 'confidence': 'high', 'role': role,
                                   'source': 'css-variable'})

        # Tailwind config colors
        for m in self.TW_COLOR.finditer(file_contents):
            h = m.group(1).lower()
            if h.startswith('#') and h not in GENERIC_COLORS and h not in seen:
                seen.add(h)
                colors.append({'value': h, 'confidence': 'medium', 'role': 'primary',
                                'source': 'tailwind-config'})

        # Regular hex colors
        for m in self.HEX6.finditer(file_contents):
            h = m.group().lower()
            if h not in GENERIC_COLORS and h not in seen:
                seen.add(h)
                colors.append({'value': h, 'confidence': 'low', 'role': 'unknown',
                                'source': 'css-rule'})

        return {'colors': colors[:20]}

    def _guess_role(self, ctx):
        ctx = ctx.lower()
        if 'primary' in ctx or 'main' in ctx:
            return 'primary'
        if 'secondary' in ctx:
            return 'secondary'
        if 'accent' in ctx or 'highlight' in ctx:
            return 'accent'
        return 'unknown'


# ══════════════════════════════════════════════════════════════════════════════
# CLASS 4 — FontInferrer
# ══════════════════════════════════════════════════════════════════════════════

class FontInferrer:

    GOOGLE   = re.compile(r'fonts\.googleapis\.com/css2?\?family=([^"&\s<]+)', re.IGNORECASE)
    FACE     = re.compile(r'@font-face\s*\{[^}]*font-family\s*:\s*["\']?([^"\';\}]+)', re.DOTALL)
    FAMILY   = re.compile(r'font-family\s*:\s*["\']?([^"\';\}]+)', re.IGNORECASE)
    TW_FONT  = re.compile(r'fontFamily\s*:\s*\{[^}]+["\']([^"\']+)["\']')
    VAR_FONT = re.compile(r'--(font-heading|font-body|font-display)\s*:\s*["\']?([^"\';\}]+)',
                          re.IGNORECASE)

    def infer(self, file_contents):
        fonts = []
        seen = set()

        # CSS variables (highest confidence)
        for m in self.VAR_FONT.finditer(file_contents):
            name = self._clean(m.group(2))
            if name and name.lower() not in GENERIC_FONTS and name not in seen:
                seen.add(name)
                role = 'heading' if 'heading' in m.group(1) else (
                    'body' if 'body' in m.group(1) else 'display')
                fonts.append({'name': name, 'confidence': 'high', 'role': role,
                               'source': 'css-variable'})

        # Google Fonts imports
        for m in self.GOOGLE.finditer(file_contents):
            for fam in m.group(1).split('|'):
                name = self._clean(re.sub(r':.*', '', fam).replace('+', ' '))
                if name and name.lower() not in GENERIC_FONTS and name not in seen:
                    seen.add(name)
                    fonts.append({'name': name, 'confidence': 'high', 'role': 'unknown',
                                   'source': 'google-fonts'})

        # @font-face
        for m in self.FACE.finditer(file_contents):
            name = self._clean(m.group(1))
            if name and name.lower() not in GENERIC_FONTS and name not in seen:
                seen.add(name)
                fonts.append({'name': name, 'confidence': 'high', 'role': 'unknown',
                               'source': 'font-face'})

        # Tailwind config
        for m in self.TW_FONT.finditer(file_contents):
            name = self._clean(m.group(1))
            if name and name.lower() not in GENERIC_FONTS and name not in seen:
                seen.add(name)
                fonts.append({'name': name, 'confidence': 'medium', 'role': 'unknown',
                               'source': 'tailwind-config'})

        return {'fonts': fonts[:10]}

    def _clean(self, raw):
        s = raw.strip().strip('"\'').split(',')[0].strip()
        s = re.sub(r'\s+', ' ', s)
        return s if len(s) > 1 else ''


# ══════════════════════════════════════════════════════════════════════════════
# CLASS 5 — PageInventoryInferrer
# ══════════════════════════════════════════════════════════════════════════════

class PageInventoryInferrer:

    NUXT_PAGE  = re.compile(r'pages/([a-zA-Z0-9/_\[\]-]+)\.(vue|jsx|tsx|astro|svelte)')
    NEXT_PAGE  = re.compile(r'app/([a-zA-Z0-9/_\[\]-]+)/page\.(tsx|jsx|js)')
    REACT_VIEW = re.compile(r'views?/([a-zA-Z0-9/_-]+)\.(vue|jsx|tsx)')
    SCREENS    = re.compile(r'screens/([a-zA-Z0-9/_-]+)\.(tsx|jsx|vue)')

    BACKEND_RE = re.compile(
        r'\b(service|services|controller|middleware|route(?:r|s)?|endpoint|migration|'
        r'model|repository|handler|database|schema|redis|email|smtp|cron|webhook|'
        r'job|queue|seed|fixture|jwt|token|session|resolver|dto|validator|'
        r'api/|/api|\.spec\.|\.test\.)\b',
        re.IGNORECASE,
    )

    SEMANTIC = re.compile(
        r'(?:build|create|design|implement|develop|add)\s+(?:the\s+)?'
        r'([A-Za-z][A-Za-z0-9 \-]{2,40}?)\s+(?:page|screen|view|interface|dashboard)\b',
        re.IGNORECASE,
    )

    COMPOUND = re.compile(
        r'(?:build|create|design|implement|develop|add)\s+(?:the\s+)?'
        r'(homepage|loginpage|signuppage|registerpage)',
        re.IGNORECASE,
    )

    COMPOUND_SLUGS = {'homepage': 'home', 'loginpage': 'login',
                      'signuppage': 'signup', 'registerpage': 'register'}

    SECTION_HINTS_RE = re.compile(
        r'\b(hero|header|nav|footer|card|grid|table|form|list|sidebar|modal|'
        r'drawer|banner|section|panel|dashboard|stats|chart|profile|detail|'
        r'search|filter|gallery|carousel)\b',
        re.IGNORECASE,
    )

    def infer(self, texts):
        lines = []
        for t in texts:
            lines.extend(t.splitlines())

        seen = {}

        for i, line in enumerate(lines):
            if self.BACKEND_RE.search(line):
                continue

            context_lines = lines[max(0, i-3):i+4]
            context = ' '.join(context_lines)
            sections = list(set(self.SECTION_HINTS_RE.findall(context)))

            # Framework paths
            for pat in [self.NUXT_PAGE, self.NEXT_PAGE, self.REACT_VIEW, self.SCREENS]:
                for m in pat.finditer(line):
                    slug = self._path_to_slug(m.group(1))
                    if slug and slug not in seen:
                        seen[slug] = {'name': self._slug_to_name(slug), 'slug': slug,
                                       'route': '/' + slug.replace('admin-', 'admin/'),
                                       'source': m.group(), 'detection': 'path',
                                       'section_hints': sections}

            # Compound single-word names
            for m in self.COMPOUND.finditer(line):
                slug = self.COMPOUND_SLUGS.get(m.group(1).lower(), 'home')
                if slug not in seen:
                    seen[slug] = {'name': slug.title(), 'slug': slug,
                                   'route': '/' + slug, 'source': m.group(0),
                                   'detection': 'semantic', 'section_hints': sections}

            # Semantic "Build the X Page"
            for m in self.SEMANTIC.finditer(line):
                name = m.group(1).strip()
                slug = self._name_to_slug(name)
                if slug and slug not in seen:
                    seen[slug] = {'name': name.title(), 'slug': slug,
                                   'route': '/' + slug.replace('admin-', 'admin/'),
                                   'source': m.group(0), 'detection': 'semantic',
                                   'section_hints': sections}

        pages = list(seen.values())
        return {'pages': pages, 'total': len(pages)}

    def _path_to_slug(self, path):
        s = re.sub(r'\[(slug|id|.*?)\]', 'detail', path)
        s = s.replace('/index', '').replace('/', '-').strip('-').lower()
        return s or 'page'

    def _name_to_slug(self, name):
        s = name.lower().strip()
        s = re.sub(r'\s+(?:page|screen|view|interface|dashboard)s?$', '', s).strip()
        if s in ('home', 'landing', 'main', 'index', 'homepage', 'home page'):
            return 'home'
        if 'listing' in s:
            s = re.sub(r'\s+listing$', '', s).strip()
        s = re.sub(r'[\s_]+', '-', s)
        s = re.sub(r'[^a-z0-9\-]', '', s)
        return s.strip('-') or 'page'

    def _slug_to_name(self, slug):
        return slug.replace('-', ' ').title()


# ══════════════════════════════════════════════════════════════════════════════
# CLASS 6 — SpecKitArtifactInferrer
# ══════════════════════════════════════════════════════════════════════════════

class SpecKitArtifactInferrer:

    PHASE_RE   = re.compile(r'^##\s+Phase\s+(\S+)', re.MULTILINE)
    US_RE      = re.compile(r'User Story\s+\d+|US\d+')
    TASK_RE    = re.compile(r'^- \[[ xX]\]\s+(T\d+.*)', re.MULTILINE)
    NAME_RE    = re.compile(r'^#\s+(.+)$', re.MULTILINE)
    TECH_KEYS  = ['Nuxt', 'Vue', 'React', 'Next', 'Astro', 'SvelteKit',
                  'Express', 'FastAPI', 'Django', 'Tailwind', 'TypeScript',
                  'Prisma', 'PostgreSQL', 'MongoDB', 'Redis', 'GraphQL']

    def infer(self, root):
        root = Path(root)
        plan_path  = self._find(root, 'plan.md')
        tasks_path = self._find(root, 'tasks.md')
        spec_path  = self._find(root, 'spec.md')

        result = {
            'plan_path':  str(plan_path)  if plan_path  else None,
            'tasks_path': str(tasks_path) if tasks_path else None,
            'spec_path':  str(spec_path)  if spec_path  else None,
            'project_name': 'Unknown',
            'phases': [],
            'user_stories': [],
            'tech_stack': [],
        }

        if plan_path:
            content = plan_path.read_text(encoding='utf-8', errors='ignore')
            m = self.NAME_RE.search(content)
            if m:
                result['project_name'] = m.group(1).strip()
            result['phases'] = self.PHASE_RE.findall(content)
            result['user_stories'] = list(dict.fromkeys(self.US_RE.findall(content)))
            result['tech_stack'] = [k for k in self.TECH_KEYS if k.lower() in content.lower()]

        if tasks_path:
            content = tasks_path.read_text(encoding='utf-8', errors='ignore')
            tasks = self.TASK_RE.findall(content)
            result['total_tasks'] = len(tasks)
            result['parallel_tasks'] = sum(1 for t in tasks if '[P]' in t)

        return result

    def _find(self, root, filename):
        try:
            return SpecKitResolver(root).find(filename)
        except RuntimeError:
            return None


# ══════════════════════════════════════════════════════════════════════════════
# CLASS 7 — PresetResolver
# ══════════════════════════════════════════════════════════════════════════════

class PresetResolver:
    """Resolve only explicit, project-owned brand tokens.

    This class used to contain category presets. That was dangerous because any
    caller could accidentally recreate default EdTech/SaaS colors and fonts.
    It now fails unless explicit high-confidence project signals are present.
    """

    def resolve(self, category, color_signals, font_signals):
        resolved = {
            "category": category,
            "source": "explicit_project_signals",
            "register": "unapproved",
        }

        high_colors = [c for c in color_signals.get('colors', [])
                       if c['confidence'] == 'high' and c['role'] == 'primary']
        if not high_colors:
            raise RuntimeError("No explicit primary color signal found. Approve brand direction instead of using presets.")
        resolved['primary'] = high_colors[0]['value']

        high_fonts = [f for f in font_signals.get('fonts', [])
                      if f['confidence'] == 'high']
        if not high_fonts:
            raise RuntimeError("No explicit font signal found. Approve brand direction instead of using presets.")
        for fnt in high_fonts:
            if fnt['role'] == 'heading':
                resolved['heading_font'] = fnt['name']
            elif fnt['role'] == 'body':
                resolved['body_font'] = fnt['name']

        if 'heading_font' not in resolved or 'body_font' not in resolved:
            raise RuntimeError("Explicit heading/body fonts are incomplete. Approve brand direction instead of using presets.")
        return resolved


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def collect_file_contents(root, extensions, max_files=50, max_size_kb=100):
    root = Path(root)
    parts = []
    count = 0
    for fpath in iter_real_source_files(root, extensions):
        if count >= max_files:
            break
        if fpath.suffix.lower() in SKIP_EXTENSIONS:
            continue
        try:
            size_kb = fpath.stat().st_size / 1024
            if size_kb > max_size_kb:
                continue
            text = fpath.read_text(encoding='utf-8', errors='ignore')
            parts.append('/* FILE: %s */\n%s' % (fpath.relative_to(root), text))
            count += 1
        except Exception:
            pass
    return '\n\n'.join(parts)


def collect_text_lines(root):
    root = Path(root)
    lines = []

    def _add(path):
        if path and path.exists():
            lines.extend(path.read_text(encoding='utf-8', errors='ignore').splitlines())

    # plan.md and tasks.md (search)
    ski = SpecKitArtifactInferrer()
    result = ski.infer(root)
    if result['plan_path']:
        _add(Path(result['plan_path']))
    if result['tasks_path']:
        _add(Path(result['tasks_path']))

    _add(root / 'README.md')
    _add(root / 'package.json')

    return lines


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CLI
# ══════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='UI Bridge inference engine')
    parser.add_argument('--root', default='.', help='Project root directory')
    parser.add_argument('--infer',
                        choices=['project_type', 'language', 'colors', 'fonts',
                                 'pages', 'speckit', 'explicit_tokens', 'all'],
                        default='all')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    results = {}

    text_lines   = collect_text_lines(root)
    file_content = collect_file_contents(
        root, {'.css', '.scss', '.vue', '.jsx', '.tsx', '.html', '.ts', '.js'})

    if args.infer in ('project_type', 'all'):
        r = ProjectTypeInferrer().infer(text_lines)
        results['project_type'] = r
        if not args.quiet:
            print('Project type: %s (%s confidence, %d signals)' % (
                r['category'], r['confidence'], r['signals_found']), file=sys.stderr)

    if args.infer in ('language', 'all'):
        r = LanguageInferrer().infer(text_lines)
        results['language'] = r
        if not args.quiet:
            print('Language: %s (RTL=%s)' % (r['primary_language'], r['is_rtl']),
                  file=sys.stderr)

    if args.infer in ('colors', 'all'):
        r = BrandColorInferrer().infer(file_content)
        results['colors'] = r
        if not args.quiet:
            print('Colors: %d signals found' % len(r['colors']), file=sys.stderr)

    if args.infer in ('fonts', 'all'):
        r = FontInferrer().infer(file_content)
        results['fonts'] = r
        if not args.quiet:
            print('Fonts: %d signals found' % len(r['fonts']), file=sys.stderr)

    if args.infer in ('pages', 'all'):
        r = PageInventoryInferrer().infer(text_lines)
        results['pages'] = r
        if not args.quiet:
            print('Pages: %d discovered' % r['total'], file=sys.stderr)
            for p in r['pages']:
                print('  [%s] %s' % (p['detection'], p['slug']), file=sys.stderr)

    if args.infer in ('speckit', 'all'):
        r = SpecKitArtifactInferrer().infer(root)
        results['speckit'] = r
        if not args.quiet:
            print('Spec Kit: plan=%s, tasks=%s, phases=%d' % (
                r['plan_path'], r['tasks_path'], len(r['phases'])), file=sys.stderr)

    if args.infer in ('explicit_tokens',):
        cat = results.get('project_type', {}).get('category', 'Generic Professional')
        col = results.get('colors', {'colors': []})
        fnt = results.get('fonts', {'fonts': []})
        r = PresetResolver().resolve(cat, col, fnt)
        results['explicit_tokens'] = r
        if not args.quiet:
            print('Explicit tokens: primary=%s, font=%s, register=%s' % (
                r['primary'], r['heading_font'], r['register']), file=sys.stderr)

    out_dir = root / '.ui-bridge'
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / 'infer-results.json'
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    if not args.quiet:
        print('Saved: %s' % out_path, file=sys.stderr)

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
