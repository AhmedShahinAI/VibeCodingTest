"""
Executable $ui-implement workflow wrapper.

This wrapper enforces a Phase 0-first, page-by-page UI flow. It prepares shared
prototype infrastructure, advances selected pages through the HTML stages in the
Phase 0 order, and publishes only reviewed pages.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from ui_bridge_core import ensure_bridge, read_json


SCRIPT_DIR = Path(__file__).resolve().parent
STAGES = ["skeleton", "content", "layout", "styling", "interactions", "accessibility", "anti-slop", "reviewers"]


def run(args: list[str], root: Path) -> None:
    proc = subprocess.run([sys.executable, str(SCRIPT_DIR / args[0]), *args[1:]], cwd=root, text=True)
    if proc.returncode:
        raise SystemExit(proc.returncode)


def ensure_phase0_ready(root: Path) -> None:
    bridge = ensure_bridge(root)
    phase0_meta = bridge / "phase0-plan.json"
    page_map = bridge / "page-map.json"
    design_system = bridge / "design-system.json"
    if not phase0_meta.exists():
        raise SystemExit("ERROR: .ui-bridge/phase0-plan.json not found. Run /ui-plan first so Phase 0 ordering exists.")
    if not page_map.exists():
        raise SystemExit("ERROR: .ui-bridge/page-map.json not found. Run /ui-plan first.")
    if not design_system.exists():
        raise SystemExit("ERROR: .ui-bridge/design-system.json not found. Run /ui-plan first.")


def phase0_pages(root: Path) -> list[dict]:
    data = read_json(ensure_bridge(root) / "phase0-plan.json", default={}) or {}
    return data.get("pages", [])


def page_lookup(root: Path) -> dict[str, dict]:
    page_map = read_json(ensure_bridge(root) / "page-map.json", default={}) or {}
    pages = page_map.get("pages", [])
    return {page.get("slug"): page for page in pages}


def selected_pages(root: Path, page: str | None, group: str | None, max_pages: int | None) -> list[dict]:
    ordered = []
    lookup = page_lookup(root)
    for meta in phase0_pages(root):
        slug = meta.get("slug")
        if slug in lookup:
            ordered.append(lookup[slug])
    if not ordered:
        ordered = list(lookup.values())
    if page:
        requested = "index" if page in ("home", "homepage") else page
        ordered = [p for p in ordered if p.get("slug") == requested]
    if group == "public":
        ordered = [p for p in ordered if not p.get("is_admin")]
    elif group == "admin":
        ordered = [p for p in ordered if p.get("is_admin")]
    if max_pages:
        ordered = ordered[:max_pages]
    return ordered


def build_token_css(root: Path) -> str:
    bridge = ensure_bridge(root)
    design_system = read_json(bridge / "design-system.json", default={}) or {}
    approved_brand = design_system.get("approved_brand", {}) or {}
    palette = (design_system.get("colors", {}) or {}).get("palette", {}) or {}
    typography = (design_system.get("typography", {}) or {}).get("font_pair", {}) or {}
    is_rtl = bool(design_system.get("is_rtl"))
    heading_font = approved_brand.get("fonts", {}).get("heading") or approved_brand.get("fonts", {}).get("arabic_heading") or typography.get("heading") or "system-ui"
    body_font = approved_brand.get("fonts", {}).get("body") or approved_brand.get("fonts", {}).get("arabic_body") or typography.get("body") or "system-ui"
    mono_font = typography.get("mono") or "monospace"
    lines = [
        "/* Shared design tokens for generated UI prototypes. */",
        ":root {",
        f"  --color-primary: {palette.get('primary', '#243D36')};",
        f"  --color-accent: {palette.get('accent', '#8A4D76')};",
        f"  --color-bg: {palette.get('bg', '#FFFFFF')};",
        f"  --color-surface: {palette.get('surface', '#F4F2EC')};",
        f"  --color-border: {palette.get('border', '#D7DCD8')};",
        f"  --color-text-primary: {palette.get('text_primary', approved_brand.get('palette', {}).get('text', '#1F2724'))};",
        f"  --color-text-secondary: {palette.get('text_secondary', '#53615C')};",
        f"  --font-heading: '{heading_font}', sans-serif;",
        f"  --font-body: '{body_font}', sans-serif;",
        f"  --font-mono: '{mono_font}', monospace;",
        "  --text-h1: clamp(2.4rem, 6vw, 5.4rem);",
        "  --text-h2: clamp(1.8rem, 3.5vw, 2.8rem);",
        "  --text-body: 1rem;",
        "  --space-2: 0.5rem;",
        "  --space-3: 0.75rem;",
        "  --space-4: 1rem;",
        "  --space-6: 1.5rem;",
        "  --space-8: 2rem;",
        "  --space-12: 3rem;",
        "  --radius-sm: 0.5rem;",
        "  --radius-md: 1rem;",
        "  --radius-lg: 1.5rem;",
        "  --shadow-card: 0 20px 50px rgba(12, 22, 19, 0.08);",
        "  --duration-fast: 160ms;",
        "  --duration-base: 220ms;",
        "  --ease-primary: cubic-bezier(0.22, 1, 0.36, 1);",
        "  --container-max: 1180px;",
        "}",
        "",
        "html { font-family: var(--font-body); font-size: 16px; }",
        f'html[dir="rtl"] {{ direction: {"rtl" if is_rtl else "ltr"}; }}',
        "body { background: var(--color-bg); color: var(--color-text-primary); }",
        ".container { width: min(var(--container-max), calc(100% - 2 * var(--space-6))); margin-inline: auto; }",
        ".site-shell-header { position: sticky; top: 0; z-index: 50; background: var(--color-surface); border-bottom: 1px solid var(--color-border); }",
        ".site-shell-footer { border-top: 1px solid var(--color-border); background: var(--color-surface); }",
        ".admin-shell { display: grid; grid-template-columns: 280px 1fr; min-height: 100vh; }",
        ".admin-shell .sidebar { background: var(--color-surface); border-inline-end: 1px solid var(--color-border); }",
        ".prototype-nav { position: fixed; bottom: 0; left: 0; right: 0; background: rgba(10,10,10,.96); color: rgba(255,255,255,.6); padding: 8px clamp(12px,3vw,32px); display: flex; align-items: center; gap: 6px; font-size: .72rem; z-index: 9999; flex-wrap: wrap; font-family: sans-serif; border-top: 1px solid rgba(255,255,255,.08); }",
        ".prototype-nav a { color: var(--color-primary); padding: 2px 4px; border-radius: 3px; }",
        ".proto-spacer { height: 48px; }",
        "@media (max-width: 768px) {",
        "  .container { width: min(var(--container-max), calc(100% - 2 * var(--space-4))); }",
        "  .admin-shell { grid-template-columns: 1fr; }",
        "}",
        "@media (prefers-reduced-motion: reduce) {",
        "  *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; }",
        "}",
    ]
    return "\n".join(lines) + "\n"


def partial_nav_public(project_name: str, pages: list[dict]) -> str:
    links = []
    map_items = []
    for page in pages:
        if page.get("is_admin"):
            continue
        slug = page.get("slug")
        label = page.get("name", slug)
        links.append(f'<a href="{slug}.html" data-page="{slug}">{label}</a>')
        map_items.append(f"'{slug}.html': '{slug}'")
    link_html = "\n      ".join(links) or '<a href="index.html" data-page="index">Home</a>'
    map_js = ", ".join(map_items) or "'index.html': 'index'"
    return (
        f'<div class="container shell-nav-inner">'
        f'<a href="index.html" class="brand-lockup" aria-label="{project_name}">{project_name}</a>'
        f'<nav class="shell-nav-links" aria-label="Primary navigation">{link_html}</nav>'
        f'</div>\n'
        f'<script>(function(){{var map={{ {map_js} }};var key=map[location.pathname.split("/").pop()];if(key){{var el=document.querySelector(\'[data-page="\'+key+\'"]\');if(el)el.classList.add("active");}}}})();</script>\n'
    )


def partial_footer_public(project_name: str) -> str:
    return (
        f'<div class="container"><div class="footer-copy"><strong>{project_name}</strong>'
        f'<p>Approved prototype reference generated from UI Phase 0 artifacts.</p></div></div>\n'
    )


def partial_sidebar_admin(pages: list[dict]) -> str:
    links = []
    map_items = []
    for page in pages:
        if not page.get("is_admin"):
            continue
        slug = page.get("slug")
        label = page.get("name", slug)
        links.append(f'<a href="{slug}.html" data-page="{slug}">{label}</a>')
        map_items.append(f"'{slug}.html': '{slug}'")
    if not links:
        links.append('<a href="admin-dashboard.html" data-page="admin-dashboard">Dashboard</a>')
        map_items.append("'admin-dashboard.html': 'admin-dashboard'")
    link_html = "\n  ".join(links)
    map_js = ", ".join(map_items)
    return (
        '<div class="admin-sidebar-inner">\n'
        '  <strong class="sidebar-title">Admin Pages</strong>\n'
        f'  {link_html}\n'
        '</div>\n'
        f'<script>(function(){{var map={{ {map_js} }};var key=map[location.pathname.split("/").pop()];if(key){{var el=document.querySelector(\'[data-page="\'+key+\'"]\');if(el)el.classList.add("active");}}}})();</script>\n'
    )


def compile_partials_script() -> str:
    return """from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
