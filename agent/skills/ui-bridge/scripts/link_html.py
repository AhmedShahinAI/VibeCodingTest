"""
link_html.py — Scan generated HTML prototypes and match them to tasks.

Usage:
    python scripts/link_html.py [--root PATH] [--prototypes-dir PATH]

Reads:
    ui-prototypes/*.html
    tasks.md

Writes:
    .ui-bridge/task-html-map.json

Prints match statistics to stderr, JSON to stdout.
"""
import sys
import re
import json
import argparse
from pathlib import Path
from datetime import date

from ui_bridge_core import SpecKitResolver, ensure_bridge


def extract_html_sections(html_path: Path) -> dict:
    """Extract page title, id attributes, and section headings from an HTML file."""
    content = html_path.read_text(encoding="utf-8", errors="ignore")

    # Title
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else html_path.stem

    # Remove the project name suffix if present (e.g., " | Project Name")
    title = re.sub(r'\s*\|.*$', '', title).strip()

    # All id="" attributes
    ids = re.findall(r'\bid=["\']([^"\']+)["\']', content)
    # Filter out trivial/single-char ids
    ids = [i for i in ids if len(i) > 1]

    # Section headings with their parent id
    sections = []
    for m in re.finditer(r'<(?:section|header|main|nav|footer|div)[^>]*id=["\']([^"\']+)["\'][^>]*>.*?<h[1-3][^>]*>([^<]+)</h[1-3]>',
                          content, re.IGNORECASE | re.DOTALL):
        sections.append({"id": m.group(1), "heading": m.group(2).strip()})

    # If no structured sections found, fall back to all ids
    if not sections:
        sections = [{"id": i, "heading": i.replace("-", " ").title()} for i in ids[:10]]

    return {
        "slug": html_path.stem,
        "file": str(html_path),
        "title": title,
        "ids": ids,
        "sections": sections,
    }


def match_tasks_to_pages(tasks_path: Path, page_map: list) -> dict:
    """Match task lines in tasks.md to page slugs."""
    if not tasks_path.exists():
        return {}

    content = tasks_path.read_text(encoding="utf-8")
    task_lines = re.findall(r'^- \[[ x]\]\s+(T\d+.*)$', content, re.MULTILINE)

    matches = {}  # task_id → {file, sections, task_line}

    for task_line in task_lines:
        task_id_match = re.match(r'T\d+(?:-\d+)?', task_line)
        if not task_id_match:
            continue
        task_id = task_id_match.group()

        task_lower = task_line.lower()

        for page in page_map:
            slug = page["slug"]
            file_path = page["file"]
            file_lower = file_path.replace("\\", "/").lower()
            file_windows_lower = file_path.replace("/", "\\").lower()

            matched = False

            # Only prototype tasks should receive prototype references. Do not
            # infer from implementation paths such as apps/web/pages/index.vue;
            # that pollutes unrelated engineering tasks in home-only runs.
            if file_lower in task_lower or file_windows_lower in task_lower:
                matched = True

            if matched:
                matches[task_id] = {
                    "task_line": task_line,
                    "file": file_path,
                    "slug": slug,
                    "sections": page["sections"],
                }
                break

    return matches


def build_prototype_index(page_map: list) -> str:
    """Build markdown table of all prototypes."""
    lines = [
        "## UI Prototype Index",
        "",
        f"Generated: {date.today().isoformat()}",
        f"Total: {len(page_map)} page(s)",
        "",
        "| Page | File | Sections |",
        "|------|------|----------|",
    ]
    for page in page_map:
        name = page["title"]
        rel = page["file"]
        n = len(page["sections"])
        lines.append(f"| {name} | `{rel}` | {n} |")
    return "\n".join(lines)


def resolve_tasks_path(root: Path) -> Path:
    try:
        resolved = SpecKitResolver(root).find("tasks.md")
        if resolved:
            return resolved
    except RuntimeError as exc:
        raise SystemExit("ERROR: %s" % exc)
    raise SystemExit("ERROR: tasks.md not found. Cannot update.")


def resolve_plan_path(root: Path) -> Path:
    try:
        resolved = SpecKitResolver(root).find("plan.md")
        if resolved:
            return resolved
    except RuntimeError as exc:
        raise SystemExit("ERROR: %s" % exc)
    raise SystemExit("ERROR: plan.md not found. Cannot update.")


