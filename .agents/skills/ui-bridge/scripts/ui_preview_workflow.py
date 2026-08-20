"""
ui-into-preview - generate a deployable ui-preview canvas folder.

Default usage:
  python scripts/ui_preview_workflow.py --root .
"""
from __future__ import annotations

import argparse
import datetime
import json
import shutil
import sys
from html.parser import HTMLParser
from pathlib import Path

from ui_bridge_core import SpecKitResolver, ensure_bridge, read_json


def parse_args():
    p = argparse.ArgumentParser(description="Generate ui-preview canvas tool")
    p.add_argument("--root", default=".", help="Project root used for default path resolution")
    p.add_argument("--prototype-dir", help="Folder containing *.html prototypes")
    p.add_argument("--spec-dir", help="Folder containing *.md spec files")
    p.add_argument("--output-dir", help="Output folder")
    p.add_argument("--page-map", help="Path to page-map.json")
    p.add_argument("--project", help="Project name shown in canvas title")
    return p.parse_args()


def page_id(slug: str) -> str:
    return "page_" + slug.replace("-", "_")


def doc_id(stem: str) -> str:
    return "doc_" + stem.replace("-", "_")


def resolve_defaults(root: Path, args) -> dict:
    bridge = ensure_bridge(root)
    ds = read_json(bridge / "design-system.json", default={}) or {}
    spec = ds.get("spec", {}) or {}
    spec_dir = None
    plan_path = spec.get("plan_path")
    if plan_path:
        spec_dir = Path(plan_path).resolve().parent
    if not spec_dir:
        try:
            resolved_plan = SpecKitResolver(root).find("plan.md")
            if resolved_plan:
                spec_dir = resolved_plan.parent
        except RuntimeError:
            spec_dir = root / "specs"
    return {
        "prototype_dir": Path(args.prototype_dir).resolve() if args.prototype_dir else (root / "ui-prototypes"),
        "spec_dir": Path(args.spec_dir).resolve() if args.spec_dir else (spec_dir or root / "specs"),
        "output_dir": Path(args.output_dir).resolve() if args.output_dir else (root / "ui-preview"),
        "page_map": Path(args.page_map).resolve() if args.page_map else (bridge / "page-map.json"),
        "project": args.project or spec.get("project_name") or "UI Preview",
    }


def load_page_map(path: Path) -> list:
    data = json.loads(path.read_text(encoding="utf-8"))
    pages = []
    for p in data.get("pages", []):
        slug = p["slug"]
        if "group" in p:
            group = p["group"]
        elif p.get("is_admin") is True:
            group = "Admin"
        elif p.get("is_admin") is False:
            group = "Public"
        else:
            group = "Other"
        pages.append(
            {
                "id": page_id(slug),
                "slug": slug,
                "title": p.get("title") or p.get("name") or slug.replace("-", " ").title(),
                "group": group,
                "file": f"pages/{slug}.html",
                "direction": p.get("direction", "ltr"),
            }
        )
    return pages


def _html_direction(html_path: Path) -> str:
    try:
        head = html_path.read_text(encoding="utf-8", errors="ignore")[:1000]
        if re_search(r'<html[^>]*\bdir=["\']?rtl', head):
            return "rtl"
    except OSError:
        pass
    return "ltr"


def re_search(pattern: str, text: str) -> bool:
    import re

    return bool(re.search(pattern, text, re.IGNORECASE))


def discover_pages_from_dir(proto_dir: Path) -> list:
    pages = []
    for f in sorted(proto_dir.glob("*.html")):
        if f.stem.startswith("_"):
            continue
        slug = f.stem
        if slug == "index":
            continue
        pages.append(
            {
                "id": page_id(slug),
                "slug": slug,
                "title": slug.replace("-", " ").title(),
                "group": "Admin" if slug.startswith("admin") else "Public",
                "file": f"pages/{slug}.html",
                "direction": _html_direction(f),
            }
        )
    return pages


_STORY_W, _STORY_H, _STORY_PAD = 1280, 900, 80