PARTIALS = ROOT / "_partials"
MARKER_RE = re.compile(r"<!-- PARTIAL:([a-z0-9-]+) -->(.*?)<!-- /PARTIAL:\\1 -->", re.DOTALL)


def partial_text(name: str) -> str:
    path = PARTIALS / f"{name}.html"
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


def stamp_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    changed = False

    def repl(match):
        nonlocal changed
        name = match.group(1)
        replacement = partial_text(name)
        changed = True
        return f"<!-- PARTIAL:{name} -->\\n{replacement}\\n<!-- /PARTIAL:{name} -->"

    updated = MARKER_RE.sub(repl, original)
    if changed and updated != original:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def main():
    for html_path in sorted(ROOT.glob("*.html")):
        if html_path.name == "prototype-hub.html":
            continue
        stamp_file(html_path)


if __name__ == "__main__":
    main()
"""


def prototype_index_html(project_name: str, pages: list[dict]) -> str:
    hero_cards = []
    page_items = []
    for index, page in enumerate(pages[:6], 1):
        slug = page.get("slug")
        label = page.get("name", slug)
        group = "Admin" if page.get("is_admin") else "Public"
        hero_cards.append(
            f'<article class="hero-card"><span class="hero-card-kicker">{group} page</span>'
            f'<h3>{label}</h3><p>Open the approved prototype and review its layout, tokens, and UX flow.</p>'
            f'<a href="{slug}.html">Open page</a></article>'
        )
        page_items.append(
            f'<article class="page-card"><div><span class="page-card-number">{index:02d}</span>'
            f'<h3>{label}</h3><p>{group} reference page generated from the current Phase 0 plan.</p></div>'
            f'<a href="{slug}.html" class="page-link">View prototype</a></article>'
        )
    items = "\n".join(page_items)
    hero_grid = "\n".join(hero_cards)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{project_name} Prototype Hub</title>
  <link rel="stylesheet" href="design-tokens.css">
  <style>
    :root {{
      --hub-grad-a: color-mix(in srgb, var(--color-primary) 14%, white);
      --hub-grad-b: color-mix(in srgb, var(--color-accent) 18%, white);
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: var(--font-body); background:
      radial-gradient(circle at top left, var(--hub-grad-a), transparent 40%),
      radial-gradient(circle at top right, var(--hub-grad-b), transparent 38%),
      linear-gradient(180deg, #fbfcfb 0%, var(--color-bg) 100%);
      color: var(--color-text-primary);
    }}
    a {{ color: inherit; text-decoration: none; }}
    .hub-shell {{ padding: clamp(28px, 5vw, 64px) 0 clamp(64px, 8vw, 110px); }}
    .hero {{ display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(320px, .9fr); gap: clamp(24px, 4vw, 56px); align-items: stretch; }}
    .hero-copy {{ background: rgba(255,255,255,.82); backdrop-filter: blur(8px); border: 1px solid rgba(27,44,27,.08); border-radius: 32px; padding: clamp(28px, 4vw, 46px); box-shadow: var(--shadow-card); }}
    .eyebrow {{ display: inline-flex; align-items: center; gap: 10px; font-size: .85rem; text-transform: uppercase; letter-spacing: .14em; color: var(--color-accent); font-weight: 800; }}
    .eyebrow::before {{ content: ""; width: 34px; height: 2px; background: currentColor; }}
    h1 {{ margin: 16px 0 14px; font-size: clamp(2.6rem, 6vw, 5.6rem); line-height: .95; font-family: var(--font-heading); max-width: 9ch; }}
    .hero-copy p {{ margin: 0; max-width: 58ch; color: var(--color-text-secondary); font-size: 1.05rem; }}
    .hero-actions {{ display: flex; gap: 14px; flex-wrap: wrap; margin-top: 28px; }}
    .button {{ display: inline-flex; align-items: center; justify-content: center; min-height: 46px; padding: 0 20px; border-radius: 999px; font-weight: 700; }}
    .button.primary {{ background: var(--color-primary); color: #fff; }}
    .button.secondary {{ border: 1px solid var(--color-border); background: rgba(255,255,255,.76); }}
    .hero-grid {{ display: grid; gap: 16px; }}
    .hero-card {{ background: rgba(255,255,255,.9); border: 1px solid rgba(27,44,27,.08); border-radius: 24px; padding: 22px; box-shadow: var(--shadow-card); }}
    .hero-card-kicker {{ font-size: .76rem; text-transform: uppercase; letter-spacing: .1em; color: var(--color-accent); font-weight: 800; }}
    .hero-card h3 {{ margin: 12px 0 8px; font-size: 1.2rem; font-family: var(--font-heading); }}
    .hero-card p {{ margin: 0 0 14px; color: var(--color-text-secondary); }}
    .hero-card a {{ color: var(--color-primary); font-weight: 800; }}
    .metrics {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 22px; }}
    .metric {{ background: rgba(255,255,255,.72); border: 1px solid rgba(27,44,27,.08); border-radius: 22px; padding: 18px; }}
    .metric strong {{ display: block; font-size: 1.9rem; font-family: var(--font-heading); }}
    .metric span {{ color: var(--color-text-secondary); font-size: .92rem; }}
    .section-head {{ display: flex; align-items: end; justify-content: space-between; gap: 18px; margin: clamp(40px, 7vw, 86px) 0 22px; }}
    .section-head h2 {{ margin: 0; font-family: var(--font-heading); font-size: clamp(1.8rem, 3vw, 2.8rem); }}
    .section-head p {{ margin: 0; max-width: 56ch; color: var(--color-text-secondary); }}
    .page-list {{ display: grid; gap: 16px; }}
    .page-card {{ display: grid; grid-template-columns: 1fr auto; gap: 16px; align-items: center; background: #fff; border: 1px solid var(--color-border); border-radius: 24px; padding: 22px; box-shadow: var(--shadow-card); }}
    .page-card-number {{ display: inline-flex; min-width: 44px; height: 44px; align-items: center; justify-content: center; border-radius: 999px; background: color-mix(in srgb, var(--color-primary) 12%, white); color: var(--color-primary); font-weight: 900; margin-bottom: 12px; }}
    .page-card h3 {{ margin: 0 0 6px; font-family: var(--font-heading); font-size: 1.2rem; }}
    .page-card p {{ margin: 0; color: var(--color-text-secondary); }}
    .page-link {{ color: #fff; background: var(--color-primary); padding: 12px 18px; border-radius: 999px; font-weight: 700; white-space: nowrap; }}
    @media (max-width: 900px) {{
      .hero {{ grid-template-columns: 1fr; }}
      .metrics {{ grid-template-columns: 1fr; }}
      .page-card {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main id="main" class="container hub-shell">
    <section class="hero">
      <div class="hero-copy">
        <span class="eyebrow">Prototype system</span>
        <h1>{project_name}</h1>
        <p>Client-facing UI review hub generated from the current Spec Kit plan. Open any approved page, review the visual system, and walk the prototype set with one consistent design language.</p>
        <div class="hero-actions">
          <a class="button primary" href="{pages[0].get("slug")}.html">Open first page</a>
          <a class="button secondary" href="#pages">Browse all pages</a>
        </div>
        <div class="metrics">
          <div class="metric"><strong>{len(pages)}</strong><span>Approved page references</span></div>
          <div class="metric"><strong>Phase 0</strong><span>Design-first workflow state</span></div>
          <div class="metric"><strong>100%</strong><span>Token-driven page shell</span></div>
        </div>
      </div>
      <div class="hero-grid">
        {hero_grid}
      </div>
    </section>

    <section id="pages">
      <div class="section-head">
        <h2>Page set</h2>
        <p>Use this hub when you want a quick route through all generated screens without jumping straight into the canvas preview.</p>
      </div>
      <div class="page-list">
        {items}
      </div>
    </section>
  </main>
</body>
</html>
"""


