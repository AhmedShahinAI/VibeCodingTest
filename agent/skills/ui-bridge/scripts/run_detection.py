"""
run_detection.py — Run all 7 UI Bridge detection layers.

Usage:
    python scripts/run_detection.py --command ui-plan [--root PATH]

Saves:  .ui-bridge/detection-report.json
Prints: detection summary box to stdout
Exit:   0 if can_proceed, 1 if blocking layer failed
"""
import sys
import re
import json
import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime

from ui_bridge_core import ApprovalStore, SpecKitResolver, iter_real_source_files, read_json
from extract_brand import scan_project, has_explicit_brand


# ── Constants ─────────────────────────────────────────────────────────────────

SKIP_DIRS = frozenset([
    '.git', 'node_modules', '.nuxt', 'dist', '.output', '__pycache__',
    'ui-prototypes', '.specify', 'coverage', '.ui-bridge',
])

SCAN_EXTENSIONS = frozenset([
    '.css', '.scss', '.sass', '.vue', '.tsx', '.jsx', '.ts', '.js', '.html', '.md',
])

BACKEND_RE = re.compile(
    r'\b(service|services|controller|middleware|route(?:r|s)?|endpoint|migration|'
    r'model|repository|handler|database|schema|redis|email|smtp|cron|webhook|'
    r'job|queue|seed|fixture|jwt|token|session|resolver|dto|validator|spec\.ts|'
    r'\.test\.|\.spec\.)\b',
    re.IGNORECASE,
)

FRAMEWORK_PAGE_PATTERNS = [
    re.compile(r'pages/[^\s`\'"]+\.(?:vue|tsx|jsx|astro|svelte|html)'),
    re.compile(r'src/views/[^\s`\'"]+\.(?:vue|tsx|jsx)'),
    re.compile(r'src/pages/[^\s`\'"]+\.(?:tsx|jsx|astro)'),
    re.compile(r'app/[^\s`\'"]+/page\.(?:tsx|jsx)'),
    re.compile(r'screens/[^\s`\'"]+\.(?:tsx|jsx|vue)'),
]

SEMANTIC_PAGE_RE = re.compile(
    r'(?:build|create|design|implement|develop|add)\s+'
    r'(?:the\s+)?'
    r'([A-Za-z][A-Za-z0-9 \-]{2,40}?)\s+'
    r'(?:page|screen|view|interface|dashboard)\b',
    re.IGNORECASE,
)

# Compound single-word page names that SEMANTIC_PAGE_RE cannot match (no space before "page")
COMPOUND_PAGE_RE = re.compile(
    r'(?:build|create|design|implement|develop|add)\s+(?:the\s+)?'
    r'(homepage|loginpage|signuppage|registerpage)',
    re.IGNORECASE,
)

COMPOUND_PAGE_SLUGS = {
    'homepage': 'home',
    'loginpage': 'login',
    'signuppage': 'signup',
    'registerpage': 'register',
}

CATEGORY_KEYWORDS = {
    'EdTech':             ['course', 'training', 'learn', 'lms', 'edtech', 'education', 'instructor', 'student'],
    'E-commerce':         ['shop', 'cart', 'product', 'checkout', 'inventory', 'order', 'purchase'],
    'SaaS Dashboard':     ['dashboard', 'analytics', 'saas', 'b2b', 'metrics', 'workspace', 'subscription'],
    'Booking Platform':   ['booking', 'appointment', 'reservation', 'schedule', 'calendar'],
    'Healthcare':         ['clinic', 'doctor', 'health', 'medical', 'hospital', 'patient'],
    'Fintech':            ['invest', 'finance', 'payment', 'fintech', 'bank', 'portfolio', 'transaction'],
    'Travel/Hospitality': ['hotel', 'travel', 'tour', 'flight', 'accommodation', 'destination'],
    'Food & Beverage':    ['restaurant', 'menu', 'food', 'delivery', 'recipe', 'meal'],
    'Real Estate':        ['real estate', 'property', 'rent', 'mortgage', 'listing', 'apartment'],
    'Creative Agency':    ['agency', 'portfolio', 'creative', 'studio', 'branding', 'design firm'],
    'Marketing/CRM':      ['marketing', 'crm', 'leads', 'registrations', 'landing', 'campaigns', 'contacts'],
}