def generate_story_stops(pages: list, state: dict) -> list:
    frame_map = {f["id"]: f for f in state["frames"]}
    stops = []
    for p in pages:
        frame = frame_map.get(p["id"])
        if not frame or not frame.get("visible", True):
            continue
        zoom = min(
            3.0,
            max(
                0.2,
                min(
                    (_STORY_W - _STORY_PAD * 2) / frame["width"],
                    (_STORY_H - _STORY_PAD * 2) / frame["height"],
                ),
            ),
        )
        vx = (_STORY_W - frame["width"] * zoom) / 2 - frame["x"] * zoom
        vy = (_STORY_H - frame["height"] * zoom) / 2 - frame["y"] * zoom
        stops.append(
            {
                "id": "stop_" + p["id"],
                "label": p["title"],
                "viewport": {"x": round(vx, 1), "y": round(vy, 1), "zoom": round(zoom, 4)},
            }
        )
    return stops


def generate_scenario_docs(pages: list, nav_wires: list, out_docs_dir: Path) -> list:
    from collections import defaultdict

    id_to_page = {p["id"]: p for p in pages}
    wire_out = defaultdict(list)
    wire_in = defaultdict(list)
    for wire in nav_wires:
        wire_out[wire["from"]].append(wire["to"])
        wire_in[wire["to"]].append(wire["from"])

    groups = {}
    for page in pages:
        groups.setdefault(page["group"], []).append(page)

    written_docs = []
    for group_name, group_pages in groups.items():
        slug = "scenario-" + group_name.lower().replace(" ", "-")
        fname = slug + ".md"
        fpath = out_docs_dir / fname
        lines = [
            f"# {group_name} - User Scenarios",
            "",
            f"Generated on {datetime.date.today().isoformat()} for client presentation review.",
            "",
        ]
        for page in group_pages:
            outs = [id_to_page[t]["title"] for t in wire_out.get(page["id"], []) if t in id_to_page]
            ins = [id_to_page[s]["title"] for s in wire_in.get(page["id"], []) if s in id_to_page]
            lines += [
                f"## {page['title']}",
                f"**File:** `{page['file']}`  ",
                f"**Direction:** {'RTL' if page.get('direction') == 'rtl' else 'LTR'}  ",
                ("**From:** " + ", ".join(ins) if ins else "**From:** *(entry point)*") + "  ",
                ("**To:** " + ", ".join(outs) if outs else "**To:** *(terminal page)*"),
                "",
            ]
        fpath.write_text("\n".join(lines), encoding="utf-8")
        written_docs.append({"id": doc_id(slug), "title": f"{group_name} Scenarios", "file": f"docs/{fname}"})
    return written_docs


