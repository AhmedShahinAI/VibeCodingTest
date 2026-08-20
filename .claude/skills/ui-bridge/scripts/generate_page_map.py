"""
generate_page_map.py — Build page map from parsed Spec Kit + brand data.

Usage:
    python scripts/generate_page_map.py [--root PATH]

Reads:
    .ui-bridge/parsed-speckit.json
    .ui-bridge/brand-signals.json

Writes:
    .ui-bridge/page-map.md
    .ui-bridge/page-map.json
"""
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import date


def page_to_slug(page_path: str) -> str:
    """Convert pages/admin/courses/index.vue → admin-courses."""
    p = page_path
    p = p.replace("pages/", "").replace("apps/web/pages/", "")
    p = re.sub(r'\.(vue|tsx|jsx|html)$', '', p)
    p = p.replace("/index", "")
    p = re.sub(r'\[slug\]|\[id\]|\[.*?\]', 'detail', p)
    p = p.replace("/", "-").strip("-")
    return p or "index"


def page_to_name(slug: str) -> str:
    """admin-courses → Admin Courses."""
    return slug.replace("-", " ").title()


def is_admin(page_path: str) -> bool:
    return "pages/admin/" in page_path or "admin/" in page_path or page_path.startswith("admin-")


def static_content_for(slug: str) -> dict:
    if slug in ("index", "home"):
        return {
            "hero": ["specific Arabic value proposition", "proof statement", "registration CTA"],
            "courses": ["3 realistic course titles", "category", "duration", "upcoming date"],
            "experts": ["3 Arabic expert names", "title", "credentials"],
            "partners": ["realistic organization names"],
        }
    if "courses" in slug:
        return {"courses": ["course title", "category", "objectives", "round dates", "price or seats"]}
    if "experts" in slug:
        return {"experts": ["expert name", "role", "bio", "certificates", "companies"]}
    if slug.startswith("admin"):
        return {"admin": ["table rows", "form labels", "status labels", "empty/error states"]}
    return {"content": ["representative static copy", "realistic labels", "page-specific data"]}


def api_notes_for(slug: str) -> dict:
    if slug.startswith("admin"):
        return {"implementation_only": "Admin APIs belong in contracts/admin.md; do not fetch data in static HTML."}
    return {"implementation_only": "Public APIs belong in contracts/public.md; static prototype embeds representative content."}


def infer_sections(page_path: str, slug: str, direction: str) -> list:
    """Infer likely sections from page type."""
    sections_map = {
        "index": ["Navbar", "Hero section", "Featured items", "CTA banner", "Footer"],
        "courses": ["Navbar", "Page header", "Category filter tabs", "Course grid", "Pagination", "Footer"],
        "courses-detail": ["Navbar", "Course hero with image", "Description & objectives", "Rounds table", "Registration form", "Footer"],
        "experts": ["Navbar", "Page header", "Expert grid", "Footer"],
        "experts-detail": ["Navbar", "Expert hero (photo + name + title)", "Bio section", "Experience & certificates", "Companies", "Projects grid", "Footer"],
        "partners": ["Navbar", "Page header", "Partner logo grid", "Footer"],
        "events": ["Navbar", "Page header", "Event cards grid", "Footer"],
        "faq": ["Navbar", "Page header", "FAQ accordion", "Footer"],
        "terms": ["Navbar", "Page header", "Terms content sections", "Footer"],
        "admin-login": ["Login card", "Email + password form", "Submit button", "Error state"],
        "admin-dashboard": ["Sidebar", "Top bar", "Stats cards", "Recent registrations table", "Quick actions"],
        "admin-courses": ["Sidebar", "Top bar", "Courses table", "New course button", "Status filter"],
        "admin-courses-detail": ["Sidebar", "Top bar", "Course form", "Rounds inline table", "Save/delete actions"],
        "admin-registrations": ["Sidebar", "Top bar", "Filter tabs", "Registrations table", "Pagination"],
        "admin-registrations-detail": ["Sidebar", "Top bar", "Registration info card", "Status dropdown", "Notes timeline", "Add note form"],
        "admin-experts": ["Sidebar", "Top bar", "Experts table", "New expert button"],
        "admin-experts-detail": ["Sidebar", "Top bar", "Expert form", "Certificates list", "Companies list", "Projects list"],
        "admin-media": ["Sidebar", "Top bar", "Upload dropzone", "Media grid", "Pagination"],
        "admin-seo": ["Sidebar", "Top bar", "Page slug selector", "SEO form", "Preview"],
        "admin-partners": ["Sidebar", "Top bar", "Partners table with ordering", "Add form"],
        "admin-events": ["Sidebar", "Top bar", "Events table", "Add/edit form"],
        "admin-faq": ["Sidebar", "Top bar", "FAQ ordered list", "Add/edit form"],
        "admin-terms": ["Sidebar", "Top bar", "Terms ordered list", "Rich text editor"],
        "admin-users": ["Sidebar", "Top bar", "Users table", "Invite user form"],
    }
    return sections_map.get(slug, ["Navbar", "Main content", "Footer"])


def normalize_pages(pages: list) -> list:
    normalized = []
    for page in pages:
        if isinstance(page, dict):
            slug = page.get("slug") or page_to_slug(page.get("source", "page"))
            source = page.get("source", slug)
            name = page.get("name") or page_to_name(slug)
        else:
            slug = page_to_slug(str(page))
            source = str(page)
            name = page_to_name(slug)
        normalized.append({"slug": slug, "source": source, "name": name, "is_admin": is_admin(slug) or is_admin(source)})
    return normalized