SECTION_ESTIMATES = {
    'home':                    6,
    'courses':                 5,
    'course-detail':           6,
    'experts':                 4,
    'expert-detail':           7,
    'experts-detail':          7,
    'admin-dashboard':         5,
    'admin-login':             3,
    'admin-registrations':     5,
    'admin-courses':           4,
    'admin-courses-detail':    5,
    'admin-experts':           4,
    'admin-experts-detail':    6,
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def find_file(name, root):
    try:
        return SpecKitResolver(root).find(name)
    except RuntimeError as exc:
        raise SystemExit('ERROR: %s' % exc)


def page_to_slug(path_or_name: str) -> str:
    s = path_or_name
    # Strip framework prefixes
    for prefix in ['pages/', 'apps/web/pages/', 'src/views/', 'src/pages/', 'screens/']:
        s = s.replace(prefix, '')
    s = re.sub(r'\.(vue|tsx|jsx|astro|svelte|html)$', '', s)
    s = s.replace('/index', '').replace('/', '-')
    s = re.sub(r'\[(slug|id|.*?)\]', 'detail', s)
    s = s.strip('-').lower()
    return s or 'page'


def slug_from_name(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r'\s+(?:page|screen|view|interface|dashboard)s?$', '', s).strip()
    if s in ('home', 'landing', 'main', 'index', 'homepage'):
        return 'home'
    if 'listing' in s:
        s = re.sub(r'\s+listing$', '', s).strip()
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'[^a-z0-9\-]', '', s)
    return s.strip('-') or 'page'


def scan_dir(root: Path):
    for path in root.rglob('*'):
        if not path.is_file():
            continue
        if any(s in path.parts for s in SKIP_DIRS):
            continue
        if path.suffix.lower() not in SCAN_EXTENSIONS:
            continue
        yield path


# ── Layer 1 ───────────────────────────────────────────────────────────────────

def layer_1(root: Path) -> dict:
    plan_path  = find_file('plan.md',  root)
    tasks_path = find_file('tasks.md', root)
    const_path = root / '.specify' / 'memory' / 'constitution.md'

    status = 'ok'
    phases_found = 0
    tasks_found  = 0

    if plan_path:
        content = plan_path.read_text(encoding='utf-8', errors='ignore')
        phases_found = len(re.findall(r'^##\s+Phase', content, re.MULTILINE))
        if phases_found == 0:
            status = 'empty'
    else:
        status = 'missing_plan'

    if tasks_path:
        content = tasks_path.read_text(encoding='utf-8', errors='ignore')
        tasks_found = len(re.findall(r'^- \[[ x]\]\s+T\d+', content, re.MULTILINE))
        if tasks_found == 0 and status == 'ok':
            status = 'empty'
    else:
        status = 'missing_tasks'

    return {
        'plan_path':        str(plan_path)  if plan_path  else None,
        'tasks_path':       str(tasks_path) if tasks_path else None,
        'phases_found':     phases_found,
        'tasks_found':      tasks_found,
        'has_constitution': const_path.exists(),
        'status':           status,
    }


# ── Layer 2 ───────────────────────────────────────────────────────────────────

def layer_2(root: Path, l1: dict) -> dict:
    framework = 'Unknown'
    # Check package.json
    pkg = root / 'package.json'
    if not pkg.exists():
        for apps_dir in ['apps/web', 'apps/frontend', 'frontend', 'web']:
            p = root / apps_dir / 'package.json'
            if p.exists():
                pkg = p
                break

    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
            deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
            if 'nuxt' in deps:
                framework = 'Nuxt 3'
            elif 'next' in deps:
                framework = 'Next.js'
            elif 'astro' in deps:
                framework = 'Astro'
            elif '@sveltejs/kit' in deps:
                framework = 'SvelteKit'
            elif 'react' in deps:
                framework = 'React'
            elif 'vue' in deps:
                framework = 'Vue'
        except Exception:
            pass

    # Detect project category from plan.md content
    plan_content = ''
    if l1.get('plan_path'):
        plan_content = Path(l1['plan_path']).read_text(encoding='utf-8', errors='ignore').lower()
    tasks_content = ''
    if l1.get('tasks_path'):
        tasks_content = Path(l1['tasks_path']).read_text(encoding='utf-8', errors='ignore').lower()

    combined = plan_content + ' ' + tasks_content

    category = 'Generic Professional'
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            category = cat
            break

    # Arabic / RTL detection
    is_arabic = bool(re.search(r'[؀-ۿ]|arabic|عربي|rtl|dir=["\']rtl["\']', combined, re.IGNORECASE))
    is_rtl    = bool(re.search(r'rtl|dir=["\']rtl["\']', combined, re.IGNORECASE)) or is_arabic

    has_admin = bool(re.search(r'admin|dashboard|cms|manage|backoffice', combined))
    has_auth  = bool(re.search(r'login|auth|jwt|session|sign.?in|register|password', combined))

    return {
        'framework':     framework,
        'project_category': category,
        'is_arabic':     is_arabic,
        'is_rtl':        is_rtl,
        'has_admin_panel': has_admin,
        'has_auth':      has_auth,
        'status':        'ok',
    }


