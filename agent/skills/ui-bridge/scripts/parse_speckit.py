"""
parse_speckit.py — Locate and parse Spec Kit artifacts (plan.md, tasks.md, spec.md).

Usage:
    python scripts/parse_speckit.py [--json] [--root PATH]

Saves output to .ui-bridge/parsed-speckit.json
Prints JSON to stdout (if --json), progress to stderr.

Page detection is framework-agnostic — works with Vue, React, Astro, Next.js,
plain HTML, or any project where task descriptions name the pages to build.
"""
import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import date

from ui_bridge_core import SpecKitResolver, parse_phase_headings


# ── Constants ─────────────────────────────────────────────────────────────────

SKIP_DIRS = frozenset([
    '.git', 'node_modules', '.nuxt', 'dist', '__pycache__', '.ui-bridge',
    '.output', 'coverage', 'ui-prototypes',
])

# Any task line matching these keywords is a backend/logic task — skip for page detection
BACKEND_RE = re.compile(
    r'\b(service|services|controller|middleware|route(?:r|s)?|endpoint|migration|'
    r'model|repository|handler|database|schema|redis|email|smtp|cron|webhook|'
    r'job|queue|seed|fixture|jwt|token|session|resolver|dto|validator|'
    r'api/|/api|\.spec\.|\.test\.)\b',
    re.IGNORECASE,
)

# Framework file path patterns — any frontend framework
FRAMEWORK_PAGE_PATTERNS = [
    re.compile(r'pages/[^\s`\'"]+\.(?:vue|tsx|jsx|astro|svelte|html)'),
    re.compile(r'src/views/[^\s`\'"]+\.(?:vue|tsx|jsx)'),
    re.compile(r'src/pages/[^\s`\'"]+\.(?:tsx|jsx|astro)'),
    re.compile(r'app/[^\s`\'"]+/page\.(?:tsx|jsx)'),
    re.compile(r'screens/[^\s`\'"]+\.(?:tsx|jsx|vue)'),
]

# Semantic: "Build the X Page" / "Create the X Screen" / "Design the X View"
SEMANTIC_PAGE_RE = re.compile(
    r'(?:build|create|design|implement|develop|add)\s+'
    r'(?:the\s+)?'
    r'([A-Za-z][A-Za-z0-9 \-]{2,40}?)\s+'
    r'(?:page|screen|view|interface|dashboard)\b',
    re.IGNORECASE,
)


# ── Slug helpers ──────────────────────────────────────────────────────────────

def slug_from_path(path: str) -> str:
    """pages/courses/[slug].vue → courses-detail"""
    s = path
    for prefix in ['pages/', 'apps/web/pages/', 'src/views/', 'src/pages/', 'screens/']:
        s = s.replace(prefix, '')
    s = re.sub(r'\.(vue|tsx|jsx|astro|svelte|html)$', '', s)
    s = s.replace('/index', '')
    s = re.sub(r'\[(slug|id|.*?)\]', 'detail', s)
    s = s.replace('/', '-').strip('-').lower()
    return s or 'page'


def slug_from_name(name: str) -> str:
    """'Courses Listing Page' → 'courses', 'Homepage' → 'home'"""
    s = name.lower().strip()
    s = re.sub(r'\s+(?:page|screen|view|interface|dashboard)s?$', '', s).strip()
    if s in ('home', 'landing', 'main', 'index', 'homepage', 'home page'):
        return 'home'
    if 'listing' in s:
        s = re.sub(r'\s+listing$', '', s).strip()
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'[^a-z0-9\-]', '', s)
    return s.strip('-') or 'page'


def slug_to_name(slug: str) -> str:
    return slug.replace('-', ' ').title()


# ── Discovery ─────────────────────────────────────────────────────────────────

def find_feature_json(root: Path):
    fj = root / '.specify' / 'feature.json'
    if fj.exists():
        try:
            return json.loads(fj.read_text(encoding='utf-8'))['feature_directory']
        except Exception:
            pass
    return None


def search_for_file(filename: str, root: Path, max_depth: int = 4) -> Path | None:
    try:
        return SpecKitResolver(root).find(filename)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


# ── Parsers ───────────────────────────────────────────────────────────────────

def parse_plan(plan_path: Path) -> dict:
    content = plan_path.read_text(encoding='utf-8')

    name_m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    project_name = name_m.group(1).strip() if name_m else 'Unknown Project'

    phases = parse_phase_headings(content)
    if re.search(r'^#{2,3}\s+Phase\s+', content, re.MULTILINE | re.IGNORECASE) and not phases:
        raise ValueError(f"plan.md contains phase headings but parser returned no phases: {plan_path}")
    user_stories = list(dict.fromkeys(re.findall(r'US\d+[^):\n]*', content)))

    tech_keywords = ['Nuxt', 'Vue', 'React', 'Next', 'Astro', 'SvelteKit', 'Express',
                     'FastAPI', 'Django', 'Tailwind', 'TypeScript', 'Prisma',
                     'PostgreSQL', 'MongoDB', 'Redis']
    tech_stack = [kw for kw in tech_keywords if kw.lower() in content.lower()]

    rtl = bool(re.search(r'rtl|arabic|عربي|dir=["\']rtl["\']', content, re.IGNORECASE))

    project_type = 'general'
    type_map = {
        'edtech':     ['course', 'training', 'learning', 'lms', 'edtech', 'education'],
        'ecommerce':  ['shop', 'cart', 'product', 'checkout', 'inventory'],
        'saas':       ['dashboard', 'analytics', 'saas', 'b2b', 'metrics'],
        'marketing':  ['marketing', 'crm', 'leads', 'registration', 'landing'],
        'healthcare': ['clinic', 'patient', 'health', 'medical', 'hospital'],
        'finance':    ['bank', 'payment', 'finance', 'fintech', 'investment'],
    }
    cl = content.lower()
    for ptype, kws in type_map.items():
        if any(kw in cl for kw in kws):
            project_type = ptype
            break

    return {
        'project_name': project_name,
        'project_type': project_type,
        'phases':       phases,
        'user_stories': user_stories,
        'tech_stack':   tech_stack,
        'direction':    'rtl' if rtl else 'ltr',
        'language':     'arabic' if rtl else 'english',
        'path':         str(plan_path),
    }