def ensure_prototype_infrastructure(root: Path, pages: list[dict]) -> None:
    bridge = ensure_bridge(root)
    design_system = read_json(bridge / "design-system.json", default={}) or {}
    project_name = ((design_system.get("spec") or {}).get("project_name")) or "UI Prototype"
    proto_dir = root / "ui-prototypes"
    partials_dir = proto_dir / "_partials"
    proto_dir.mkdir(exist_ok=True)
    partials_dir.mkdir(parents=True, exist_ok=True)

    token_css = build_token_css(root)
    (proto_dir / "design-tokens.css").write_text(token_css, encoding="utf-8")
    (proto_dir / "compile-partials.py").write_text(compile_partials_script(), encoding="utf-8")
    (partials_dir / "nav-public.html").write_text(partial_nav_public(project_name, pages), encoding="utf-8")
    (partials_dir / "footer-public.html").write_text(partial_footer_public(project_name), encoding="utf-8")
    (partials_dir / "sidebar-admin.html").write_text(partial_sidebar_admin(pages), encoding="utf-8")
    (proto_dir / "prototype-hub.html").write_text(prototype_index_html(project_name, pages), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run staged UI implementation workflow")
    parser.add_argument("--root", default=".")
    parser.add_argument("--page")
    parser.add_argument("--group", choices=["public", "admin"])
    parser.add_argument("--max-pages", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--draft", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    ensure_phase0_ready(root)
    pages = selected_pages(root, args.page, args.group, args.max_pages)
    if not pages:
        raise SystemExit("ERROR: no pages selected for UI implementation.")

    ensure_prototype_infrastructure(root, pages)

    prepare = ["prepare_html_stages.py", "--root", str(root)]
    if args.page:
        prepare += ["--page", args.page]
    if args.group:
        prepare += ["--group", args.group]
    if args.max_pages:
        prepare += ["--max-pages", str(args.max_pages)]
    if args.resume:
        prepare.append("--resume")
    if args.draft:
        prepare.append("--draft")
    run(prepare, root)

    proto_dir = root / "ui-prototypes"
    for page in pages:
        slug = page["slug"]
        for stage in STAGES:
            cmd = ["run_html_stage.py", "--root", str(root), "--page", slug, "--stage", stage]
            if args.draft:
                cmd.append("--draft")
            run(cmd, root)

        candidate = ensure_bridge(root) / "html-stages" / slug / "08-reviewed-final-candidate.html"
        if not args.draft:
            run(["review_artifacts.py", "--root", str(root), str(candidate)], root)
            shutil.copyfile(candidate, proto_dir / f"{slug}.html")
            run([str(proto_dir / "compile-partials.py")], root)
            print(f"Published reviewed prototype in Phase 0 order: {proto_dir / f'{slug}.html'}")


if __name__ == "__main__":
    main()