def apply_scope(pages: list, page: str | None = None, group: str | None = None, max_pages: int | None = None) -> list:
    scoped = list(pages)
    if page:
        requested = "index" if page in ("home", "homepage") else page
        scoped = [p for p in scoped if p["slug"] == requested]
        if not scoped:
            raise SystemExit("ERROR: scoped page not found in parsed Spec Kit pages: %s" % page)
    if group == "public":
        scoped = [p for p in scoped if not p["is_admin"]]
    elif group == "admin":
        scoped = [p for p in scoped if p["is_admin"]]
    if max_pages is not None:
        scoped = scoped[:max_pages]
    return scoped


def build_page_map(pages: list, brand: dict, project_name: str, default_direction: str = "ltr") -> tuple:
    """Build both markdown and JSON representations of the page map."""
    direction = brand.get("direction") or default_direction or "ltr"
    normalized = normalize_pages(pages)

    public_pages = [p for p in normalized if not p["is_admin"]]
    admin_pages = [p for p in normalized if p["is_admin"]]

    entries = []
    for page in public_pages + admin_pages:
        slug = page["slug"]
        name = page["name"]
        page_dir = "ltr" if page["is_admin"] else direction
        sections = infer_sections(page, slug, page_dir)
        entry = {
            "name": name,
            "slug": slug,
            "source": page["source"],
            "html_output": f"ui-prototypes/{slug}.html",
            "direction": page_dir,
            "is_admin": page["is_admin"],
            "sections": sections,
            "static_content_needed": static_content_for(slug),
            "api_contract_notes": api_notes_for(slug),
        }
        entries.append(entry)

    # Markdown
    lines = [
        f"# Page Map: {project_name}",
        "",
        f"Generated: {date.today().isoformat()}",
        f"Total pages: {len(entries)}",
        f"Public pages: {len(public_pages)}",
        f"Admin pages: {len(admin_pages)}",
        "",
        "---",
        "",
        "## Public Pages",
        "",
    ]

    for e in entries:
        if not e["is_admin"]:
            lines += [
                f"### {e['name']}",
                f"- **HTML output**: `{e['html_output']}`",
                f"- **Source task**: `{e['source']}`",
                f"- **Direction**: {e['direction'].upper()}",
                "- **Sections**:",
            ]
            for i, s in enumerate(e["sections"], 1):
                lines.append(f"  {i}. {s}")
            lines += [f"- **Static content needed**: `{json.dumps(e['static_content_needed'], ensure_ascii=False)}`", ""]

    lines += ["## Admin Pages", ""]
    for e in entries:
        if e["is_admin"]:
            lines += [
                f"### {e['name']}",
                f"- **HTML output**: `{e['html_output']}`",
                f"- **Source task**: `{e['source']}`",
                f"- **Direction**: {e['direction'].upper()}",
                "- **Sections**:",
            ]
            for i, s in enumerate(e["sections"], 1):
                lines.append(f"  {i}. {s}")
            lines += [f"- **Static content needed**: `{json.dumps(e['static_content_needed'], ensure_ascii=False)}`", ""]

    return "\n".join(lines), entries


def main():
    parser = argparse.ArgumentParser(description="Generate page map")
    parser.add_argument("--root", default=".", help="Project root path")
    parser.add_argument("--page", help="Generate the page map for one page slug, e.g. index or home")
    parser.add_argument("--group", choices=["public", "admin"], help="Generate only public or admin pages")
    parser.add_argument("--max-pages", type=int, help="Limit the number of scoped pages")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    ui_bridge = root / ".ui-bridge"
    ui_bridge.mkdir(exist_ok=True)

    # Load parsed speckit
    speckit_json = ui_bridge / "parsed-speckit.json"
    if not speckit_json.exists():
        print("ERROR: .ui-bridge/parsed-speckit.json not found. Run parse_speckit.py first.", file=sys.stderr)
        sys.exit(1)
    speckit = json.loads(speckit_json.read_text())

    # Load brand signals
    brand_json = ui_bridge / "brand-signals.json"
    brand = {}
    if brand_json.exists():
        brand_data = json.loads(brand_json.read_text())
        brand = brand_data.get("brand_decisions") or {}

    pages = speckit.get("tasks", {}).get("pages_structured") or speckit.get("tasks", {}).get("pages", [])
    project_name = speckit.get("plan", {}).get("project_name", "Project")

    if not pages:
        print("WARNING: No pages found in parsed-speckit.json. Check tasks.md for page file paths.", file=sys.stderr)

    normalized = normalize_pages(pages)
    scoped_pages = apply_scope(normalized, page=args.page, group=args.group, max_pages=args.max_pages)
    default_direction = speckit.get("plan", {}).get("direction", "ltr")
    markdown, entries = build_page_map(scoped_pages, brand, project_name, default_direction=default_direction)

    # Write markdown
    md_path = ui_bridge / "page-map.md"
    md_path.write_text(markdown, encoding="utf-8")

    # Write JSON
    json_path = ui_bridge / "page-map.json"
    scope = {"page": args.page, "group": args.group, "max_pages": args.max_pages}
    json_path.write_text(json.dumps({"pages": entries, "generated": date.today().isoformat(), "scope": scope},
                                     indent=2, ensure_ascii=False), encoding="utf-8")

    scope_msg = " scoped" if any(scope.values()) else ""
    print(f"Generated{scope_msg} page map: {len(entries)} pages", file=sys.stderr)
    print(f"  Markdown: {md_path}", file=sys.stderr)
    print(f"  JSON:     {json_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