def parse_tasks(tasks_path: Path) -> dict:
    content = tasks_path.read_text(encoding='utf-8')

    task_lines = re.findall(r'^- \[[ x]\]\s+T\d+.*$', content, re.MULTILINE)

    # Group tasks by phase
    phases = {}
    current_phase = 'unknown'
    for line in content.splitlines():
        pm = re.match(r'^#{2,3}\s+(Phase\s+[0-9A-Za-z]+)(?:\s*[:\-\u2014].*)?$', line, re.IGNORECASE)
        if pm:
            current_phase = pm.group(1)
            phases[current_phase] = []
        tm = re.match(r'^- \[[ x]\]\s+(T\d+.*)', line)
        if tm:
            phases.setdefault(current_phase, []).append(tm.group(1))

    # Page detection — framework-agnostic
    seen_slugs = {}   # slug → {"slug", "name", "source", "detection"}

    for line in content.splitlines():
        if not re.match(r'^- \[[ x]\]\s+T\d+', line):
            continue

        # Method A: framework file paths (any frontend framework)
        found_path = False
        for pattern in FRAMEWORK_PAGE_PATTERNS:
            for m in pattern.finditer(line):
                path = m.group()
                slug = slug_from_path(path)
                if slug and slug not in seen_slugs:
                    seen_slugs[slug] = {
                        'slug':      slug,
                        'name':      slug_to_name(slug),
                        'source':    path,
                        'detection': 'path',
                    }
                found_path = True

        # Method B: semantic page names (skip if backend task OR path already found)
        if not found_path and not BACKEND_RE.search(line):
            for m in SEMANTIC_PAGE_RE.finditer(line):
                name = m.group(1).strip()
                slug = slug_from_name(name)
                if slug and slug not in seen_slugs:
                    seen_slugs[slug] = {
                        'slug':      slug,
                        'name':      name.title(),
                        'source':    f'semantic: "{m.group(0).strip()}"',
                        'detection': 'semantic',
                    }

    # Normalize output — always a list of slug strings (backward compat for generate_page_map.py)
    # Also return structured list for detection layers
    page_slugs      = list(seen_slugs.keys())
    page_structured = list(seen_slugs.values())

    # Components (from framework paths, best-effort)
    component_patterns = [
        re.compile(r'components/[^\s`\'"]+\.(?:vue|tsx|jsx)'),
    ]
    components = set()
    for pat in component_patterns:
        components.update(pat.findall(content))

    us_labels = list(dict.fromkeys(re.findall(r'\[US\d+\]', content)))

    return {
        'total_tasks':       len(task_lines),
        'phases':            {k: len(v) for k, v in phases.items()},
        'pages':             page_slugs,         # list of slug strings (for generate_page_map.py)
        'pages_structured':  page_structured,    # list of {slug, name, source, detection}
        'components':        sorted(components),
        'user_story_labels': us_labels,
        'path':              str(tasks_path),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Parse Spec Kit artifacts')
    parser.add_argument('--json', action='store_true', help='Output JSON to stdout')
    parser.add_argument('--root', default='.', help='Project root path')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    print(f'Searching for Spec Kit artifacts in: {root}', file=sys.stderr)

    plan_path  = search_for_file('plan.md',  root)
    tasks_path = search_for_file('tasks.md', root)
    spec_path  = search_for_file('spec.md',  root)

    print(f'  plan.md:  {plan_path  or "NOT FOUND"}', file=sys.stderr)
    print(f'  tasks.md: {tasks_path or "NOT FOUND"}', file=sys.stderr)
    print(f'  spec.md:  {spec_path  or "NOT FOUND"}', file=sys.stderr)

    if not plan_path and not tasks_path:
        print('ERROR: No Spec Kit artifacts found.', file=sys.stderr)
        print('Run /speckit-plan and /speckit-tasks first, then re-run /ui-plan.', file=sys.stderr)
        sys.exit(1)

    result = {
        'generated': date.today().isoformat(),
        'found': {
            'plan':  str(plan_path)  if plan_path  else None,
            'tasks': str(tasks_path) if tasks_path else None,
            'spec':  str(spec_path)  if spec_path  else None,
        },
        'plan':  parse_plan(plan_path)   if plan_path  else {},
        'tasks': parse_tasks(tasks_path) if tasks_path else {},
    }

    # Save to .ui-bridge/
    ui_bridge = root / '.ui-bridge'
    ui_bridge.mkdir(exist_ok=True)
    out = ui_bridge / 'parsed-speckit.json'
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'Saved to: {out}', file=sys.stderr)

    pages = result['tasks'].get('pages_structured', [])
    print(f'Pages found: {len(pages)}', file=sys.stderr)
    for p in pages:
        print(f'  [{p["detection"]}] {p["slug"]}.html  ←  {p["source"]}', file=sys.stderr)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