class _LinkScanner(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for key, value in attrs:
                if key == "href" and value:
                    self.hrefs.append(value)


def scan_nav_wires(source_id: str, html: str, slug_to_id: dict) -> list:
    scanner = _LinkScanner()
    scanner.feed(html)
    wires = []
    seen = set()
    for href in scanner.hrefs:
        if href.startswith(("http", "mailto", "#", "javascript")):
            continue
        stem = Path(href.split("?")[0].split("#")[0]).stem
        target_id = slug_to_id.get(stem)
        if target_id and target_id != source_id:
            key = (source_id, target_id)
            if key not in seen:
                seen.add(key)
                wires.append({"from": source_id, "to": target_id})
    return wires


FRAME_W, FRAME_H, GAP_Y, GAP_X = 380, 480, 40, 120


def generate_default_layout(pages: list) -> dict:
    seen_groups = []
    groups = {}
    for page in pages:
        group = page.get("group", "Other")
        if group not in groups:
            seen_groups.append(group)
            groups[group] = []
        groups[group].append(page)

    frames = []
    col_x = 0
    for group_name in seen_groups:
        y = 0
        for page in groups[group_name]:
            frames.append({"id": page["id"], "x": col_x, "y": y, "width": FRAME_W, "height": FRAME_H, "visible": True})
            y += FRAME_H + GAP_Y
        col_x += FRAME_W + GAP_X

    return {"version": 1, "frames": frames, "wires": [], "docs": [], "story_stops": []}


def build_manifest(project: str, pages: list, docs: list, nav_wires: list) -> dict:
    return {
        "version": 1,
        "generated": datetime.date.today().isoformat(),
        "project": project,
        "pages": pages,
        "docs": docs,
        "nav_wires": nav_wires,
    }


def append_new_pages(state: dict, manifest: dict) -> bool:
    existing = {f["id"] for f in state["frames"]}
    new_pages = [p for p in manifest["pages"] if p["id"] not in existing]
    if not new_pages:
        return False
    max_right = max((f["x"] + f["width"] for f in state["frames"]), default=0)
    x = max_right + GAP_X
    y = 0
    for page in new_pages:
        state["frames"].append({"id": page["id"], "x": x, "y": y, "width": FRAME_W, "height": FRAME_H, "visible": True})
        y += FRAME_H + GAP_Y
    return True


def run(prototype_dir: Path, spec_dir: Path, output_dir: Path, page_map: Path | None, project: str) -> None:
    if page_map and page_map.exists():
        pages = load_page_map(page_map)
    else:
        pages = discover_pages_from_dir(prototype_dir)
    slug_to_id = {p["slug"]: p["id"] for p in pages}

    for page in pages:
        src = prototype_dir / f"{page['slug']}.html"
        if not src.exists():
            print(f"  [warn] missing prototype: {src}", file=sys.stderr)

    doc_files = sorted(spec_dir.glob("*.md")) if spec_dir.exists() else []
    docs = [{"id": doc_id(f.stem), "title": f.stem.replace("-", " ").title(), "file": f"docs/{f.name}"} for f in doc_files]

    pages_out = output_dir / "pages"
    pages_out.mkdir(parents=True, exist_ok=True)
    for page in pages:
        src = prototype_dir / f"{page['slug']}.html"
        if src.exists():
            shutil.copy2(src, pages_out / f"{page['slug']}.html")

    docs_out = output_dir / "docs"
    docs_out.mkdir(parents=True, exist_ok=True)
    for f in doc_files:
        shutil.copy2(f, docs_out / f.name)

    nav_wires = []
    for page in pages:
        html_path = pages_out / f"{page['slug']}.html"
        if html_path.exists():
            html_text = html_path.read_text(encoding="utf-8", errors="ignore")
            nav_wires.extend(scan_nav_wires(page["id"], html_text, slug_to_id))

    scenario_docs = generate_scenario_docs(pages, nav_wires, docs_out)
    docs = docs + scenario_docs
    manifest = build_manifest(project, pages, docs, nav_wires)
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    state_path = output_dir / "canvas-state.json"
    dirty = False
    if not state_path.exists():
        state = generate_default_layout(pages)
        dirty = True
    else:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if append_new_pages(state, manifest):
            dirty = True

    if not state.get("story_stops"):
        state["story_stops"] = generate_story_stops(pages, state)
        dirty = True

    if dirty:
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    srv_src = Path(__file__).parent.parent / "canvas-app" / "server.py"
    if srv_src.exists():
        shutil.copy2(srv_src, output_dir / "server.py")

    _write_index_html(output_dir, project)
    print(f"[ui-into-preview] {output_dir}/ ready. Push to GitHub and enable Pages.")


def _write_index_html(out: Path, project: str) -> None:
    skill_dir = Path(__file__).parent.parent
    app_dir = skill_dir / "canvas-app"
    template = (app_dir / "index.template.html").read_text(encoding="utf-8")
    css_text = (app_dir / "canvas.css").read_text(encoding="utf-8")
    js_modules = [
        "markdown-parser.js",
        "state-manager.js",
        "canvas-core.js",
        "frame-manager.js",
        "layers-panel.js",
        "wiring.js",
        "doc-cards.js",
        "minimap.js",
        "presentation.js",
        "page-modal.js",
        "app.js",
    ]
    js_parts = []
    for name in js_modules:
        js_path = app_dir / name
        if js_path.exists():
            js_parts.append(f"/* --- {name} --- */\n" + js_path.read_text(encoding="utf-8"))
    js_text = "\n\n".join(js_parts)
    html = template.replace("{{PROJECT}}", project).replace("{{CSS}}", css_text).replace("{{JS}}", js_text)
    (out / "index.html").write_text(html, encoding="utf-8")


def main():
    args = parse_args()
    root = Path(args.root).resolve()
    defaults = resolve_defaults(root, args)
    run(
        prototype_dir=defaults["prototype_dir"],
        spec_dir=defaults["spec_dir"],
        output_dir=defaults["output_dir"],
        page_map=defaults["page_map"] if defaults["page_map"].exists() else None,
        project=defaults["project"],
    )


if __name__ == "__main__":
    main()