def update_tasks(tasks_path: Path, page_map: list, matches: dict) -> dict:
    content = tasks_path.read_text(encoding="utf-8", errors="ignore")
    original = content
    generated_by_slug = {page["slug"]: page for page in page_map}
    phase0_done = 0
    ui_refs_added = 0

    for slug, page in generated_by_slug.items():
        html_file = page["file"]
        variants = {
            html_file,
            html_file.replace("\\", "/"),
            html_file.replace("/", "\\"),
        }
        for variant in variants:
            pattern = re.compile(r"^(- \[ \].*?`%s`.*)$" % re.escape(variant), re.MULTILINE)
            content, count = pattern.subn(lambda m: m.group(1).replace("- [ ]", "- [x]", 1) + " ✅", content)
            phase0_done += count

    lines = content.splitlines()
    out_lines = []
    skip_next_ref = False
    for index, line in enumerate(lines):
        out_lines.append(line)
        task_match = re.match(r"^- \[[ xX]\]\s+(T\d+(?:-\d+)?)\b", line)
        if not task_match:
            skip_next_ref = line.strip().startswith("> **UI Reference**")
            continue
        task_id = task_match.group(1)
        if task_id not in matches:
            continue
        next_line = lines[index + 1].strip() if index + 1 < len(lines) else ""
        if skip_next_ref or next_line.startswith("> **UI Reference**"):
            continue
        info = matches[task_id]
        sections = info.get("sections", [])[:8]
        out_lines.append("  > **UI Reference**: `%s`" % info["file"])
        if sections:
            out_lines.append("  > **Sections to implement**:")
            for section in sections:
                out_lines.append("  > - %s -> `#%s`" % (section.get("heading", section.get("id", "Section")), section.get("id", "")))
        out_lines.append("  > **Implementation rule**: Match the approved HTML prototype. Visual changes require approval.")
        ui_refs_added += 1

    content = "\n".join(out_lines) + ("\n" if original.endswith("\n") else "")
    if content != original:
        tasks_path.write_text(content, encoding="utf-8")
    return {"phase0_done": phase0_done, "ui_refs_added": ui_refs_added}


def update_plan(plan_path: Path, page_map: list) -> bool:
    content = plan_path.read_text(encoding="utf-8", errors="ignore")
    if "## UI Prototype Index" in content:
        return False
    index = build_prototype_index(page_map)
    block = "\n\n---\n\n%s\n\n### Design System Reference\n\nUse only approved `.ui-bridge` artifacts and approved HTML prototypes. Do not restyle from category defaults.\n" % index
    plan_path.write_text(content.rstrip() + block + "\n", encoding="utf-8")
    return True


def write_link_report(root: Path, page_map: list, matches: dict, task_update: dict, plan_updated: bool) -> Path:
    report = [
        "# UI Bridge Link Report",
        "",
        "Generated: %s" % date.today().isoformat(),
        "",
        "## Summary",
        "",
        "- HTML files scanned: %d" % len(page_map),
        "- Task matches: %d" % len(matches),
        "- Phase 0 tasks marked complete: %d" % task_update.get("phase0_done", 0),
        "- UI Reference blocks added: %d" % task_update.get("ui_refs_added", 0),
        "- UI Prototype Index appended: %s" % ("yes" if plan_updated else "already present"),
        "",
        "## Prototypes",
        "",
    ]
    for page in page_map:
        report.append("- `%s` (%d sections)" % (page["file"], len(page["sections"])))
    out = ensure_bridge(root) / "link-report.md"
    out.write_text("\n".join(report) + "\n", encoding="utf-8")
    return out


def main():
    parser = argparse.ArgumentParser(description="Link HTML prototypes to tasks")
    parser.add_argument("--root", default=".", help="Project root path")
    parser.add_argument("--prototypes-dir", default="ui-prototypes", help="Prototypes directory")
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    proto_dir = root / args.prototypes_dir

    if not proto_dir.is_dir():
        print(f"ERROR: {proto_dir} does not exist. Run /ui-implement first.", file=sys.stderr)
        sys.exit(1)

    html_files = sorted(proto_dir.glob("*.html"))
    print(f"Scanning {len(html_files)} HTML file(s)...", file=sys.stderr)

    if not html_files:
        print("ERROR: No HTML files found. Run /ui-implement first.", file=sys.stderr)
        sys.exit(1)

    page_map = []
    for html_file in html_files:
        page_data = extract_html_sections(html_file)
        page_data["file"] = str(html_file.relative_to(root))
        page_map.append(page_data)
        print(f"  {html_file.name}: {len(page_data['sections'])} section(s)", file=sys.stderr)

    tasks_path = resolve_tasks_path(root)
    plan_path = resolve_plan_path(root)
    matches = match_tasks_to_pages(tasks_path, page_map)
    print(f"Matched {len(matches)} task(s) to prototype files", file=sys.stderr)

    index_md = build_prototype_index(page_map)
    task_update = update_tasks(tasks_path, page_map, matches)
    plan_updated = update_plan(plan_path, page_map)
    report_path = write_link_report(root, page_map, matches, task_update, plan_updated)

    result = {
        "generated": date.today().isoformat(),
        "total_pages": len(page_map),
        "total_matches": len(matches),
        "pages": page_map,
        "task_matches": matches,
        "index_markdown": index_md,
    }

    # Save
    ui_bridge = root / ".ui-bridge"
    ui_bridge.mkdir(exist_ok=True)
    out = ui_bridge / "task-html-map.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved to: {out}", file=sys.stderr)
    print(f"Link report: {report_path}", file=sys.stderr)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