# ── Layer 3 ───────────────────────────────────────────────────────────────────

def layer_3(root: Path, l2: dict) -> dict:
    signals = scan_project(root)
    approvals = ApprovalStore(root)
    approved = approvals.is_approved('brand_direction')
    primary = None
    font_heading = None
    logo_path = signals.get('logos', [{}])[0].get('path') if signals.get('logos') else None
    confidence = 'approved' if approved else ('explicit' if has_explicit_brand(signals) else 'missing')
    for cv in signals.get('css_variables', []):
        if 'primary' in cv.get('variable', '').lower():
            hx = re.search(r'#[0-9A-Fa-f]{3,6}', cv['variable'])
            if hx:
                primary = hx.group().upper()
                break
    if not primary and signals.get('tailwind_colors', {}).get('primary'):
        primary = signals['tailwind_colors']['primary']
    if signals.get('font_families'):
        font_heading = signals['font_families'][0]['font']
    return {
        'state':           'approved_brand' if approved else ('brand_intake_required' if confidence == 'missing' else 'approval_required'),
        'primary_color':   {'value': primary,      'confidence': confidence},
        'accent_color':    {'value': None, 'confidence': 'not_selected'},
        'heading_font':    {'value': font_heading,  'confidence': confidence if font_heading else 'missing'},
        'body_font':       {'value': font_heading,  'confidence': confidence if font_heading else 'missing'},
        'logo_path':       logo_path,
        'brand_signals_count': (len(signals.get('hex_colors', [])) + len(signals.get('font_families', [])) + len(signals.get('logos', []))),
        'approved': approved,
    }


# ── Layer 4 ───────────────────────────────────────────────────────────────────

def layer_4(root: Path, l1: dict) -> dict:
    if not l1.get('tasks_path'):
        return {'pages': [], 'total_pages': 0, 'public_count': 0, 'admin_count': 0}

    parsed = read_json(root / '.ui-bridge' / 'parsed-speckit.json', default={}) or {}
    parsed_pages = parsed.get('tasks', {}).get('pages_structured') or []
    if parsed_pages:
        pages = []
        for page in parsed_pages:
            slug = page.get('slug') or slug_from_name(page.get('name', 'page'))
            pages.append({
                'name': page.get('name') or slug.replace('-', ' ').title(),
                'slug': slug,
                'route': '/' + slug.replace('index', '').replace('admin-', 'admin/').replace('-detail', '/detail').strip('/'),
                'is_admin': slug.startswith('admin'),
                'source_tasks': [page.get('source') or '?'],
                'detection_method': page.get('detection') or 'parsed-speckit',
                'estimated_sections': SECTION_ESTIMATES.get(slug, 4),
            })
        public_cnt = sum(1 for p in pages if not p['is_admin'])
        admin_cnt = sum(1 for p in pages if p['is_admin'])
        return {
            'pages': pages,
            'total_pages': len(pages),
            'public_count': public_cnt,
            'admin_count': admin_cnt,
            'source': 'parsed-speckit',
        }

    tasks_content = Path(l1['tasks_path']).read_text(encoding='utf-8', errors='ignore')
    plan_content  = Path(l1['plan_path']).read_text(encoding='utf-8', errors='ignore') if l1.get('plan_path') else ''

    seen_slugs = {}   # slug → entry
    task_lines = re.findall(r'^- \[[ x]\]\s+(T\d+.*)$', tasks_content, re.MULTILINE)

    for line in task_lines:
        # Skip backend-only tasks
        if BACKEND_RE.search(line):
            continue

        # Method A: framework path patterns
        for pattern in FRAMEWORK_PAGE_PATTERNS:
            for m in pattern.finditer(line):
                path = m.group()
                slug = page_to_slug(path)
                if slug and slug not in seen_slugs:
                    task_id = re.match(r'T\d+', line)
                    seen_slugs[slug] = {
                        'name':             slug.replace('-', ' ').title(),
                        'slug':             slug,
                        'route':            '/' + slug.replace('admin-', 'admin/').replace('-detail', '/detail'),
                        'is_admin':         slug.startswith('admin'),
                        'source_tasks':     [task_id.group() if task_id else '?'],
                        'detection_method': 'path',
                        'estimated_sections': SECTION_ESTIMATES.get(slug, 4),
                    }

        # Method B: semantic patterns (only if no path found in this line)
        if not any(pat.search(line) for pat in FRAMEWORK_PAGE_PATTERNS):
            task_id = re.match(r'T\d+', line)
            tid = task_id.group() if task_id else '?'

            # Method B1: compound single-word forms (e.g. "Homepage")
            for m in COMPOUND_PAGE_RE.finditer(line):
                slug = COMPOUND_PAGE_SLUGS.get(m.group(1).lower(), 'home')
                if slug not in seen_slugs:
                    seen_slugs[slug] = {
                        'name':               slug.title(),
                        'slug':               slug,
                        'route':              '/' + slug,
                        'is_admin':           False,
                        'source_tasks':       [tid],
                        'detection_method':   'semantic',
                        'estimated_sections': SECTION_ESTIMATES.get(slug, 4),
                    }

            # Method B2: regular semantic "Build the X Page" patterns
            for m in SEMANTIC_PAGE_RE.finditer(line):
                name = m.group(1).strip()
                slug = slug_from_name(name)
                if slug and slug not in seen_slugs:
                    seen_slugs[slug] = {
                        'name':             name.title(),
                        'slug':             slug,
                        'route':            '/' + slug.replace('admin-', 'admin/'),
                        'is_admin':         'admin' in slug,
                        'source_tasks':     [tid],
                        'detection_method': 'semantic',
                        'estimated_sections': SECTION_ESTIMATES.get(slug, 4),
                    }

    pages       = list(seen_slugs.values())
    public_cnt  = sum(1 for p in pages if not p['is_admin'])
    admin_cnt   = sum(1 for p in pages if p['is_admin'])

    return {
        'pages':        pages,
        'total_pages':  len(pages),
        'public_count': public_cnt,
        'admin_count':  admin_cnt,
        'source':       'legacy-detection',
    }


# ── Layer 5 ───────────────────────────────────────────────────────────────────

def layer_5(root: Path) -> dict:
    global_impeccable = Path.home() / '.claude' / 'skills' / 'impeccable'
    local_impeccable  = root / '.claude' / 'skills' / 'impeccable'

    impeccable_installed = global_impeccable.is_dir() or local_impeccable.is_dir()

    product_md = (root / 'PRODUCT.md').exists() or (root / '.ui-bridge' / 'PRODUCT.md').exists()
    design_md  = (root / 'DESIGN.md').exists()  or (root / '.ui-bridge' / 'DESIGN.md').exists()

    npx_available = shutil.which('npx') is not None

    return {
        'impeccable_installed': impeccable_installed,
        'product_md_exists':    product_md,
        'design_md_exists':     design_md,
        'npx_available':        npx_available,
        'install_needed':       not impeccable_installed and npx_available,
    }


# ── Layer 6 ───────────────────────────────────────────────────────────────────

def layer_6(root: Path, l1: dict) -> dict:
    ui_bridge   = root / '.ui-bridge'
    proto_dir   = root / 'ui-prototypes'

    prev_run    = (ui_bridge / 'detection-report.json').exists()
    page_map    = (ui_bridge / 'page-map.json').exists()
    protos_exist = proto_dir.is_dir()

    proto_count = 0
    if protos_exist:
        proto_count = len([f for f in proto_dir.glob('*.html') if f.stem != 'index'])

    phase_0_added = False
    if l1.get('plan_path'):
        content = Path(l1['plan_path']).read_text(encoding='utf-8', errors='ignore')
        phase_0_added = bool(re.search(r'^##\s+Phase\s+0', content, re.MULTILINE))

    resuming = prev_run or proto_count > 0

    return {
        'previous_run_exists':  prev_run,
        'page_map_exists':      page_map,
        'prototypes_exist':     protos_exist,
        'prototypes_count':     proto_count,
        'phase_0_already_added': phase_0_added,
        'resuming':             resuming,
    }


# ── Layer 7 ───────────────────────────────────────────────────────────────────

def layer_7(root: Path, l6: dict) -> dict:
    proto_dir = root / 'ui-prototypes'
    if not l6.get('prototypes_exist') or l6.get('prototypes_count', 0) == 0:
        return {
            'locked_primary_color':  None,
            'locked_font_family':    None,
            'locked_border_radius':  None,
            'locked_nav_html':       None,
            'consistency_baseline_set': False,
        }

    # Read first non-index HTML file
    html_files = sorted([f for f in proto_dir.glob('*.html') if f.stem != 'index'])
    if not html_files:
        return {'locked_primary_color': None, 'locked_font_family': None,
                'locked_border_radius': None, 'locked_nav_html': None,
                'consistency_baseline_set': False}

    content = html_files[0].read_text(encoding='utf-8', errors='ignore')

    # Extract locked values
    primary_m  = re.search(r'--color-primary\s*:\s*(#[0-9A-Fa-f]{3,6})', content)
    font_m     = re.search(r'--font-(?:heading|body)\s*:\s*([^;}\n,]+)', content)
    radius_m   = re.search(r'--radius(?:-md)?\s*:\s*([^;}\n]+)', content)

    # Extract nav signature (simplified)
    nav_m      = re.search(r'<nav[^>]*>.*?</nav>', content, re.DOTALL | re.IGNORECASE)
    nav_sig    = nav_m.group()[:200] if nav_m else None

    return {
        'locked_primary_color':  primary_m.group(1) if primary_m else None,
        'locked_font_family':    font_m.group(1).strip().split(',')[0].strip() if font_m else None,
        'locked_border_radius':  radius_m.group(1).strip() if radius_m else None,
        'locked_nav_html':       nav_sig,
        'consistency_baseline_set': True,
    }


# ── Summary box ──────────────────────────────────────────────────────────────

def print_summary(command, l1, l2, l3, l4, l5, l6, l7, warnings):
    plan_name = 'Unknown'
    if l1.get('plan_path'):
        content = Path(l1['plan_path']).read_text(encoding='utf-8', errors='ignore')
        m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if m:
            plan_name = m.group(1).strip()[:30]

    category    = l2.get('project_category', 'Unknown')
    page_count  = l4.get('total_pages', 0)
    primary     = l3.get('primary_color', {}).get('value') or 'unapproved'
    font_value  = l3.get('heading_font',  {}).get('value') or 'unapproved'
    font        = str(font_value).split('/')[0].strip()
    confidence  = l3.get('primary_color', {}).get('confidence', 'inferred')
    is_arabic   = l2.get('is_arabic', False)
    resuming    = l6.get('resuming', False)
    proto_count = l6.get('prototypes_count', 0)
    impeccable  = 'Installed' if l5.get('impeccable_installed') else ('Will install' if l5.get('npx_available') else 'Not available')

    r_label = 'Yes (%d files exist)' % proto_count if resuming else 'No (fresh start)'

    w = 54
    def row(label, value):
        s = '| %-12s%s' % (label, value)
        return s + ' ' * max(0, w - len(s)) + '|'

    lines = [
        '+- UI Bridge -- Detection Complete ' + '-' * max(0, w - 35) + '+',
        row('Project:', '%s (%s)' % (plan_name, category)),
        row('Pages:', '%d pages found' % page_count),
        row('Brand:', '%s / %s (%s)' % (primary, font, confidence)),
        row('Arabic:', 'Yes' if is_arabic else 'No'),
        row('Resuming:', r_label),
        row('Impeccable:', impeccable),
        '+' + '-' * w + '+',
    ]
    print('\n'.join(lines))

    if warnings:
        for w_msg in warnings:
            print('  [!] %s' % w_msg)

    if l6.get('resuming') and proto_count > 0:
        print('  [~] Resuming from previous ui-bridge session (%d existing prototypes)' % proto_count)

    print('  Proceeding with /%s...\n' % command)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Run UI Bridge detection layers')
    parser.add_argument('--command', default='ui-plan',
                        choices=['ui-plan', 'ui-implement', 'ui-link'],
                        help='Which ui-bridge command is being run')
    parser.add_argument('--root', default='.', help='Project root path')
    parser.add_argument('--brand-policy', choices=['strict', 'proposal', 'fallback'], default='strict')
    parser.add_argument('--allow-unapproved-html', action='store_true')
    args = parser.parse_args()

    root    = Path(args.root).resolve()
    command = args.command

    print(f'Running UI Bridge detection for /{command}...', file=sys.stderr)

    # ── Run layers ────────────────────────────────────────────────────────────
    l1 = layer_1(root)
    print(f'  Layer 1 (artifacts): {l1["status"]}', file=sys.stderr)

    if l1['status'] in ('missing_plan', 'missing_tasks', 'empty'):
        print('\n✗ Layer 1 Failed — No Spec Kit artifacts found.', file=sys.stderr)
        print('  Run /speckit-plan and /speckit-tasks first, then retry.', file=sys.stderr)
        sys.exit(1)

    l2 = layer_2(root, l1)
    print(f'  Layer 2 (project):  {l2["project_category"]} | Arabic={l2["is_arabic"]}', file=sys.stderr)

    l3 = layer_3(root, l2)
    print(f'  Layer 3 (brand):    {l3["primary_color"]["value"]} ({l3["primary_color"]["confidence"]})', file=sys.stderr)

    l4 = layer_4(root, l1)
    print(f'  Layer 4 (pages):    {l4["total_pages"]} pages found', file=sys.stderr)
    for page in l4['pages']:
        print(f'    → [{page["detection_method"]}] {page["slug"]}.html', file=sys.stderr)

    l5 = layer_5(root)
    print(f'  Layer 5 (impeccable): installed={l5["impeccable_installed"]}', file=sys.stderr)

    l6 = layer_6(root, l1)
    print(f'  Layer 6 (state):    resuming={l6["resuming"]}, protos={l6["prototypes_count"]}', file=sys.stderr)

    l7 = layer_7(root, l6)
    print(f'  Layer 7 (consistency): baseline_set={l7["consistency_baseline_set"]}', file=sys.stderr)

    # ── Build warnings ───────────────────────────────────────────────────────
    warnings      = []
    decisions     = []

    if l4['total_pages'] == 0:
        warnings.append('No UI pages found — check tasks.md for page descriptions')
    if not l5['impeccable_installed'] and not l5['npx_available']:
        warnings.append('Impeccable not installed and npx unavailable — standalone mode')
    if l6['phase_0_already_added'] and command == 'ui-plan':
        warnings.append('Phase 0 already exists in plan.md — update_plan.py will replace stale UI Phase 0 when needed')
    if l7['consistency_baseline_set']:
        decisions.append(f'Existing prototype color baseline detected, not used as brand approval: {l7["locked_primary_color"]}')
        decisions.append(f'Existing prototype font baseline detected, not used as brand approval: {l7["locked_font_family"]}')

    if not l3.get('approved'):
        decisions.append('Brand not approved; strict mode blocks design and HTML generation')

    # ── Save report ──────────────────────────────────────────────────────────
    ui_bridge = root / '.ui-bridge'
    ui_bridge.mkdir(exist_ok=True)

    report = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'command':   command,
        'layer_1':   l1,
        'layer_2':   l2,
        'layer_3':   l3,
        'layer_4':   l4,
        'layer_5':   l5,
        'layer_6':   l6,
        'layer_7':   l7,
        'summary': {
            'can_proceed':    (args.brand_policy != 'strict' or l3.get('approved')),
            'warnings':       warnings,
            'decisions_made': decisions,
            'brand_policy':   args.brand_policy,
        },
    }

    report_path = ui_bridge / 'detection-report.json'
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'  Report saved: {report_path}', file=sys.stderr)

    # ── Print summary box ────────────────────────────────────────────────────
    print_summary(command, l1, l2, l3, l4, l5, l6, l7, warnings)

    if args.brand_policy == 'strict' and not l3.get('approved'):
        print('ERROR: strict brand policy requires approved brand before continuing.', file=sys.stderr)
        sys.exit(1)
    if args.brand_policy == 'fallback' and not args.allow_unapproved_html and command == 'ui-implement':
        print('ERROR: fallback HTML requires --allow-unapproved-html.', file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
