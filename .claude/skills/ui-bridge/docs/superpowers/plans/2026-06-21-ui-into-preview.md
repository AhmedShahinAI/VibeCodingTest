# `/ui-into-preview` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `/ui-into-preview` subskill — a Python generator that produces a GitHub Pages-deployable infinite-canvas presentation tool from any set of HTML prototypes.

**Architecture:** A Python script (`ui_preview_workflow.py`) copies prototype HTML files into `ui-preview/`, generates `manifest.json` (page registry + fresh nav wires) and `canvas-state.json` (layout), then inlines the canvas app source from `canvas-app/` into a fully self-contained `index.html`. The canvas app is 100% vanilla HTML/JS/CSS — no build step, no framework, no backend. It loads both JSON files via `fetch()` at runtime.

**Tech Stack:** Python 3.8+ (pathlib, json, argparse, html.parser, shutil), Vanilla JS ES2020, CSS custom properties + CSS Grid, pytest, Node.js ≥18 (for JS pure-function tests only)

## Global Constraints

- `index.html` must be fully self-contained — no `<link>`, no `<script src>`, no external CDN
- `canvas-state.json` never overwritten once created — only new page frames may be appended
- `manifest.json` always regenerated on every run (includes fresh `nav_wires`)
- `nav_wires` live exclusively in `manifest.json`, never in `canvas-state.json`
- All page IDs: `page_<slug_with_underscores>` (hyphens → underscores)
- All doc IDs: `doc_<stem_with_underscores>`
- All wire IDs: `wire_<6-char-hex>` (generated with `secrets.token_hex(3)`)
- All story stop IDs: `stop_<6-char-hex>`
- `canvas-state.json` version field is always `1` for this implementation
- Zoom range: 10%–300%; default frame size: 380×620px; gap between frames: 40px; gap between clusters: 120px
- No React, no Vue, no build tools, no backend

---

## File Structure

**New files to create:**

```
ui-gernreate-from-plan/
├── canvas-app/
│   ├── index.template.html     ← HTML shell with {{CSS}} and {{JS}} placeholders
│   ├── canvas.css              ← All CSS (layout, frames, layers, toolbar, minimap)
│   ├── markdown-parser.js      ← Pure MD→HTML parser (~80 lines, no deps)
│   ├── state-manager.js        ← In-memory state, load/save/migrate/drag-drop
│   ├── canvas-core.js          ← Pan/zoom transform engine + event handlers
│   ├── frame-manager.js        ← Frame card DOM, drag reposition, blocker, focus
│   ├── layers-panel.js         ← Layers panel render + visibility toggles
│   ├── wiring.js               ← SVG bezier wires (nav from manifest + flow manual)
│   ├── doc-cards.js            ← Markdown doc cards on canvas
│   ├── minimap.js              ← Minimap thumbnail + viewport indicator
│   ├── presentation.js         ← Presentation mode + story stop navigation
│   └── app.js                  ← Entry point, orchestrates all modules
├── scripts/
│   └── ui_preview_workflow.py  ← NEW
├── subskills/
│   └── ui-preview/
│       └── SKILL.md            ← NEW
├── tests/
│   └── test_ui_preview.py      ← NEW
└── SKILL.md                    ← MODIFY
```

**JS module load order** (inlined into `index.html` in this sequence):
`markdown-parser.js` → `state-manager.js` → `canvas-core.js` → `frame-manager.js` → `layers-panel.js` → `wiring.js` → `doc-cards.js` → `minimap.js` → `presentation.js` → `app.js`

---

## Task 1: Repo scaffolding + Python CLI skeleton

**Files:**
- Create: `canvas-app/` (empty directory with `.gitkeep`)
- Create: `scripts/ui_preview_workflow.py`
- Create: `subskills/ui-preview/` (empty directory)
- Create: `tests/test_ui_preview.py`

**Interfaces:**
- Produces: CLI entry point `main()`, args namespace with `.prototype_dir`, `.spec_dir`, `.output_dir`, `.page_map`, `.project`

- [ ] **Step 1: Write failing test**

```python
# tests/test_ui_preview.py
import subprocess, sys

def test_cli_help_exits_zero():
    result = subprocess.run(
        [sys.executable, "scripts/ui_preview_workflow.py", "--help"],
        capture_output=True, cwd="."
    )
    assert result.returncode == 0
    assert b"--prototype-dir" in result.stdout

def test_cli_missing_required_arg_exits_nonzero():
    result = subprocess.run(
        [sys.executable, "scripts/ui_preview_workflow.py"],
        capture_output=True, cwd="."
    )
    assert result.returncode != 0
```

- [ ] **Step 2: Run tests to see them fail**

```
pytest tests/test_ui_preview.py::test_cli_help_exits_zero -v
```
Expected: `ERROR` — `scripts/ui_preview_workflow.py` not found

- [ ] **Step 3: Create the script skeleton**

```python
# scripts/ui_preview_workflow.py
"""
ui-into-preview — generates ui-preview/ canvas presentation folder.

Usage:
  python scripts/ui_preview_workflow.py \
    --prototype-dir ui-prototypes \
    --spec-dir specs/001-edtech-marketing-crm \
    --output-dir ui-preview \
    --page-map .ui-bridge/page-map.json \
    --project "My Project"
"""
import argparse, json, shutil, sys, secrets
from pathlib import Path
from html.parser import HTMLParser


def parse_args():
    p = argparse.ArgumentParser(description="Generate ui-preview/ canvas tool")
    p.add_argument("--prototype-dir", required=True, help="Folder containing *.html prototypes")
    p.add_argument("--spec-dir",      required=True, help="Folder containing *.md spec files")
    p.add_argument("--output-dir",    required=True, help="Output folder (will be created)")
    p.add_argument("--page-map",      required=True, help="Path to page-map.json")
    p.add_argument("--project",       default="UI Preview", help="Project name shown in canvas title")
    return p.parse_args()


def main():
    args = parse_args()
    print(f"[ui-into-preview] Generating {args.output_dir} ...")
    # steps will be filled in by later tasks
    print("[ui-into-preview] Done. Push ui-preview/ to GitHub and enable Pages.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Create directories and placeholder files**

```
mkdir canvas-app
echo. > canvas-app/.gitkeep
mkdir subskills\ui-preview
```

- [ ] **Step 5: Run tests — expect pass**

```
pytest tests/test_ui_preview.py -v
```
Expected: both tests pass

- [ ] **Step 6: Commit**

```
git add scripts/ui_preview_workflow.py tests/test_ui_preview.py canvas-app/.gitkeep subskills/ui-preview/
git commit -m "feat(ui-preview): scaffold Python CLI and test harness"
```

---

## Task 2: Page discovery + manifest generation

**Files:**
- Modify: `scripts/ui_preview_workflow.py` — add `page_id()`, `load_page_map()`, `build_manifest()`
- Modify: `tests/test_ui_preview.py` — add manifest tests

**Interfaces:**
- Produces: `build_manifest(project, pages, docs, nav_wires) → dict` matching spec Section 4 schema

- [ ] **Step 1: Write failing tests**

```python
# append to tests/test_ui_preview.py
import importlib.util, sys
from pathlib import Path

def load_script():
    spec = importlib.util.spec_from_file_location(
        "workflow", Path("scripts/ui_preview_workflow.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_page_id_converts_hyphens():
    wf = load_script()
    assert wf.page_id("course-detail") == "page_course_detail"
    assert wf.page_id("index") == "page_index"
    assert wf.page_id("admin-login") == "page_admin_login"

def test_build_manifest_structure():
    wf = load_script()
    pages = [{"id": "page_home", "slug": "index", "title": "Home",
              "group": "Public", "file": "pages/index.html", "direction": "rtl"}]
    docs  = [{"id": "doc_spec", "title": "Specification", "file": "docs/spec.md"}]
    result = wf.build_manifest("TestProject", pages, docs, [])
    assert result["version"] == 1
    assert result["project"] == "TestProject"
    assert result["pages"][0]["id"] == "page_home"
    assert result["docs"][0]["id"] == "doc_spec"
    assert "nav_wires" in result
    assert isinstance(result["nav_wires"], list)

def test_load_page_map(tmp_path):
    wf = load_script()
    pm = {"pages": [
        {"slug": "index",   "title": "Home",    "group": "Public", "direction": "rtl"},
        {"slug": "courses", "title": "Courses", "group": "Public", "direction": "rtl"},
        {"slug": "admin",   "title": "Admin",   "group": "Admin",  "direction": "ltr"},
    ]}
    f = tmp_path / "page-map.json"
    f.write_text(json.dumps(pm))
    pages = wf.load_page_map(str(f))
    assert pages[0]["id"] == "page_index"
    assert pages[1]["id"] == "page_courses"
    assert pages[2]["id"] == "page_admin"
    assert pages[0]["file"] == "pages/index.html"
```

- [ ] **Step 2: Run to confirm failure**

```
pytest tests/test_ui_preview.py::test_page_id_converts_hyphens -v
```
Expected: `AttributeError: module 'workflow' has no attribute 'page_id'`

- [ ] **Step 3: Implement functions**

```python
# add to scripts/ui_preview_workflow.py (after imports, before main)
import datetime

def page_id(slug: str) -> str:
    return "page_" + slug.replace("-", "_")

def doc_id(stem: str) -> str:
    return "doc_" + stem.replace("-", "_")

def load_page_map(path: str) -> list:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    pages = []
    for p in data.get("pages", []):
        slug = p["slug"]
        pages.append({
            "id":        page_id(slug),
            "slug":      slug,
            "title":     p.get("title", slug.replace("-", " ").title()),
            "group":     p.get("group", "Other"),
            "file":      f"pages/{slug}.html",
            "direction": p.get("direction", "ltr"),
        })
    return pages

def build_manifest(project: str, pages: list, docs: list, nav_wires: list) -> dict:
    return {
        "version":   1,
        "generated": datetime.date.today().isoformat(),
        "project":   project,
        "pages":     pages,
        "docs":      docs,
        "nav_wires": nav_wires,
    }
```

- [ ] **Step 4: Run tests — expect pass**

```
pytest tests/test_ui_preview.py -v
```
Expected: all tests pass

- [ ] **Step 5: Commit**

```
git add scripts/ui_preview_workflow.py tests/test_ui_preview.py
git commit -m "feat(ui-preview): page discovery and manifest generation"
```

---

## Task 3: Nav wire scanning

**Files:**
- Modify: `scripts/ui_preview_workflow.py` — add `LinkScanner`, `scan_nav_wires()`
- Modify: `tests/test_ui_preview.py` — add nav wire tests

**Interfaces:**
- Produces: `scan_nav_wires(source_page_id, html_text, slug_to_id) → list[dict]`
  Each dict: `{"from": "page_x", "to": "page_y"}`

- [ ] **Step 1: Write failing tests**

```python
def test_scan_nav_wires_finds_local_links():
    wf = load_script()
    html = '<a href="courses.html">Go</a><a href="experts.html">X</a>'
    slug_map = {"index": "page_index", "courses": "page_courses", "experts": "page_experts"}
    result = wf.scan_nav_wires("page_index", html, slug_map)
    assert {"from": "page_index", "to": "page_courses"} in result
    assert {"from": "page_index", "to": "page_experts"} in result

def test_scan_nav_wires_ignores_external():
    wf = load_script()
    html = '<a href="https://example.com">Ext</a><a href="mailto:x@y.com">Mail</a>'
    slug_map = {"index": "page_index"}
    result = wf.scan_nav_wires("page_index", html, slug_map)
    assert result == []

def test_scan_nav_wires_ignores_self():
    wf = load_script()
    html = '<a href="index.html">Home</a>'
    slug_map = {"index": "page_index"}
    result = wf.scan_nav_wires("page_index", html, slug_map)
    assert result == []
```

- [ ] **Step 2: Run to confirm failure**

```
pytest tests/test_ui_preview.py::test_scan_nav_wires_finds_local_links -v
```
Expected: `AttributeError: ... scan_nav_wires`

- [ ] **Step 3: Implement**

```python
# add to scripts/ui_preview_workflow.py

class _LinkScanner(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs: list[str] = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for k, v in attrs:
                if k == "href" and v:
                    self.hrefs.append(v)

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
```

- [ ] **Step 4: Run tests — expect pass**

```
pytest tests/test_ui_preview.py -v
```

- [ ] **Step 5: Commit**

```
git add scripts/ui_preview_workflow.py tests/test_ui_preview.py
git commit -m "feat(ui-preview): nav wire scanning from href attributes"
```

---

## Task 4: Auto layout algorithm

**Files:**
- Modify: `scripts/ui_preview_workflow.py` — add `generate_default_layout()`
- Modify: `tests/test_ui_preview.py`

**Interfaces:**
- Produces: `generate_default_layout(pages) → dict` — full `canvas-state.json` structure

- [ ] **Step 1: Write failing tests**

```python
def test_generate_default_layout_groups_columns():
    wf = load_script()
    pages = [
        {"id": "page_home",    "group": "Public"},
        {"id": "page_courses", "group": "Public"},
        {"id": "page_admin",   "group": "Admin"},
    ]
    state = wf.generate_default_layout(pages)
    frames = {f["id"]: f for f in state["frames"]}

    # Both Public pages in column x=0
    assert frames["page_home"]["x"] == 0
    assert frames["page_courses"]["x"] == 0
    # Second Public page is below first (620 height + 40 gap)
    assert frames["page_courses"]["y"] == 660
    # Admin cluster starts at x = 380 + 120 = 500
    assert frames["page_admin"]["x"] == 500
    assert frames["page_admin"]["y"] == 0

def test_generate_default_layout_schema():
    wf = load_script()
    state = wf.generate_default_layout([{"id": "page_x", "group": "G"}])
    assert state["version"] == 1
    assert isinstance(state["frames"], list)
    assert isinstance(state["wires"], list)
    assert isinstance(state["docs"], list)
    assert isinstance(state["story_stops"], list)
    assert state["frames"][0]["width"] == 380
    assert state["frames"][0]["height"] == 620
    assert state["frames"][0]["visible"] is True
```

- [ ] **Step 2: Run to confirm failure**

```
pytest tests/test_ui_preview.py::test_generate_default_layout_groups_columns -v
```

- [ ] **Step 3: Implement**

```python
def generate_default_layout(pages: list) -> dict:
    FRAME_W, FRAME_H, GAP_Y, GAP_X = 380, 620, 40, 120
    # preserve group order of first appearance
    seen_groups: list[str] = []
    groups: dict[str, list] = {}
    for p in pages:
        g = p.get("group", "Other")
        if g not in groups:
            seen_groups.append(g)
            groups[g] = []
        groups[g].append(p)

    frames = []
    col_x = 0
    for group_name in seen_groups:
        y = 0
        for page in groups[group_name]:
            frames.append({
                "id":      page["id"],
                "x":       col_x,
                "y":       y,
                "width":   FRAME_W,
                "height":  FRAME_H,
                "visible": True,
            })
            y += FRAME_H + GAP_Y
        col_x += FRAME_W + GAP_X

    return {"version": 1, "frames": frames, "wires": [], "docs": [], "story_stops": []}
```

- [ ] **Step 4: Run tests — expect pass**

```
pytest tests/test_ui_preview.py -v
```

- [ ] **Step 5: Commit**

```
git add scripts/ui_preview_workflow.py tests/test_ui_preview.py
git commit -m "feat(ui-preview): auto layout engine — group-based clustering"
```

---

## Task 5: `canvas-state.json` update logic (append new pages)

**Files:**
- Modify: `scripts/ui_preview_workflow.py` — add `append_new_pages()`
- Modify: `tests/test_ui_preview.py`

**Interfaces:**
- Produces: `append_new_pages(state, manifest) → bool` — mutates state in place, returns True if changed

- [ ] **Step 1: Write failing tests**

```python
def test_append_new_pages_preserves_existing_positions():
    wf = load_script()
    state = {
        "version": 1,
        "frames": [{"id": "page_home", "x": 99, "y": 77,
                    "width": 380, "height": 620, "visible": True}],
        "wires": [], "docs": [], "story_stops": []
    }
    manifest = {"pages": [{"id": "page_home"}, {"id": "page_courses"}]}
    changed = wf.append_new_pages(state, manifest)
    assert changed is True
    # existing frame untouched
    assert state["frames"][0]["x"] == 99
    assert state["frames"][0]["y"] == 77
    # new frame appended
    ids = [f["id"] for f in state["frames"]]
    assert "page_courses" in ids

def test_append_new_pages_no_change_when_all_present():
    wf = load_script()
    state = {
        "version": 1,
        "frames": [{"id": "page_home", "x": 0, "y": 0,
                    "width": 380, "height": 620, "visible": True}],
        "wires": [], "docs": [], "story_stops": []
    }
    manifest = {"pages": [{"id": "page_home"}]}
    changed = wf.append_new_pages(state, manifest)
    assert changed is False
    assert len(state["frames"]) == 1
```

- [ ] **Step 2: Run to confirm failure**

```
pytest tests/test_ui_preview.py::test_append_new_pages_preserves_existing_positions -v
```

- [ ] **Step 3: Implement**

```python
def append_new_pages(state: dict, manifest: dict) -> bool:
    existing = {f["id"] for f in state["frames"]}
    new_pages = [p for p in manifest["pages"] if p["id"] not in existing]
    if not new_pages:
        return False

    # place new frames to the right of the rightmost existing frame
    if state["frames"]:
        max_right = max(f["x"] + f["width"] for f in state["frames"])
    else:
        max_right = 0
    x = max_right + 120
    y = 0
    for page in new_pages:
        state["frames"].append({
            "id":      page["id"],
            "x":       x,
            "y":       y,
            "width":   380,
            "height":  620,
            "visible": True,
        })
        y += 660
    return True
```

- [ ] **Step 4: Run all tests**

```
pytest tests/test_ui_preview.py -v
```

- [ ] **Step 5: Commit**

```
git add scripts/ui_preview_workflow.py tests/test_ui_preview.py
git commit -m "feat(ui-preview): canvas-state append-new-pages preserves layout"
```

---

## Task 6: File copying + Python integration test

**Files:**
- Modify: `scripts/ui_preview_workflow.py` — complete `main()` with copy + manifest + state write
- Modify: `tests/test_ui_preview.py` — integration test

**Interfaces:**
- Consumes: all functions from Tasks 1–5
- Produces: `ui-preview/` folder with correct structure (tested end-to-end)

- [ ] **Step 1: Write integration test**

```python
import json
from pathlib import Path

def test_full_run_creates_correct_output_structure(tmp_path):
    wf = load_script()
    # build a minimal prototype setup
    proto = tmp_path / "ui-prototypes"
    proto.mkdir()
    (proto / "index.html").write_text(
        '<html><body><a href="courses.html">Go</a></body></html>'
    )
    (proto / "courses.html").write_text(
        '<html><body><a href="index.html">Back</a></body></html>'
    )

    spec_dir = tmp_path / "specs"
    spec_dir.mkdir()
    (spec_dir / "spec.md").write_text("# Spec")

    page_map_data = {"pages": [
        {"slug": "index",   "title": "Home",    "group": "Public", "direction": "rtl"},
        {"slug": "courses", "title": "Courses", "group": "Public", "direction": "rtl"},
    ]}
    pm = tmp_path / "page-map.json"
    pm.write_text(json.dumps(page_map_data))

    out = tmp_path / "ui-preview"

    # call run() directly (we'll refactor main into run())
    wf.run(
        prototype_dir=str(proto),
        spec_dir=str(spec_dir),
        output_dir=str(out),
        page_map=str(pm),
        project="TestProject"
    )

    assert (out / "manifest.json").exists()
    assert (out / "canvas-state.json").exists()
    assert (out / "index.html").exists()
    assert (out / "pages" / "index.html").exists()
    assert (out / "pages" / "courses.html").exists()
    assert (out / "docs" / "spec.md").exists()

    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["project"] == "TestProject"
    assert len(manifest["nav_wires"]) >= 2  # index↔courses both directions
    assert manifest["pages"][0]["id"] == "page_index"

    state = json.loads((out / "canvas-state.json").read_text())
    assert state["version"] == 1
    assert len(state["frames"]) == 2

def test_rerun_preserves_canvas_positions(tmp_path):
    wf = load_script()
    # first run setup (reuse above structure)
    proto = tmp_path / "ui-prototypes"
    proto.mkdir()
    (proto / "index.html").write_text('<html><body></body></html>')
    spec_dir = tmp_path / "specs"; spec_dir.mkdir()
    pm_data = {"pages": [{"slug": "index", "title": "Home", "group": "G", "direction": "ltr"}]}
    pm = tmp_path / "pm.json"; pm.write_text(json.dumps(pm_data))
    out = tmp_path / "ui-preview"

    wf.run(str(proto), str(spec_dir), str(out), str(pm), "P")

    # manually move a frame
    state_path = out / "canvas-state.json"
    state = json.loads(state_path.read_text())
    state["frames"][0]["x"] = 999
    state_path.write_text(json.dumps(state))

    # add a new page
    (proto / "courses.html").write_text('<html><body></body></html>')
    pm_data["pages"].append({"slug": "courses", "title": "Courses", "group": "G", "direction": "ltr"})
    pm.write_text(json.dumps(pm_data))

    wf.run(str(proto), str(spec_dir), str(out), str(pm), "P")

    state2 = json.loads(state_path.read_text())
    frames = {f["id"]: f for f in state2["frames"]}
    assert frames["page_index"]["x"] == 999   # preserved
    assert "page_courses" in frames           # new page appended
```

- [ ] **Step 2: Run to confirm failure**

```
pytest tests/test_ui_preview.py::test_full_run_creates_correct_output_structure -v
```
Expected: `AttributeError: module ... has no attribute 'run'`

- [ ] **Step 3: Implement `run()` and wire up `main()`**

```python
def run(prototype_dir: str, spec_dir: str, output_dir: str,
        page_map: str, project: str) -> None:
    proto  = Path(prototype_dir)
    specs  = Path(spec_dir)
    out    = Path(output_dir)

    # 1. Load page map
    pages = load_page_map(page_map)
    slug_to_id = {p["slug"]: p["id"] for p in pages}

    # 2. Verify HTML files exist
    for p in pages:
        src = proto / f"{p['slug']}.html"
        if not src.exists():
            print(f"  [warn] missing prototype: {src}", file=sys.stderr)

    # 3. Collect doc files
    doc_files = sorted(specs.glob("*.md")) if specs.exists() else []
    docs = [{"id": doc_id(f.stem), "title": f.stem.replace("-", " ").title(),
             "file": f"docs/{f.name}"} for f in doc_files]

    # 4. Copy pages
    pages_out = out / "pages"
    pages_out.mkdir(parents=True, exist_ok=True)
    for p in pages:
        src = proto / f"{p['slug']}.html"
        if src.exists():
            shutil.copy2(src, pages_out / f"{p['slug']}.html")

    # 5. Copy docs
    docs_out = out / "docs"
    docs_out.mkdir(parents=True, exist_ok=True)
    for f in doc_files:
        shutil.copy2(f, docs_out / f.name)

    # 6. Scan nav wires
    nav_wires = []
    for p in pages:
        html_path = pages_out / f"{p['slug']}.html"
        if html_path.exists():
            html = html_path.read_text(encoding="utf-8", errors="ignore")
            nav_wires.extend(scan_nav_wires(p["id"], html, slug_to_id))

    # 7. Write manifest (always)
    manifest = build_manifest(project, pages, docs, nav_wires)
    (out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 8/9. Write or update canvas-state.json
    state_path = out / "canvas-state.json"
    if not state_path.exists():
        state = generate_default_layout(pages)
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    else:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if append_new_pages(state, manifest):
            state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    # 10. Generate index.html (placeholder until Task 18)
    _write_index_html(out, project)

    print(f"[ui-into-preview] {out}/ ready. Push to GitHub and enable Pages.")


def _write_index_html(out: Path, project: str) -> None:
    """Placeholder — replaced in Task 18 with full inline assembly."""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>{project} — UI Preview</title></head>
<body><p>Canvas coming in Task 18. Open manifest.json to verify output.</p></body>
</html>"""
    (out / "index.html").write_text(html, encoding="utf-8")


def main():
    args = parse_args()
    run(
        prototype_dir=args.prototype_dir,
        spec_dir=args.spec_dir,
        output_dir=args.output_dir,
        page_map=args.page_map,
        project=args.project,
    )
```

- [ ] **Step 4: Run all tests**

```
pytest tests/test_ui_preview.py -v
```
Expected: all pass

- [ ] **Step 5: Commit**

```
git add scripts/ui_preview_workflow.py tests/test_ui_preview.py
git commit -m "feat(ui-preview): complete Python generator — copy, manifest, state"
```

---

## Task 7: Markdown parser (JS pure function)

**Files:**
- Create: `canvas-app/markdown-parser.js`
- Create: `tests/test_markdown_parser.js`

**Interfaces:**
- Produces: global `function parseMarkdown(md: string): string`

- [ ] **Step 1: Create test file**

```js
// tests/test_markdown_parser.js
// Run with: node tests/test_markdown_parser.js
const fs = require('fs')
eval(fs.readFileSync('canvas-app/markdown-parser.js', 'utf8'))

let passed = 0, failed = 0
function assert(label, actual, expected) {
  if (actual === expected) { console.log('  ✓', label); passed++ }
  else { console.error('  ✗', label, '\n    got:', actual, '\n    exp:', expected); failed++ }
}
function includes(label, actual, fragment) {
  if (actual.includes(fragment)) { console.log('  ✓', label); passed++ }
  else { console.error('  ✗', label, '\n    missing:', fragment, '\n    in:', actual); failed++ }
}

includes('h1', parseMarkdown('# Hello'), '<h1>Hello</h1>')
includes('h2', parseMarkdown('## World'), '<h2>World</h2>')
includes('bold', parseMarkdown('**bold**'), '<strong>bold</strong>')
includes('italic', parseMarkdown('*italic*'), '<em>italic</em>')
includes('inline code', parseMarkdown('`code`'), '<code>code</code>')
includes('unordered list', parseMarkdown('- item one'), '<li>item one</li>')
includes('link', parseMarkdown('[text](url)'), '<a href="url">text</a>')
includes('code block open', parseMarkdown('```\nfoo\n```'), '<pre><code>')
includes('paragraph', parseMarkdown('plain text'), '<p>plain text</p>')

console.log(`\n${passed} passed, ${failed} failed`)
if (failed) process.exit(1)
```

- [ ] **Step 2: Run to confirm failure**

```
node tests/test_markdown_parser.js
```
Expected: `ReferenceError: parseMarkdown is not defined`

- [ ] **Step 3: Implement parser**

```js
// canvas-app/markdown-parser.js
function parseMarkdown(md) {
  const lines = md.split('\n')
  const html = []
  let inCode = false, inList = false

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i]

    if (line.startsWith('```')) {
      if (!inCode) { if (inList) { html.push('</ul>'); inList = false } html.push('<pre><code>'); inCode = true }
      else          { html.push('</code></pre>'); inCode = false }
      continue
    }
    if (inCode) { html.push(escHtml(line)); continue }

    if (line.startsWith('# '))      { if (inList) { html.push('</ul>'); inList = false } html.push(`<h1>${inline(line.slice(2))}</h1>`); continue }
    if (line.startsWith('## '))     { if (inList) { html.push('</ul>'); inList = false } html.push(`<h2>${inline(line.slice(3))}</h2>`); continue }
    if (line.startsWith('### '))    { if (inList) { html.push('</ul>'); inList = false } html.push(`<h3>${inline(line.slice(4))}</h3>`); continue }
    if (line.startsWith('#### '))   { if (inList) { html.push('</ul>'); inList = false } html.push(`<h4>${inline(line.slice(5))}</h4>`); continue }
    if (line.startsWith('- ') || line.startsWith('* ')) {
      if (!inList) { html.push('<ul>'); inList = true }
      html.push(`<li>${inline(line.slice(2))}</li>`)
      continue
    }
    if (inList) { html.push('</ul>'); inList = false }
    if (line.trim() === '') { html.push('<br>'); continue }
    html.push(`<p>${inline(line)}</p>`)
  }
  if (inList) html.push('</ul>')
  if (inCode) html.push('</code></pre>')
  return html.join('\n')
}

function inline(text) {
  return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
}
```

- [ ] **Step 4: Run tests — expect pass**

```
node tests/test_markdown_parser.js
```
Expected: all 9 tests pass

- [ ] **Step 5: Commit**

```
git add canvas-app/markdown-parser.js tests/test_markdown_parser.js
git commit -m "feat(ui-preview): vanilla markdown parser — headers, bold, lists, code, links"
```

---

## Task 8: State manager (JS)

**Files:**
- Create: `canvas-app/state-manager.js`
- Create: `tests/test_state_manager.js`

**Interfaces:**
- Produces: global `StateManager` object with methods listed below
- Consumes: nothing (no deps)

- [ ] **Step 1: Create test file**

```js
// tests/test_state_manager.js
// Run with: node tests/test_state_manager.js
const fs = require('fs')
// provide browser stubs
global.document = { addEventListener: () => {} }
global.fetch = () => {}
eval(fs.readFileSync('canvas-app/state-manager.js', 'utf8'))

let passed = 0, failed = 0
function ok(label, cond) {
  if (cond) { console.log('  ✓', label); passed++ }
  else { console.error('  ✗', label); failed++ }
}

// migrateState: add version + story_stops to old file
const old = { frames: [], wires: [], docs: [] }
const migrated = StateManager.migrateState(old)
ok('migration adds version=1', migrated.version === 1)
ok('migration adds story_stops', Array.isArray(migrated.story_stops))

// generateDefaultLayout from manifest
const manifest = { pages: [{ id: 'page_a', group: 'G' }], docs: [] }
const layout = StateManager.generateDefaultLayout(manifest)
ok('default layout has frames', layout.frames.length === 1)
ok('default layout version', layout.version === 1)

// updateFramePosition
StateManager.state = { frames: [{ id: 'page_a', x: 0, y: 0, width: 380, height: 620, visible: true }], wires: [], docs: [], story_stops: [] }
StateManager.updateFramePosition('page_a', 55, 77)
ok('updateFramePosition x', StateManager.state.frames[0].x === 55)
ok('updateFramePosition y', StateManager.state.frames[0].y === 77)

// setFrameVisible
StateManager.setFrameVisible('page_a', false)
ok('setFrameVisible false', StateManager.state.frames[0].visible === false)

console.log(`\n${passed} passed, ${failed} failed`)
if (failed) process.exit(1)
```

- [ ] **Step 2: Run to confirm failure**

```
node tests/test_state_manager.js
```

- [ ] **Step 3: Implement**

```js
// canvas-app/state-manager.js
const StateManager = (() => {
  let _state = null

  function migrateState(s) {
    if (!s.version || s.version < 1) {
      s.version     = 1
      s.story_stops = s.story_stops ?? []
      s.docs        = s.docs        ?? []
      s.wires       = s.wires       ?? []
    }
    return s
  }

  function generateDefaultLayout(manifest) {
    const FRAME_W = 380, FRAME_H = 620, GAP_Y = 40, GAP_X = 120
    const groups = {}, order = []
    for (const p of manifest.pages) {
      const g = p.group ?? 'Other'
      if (!groups[g]) { groups[g] = []; order.push(g) }
      groups[g].push(p)
    }
    const frames = []
    let colX = 0
    for (const g of order) {
      let y = 0
      for (const p of groups[g]) {
        frames.push({ id: p.id, x: colX, y, width: FRAME_W, height: FRAME_H, visible: true })
        y += FRAME_H + GAP_Y
      }
      colX += FRAME_W + GAP_X
    }
    return { version: 1, frames, wires: [], docs: [], story_stops: [] }
  }

  function getState() { return _state }

  function updateFramePosition(id, x, y) {
    const f = _state.frames.find(f => f.id === id)
    if (f) { f.x = x; f.y = y }
  }

  function setFrameVisible(id, visible) {
    const f = _state.frames.find(f => f.id === id)
    if (f) f.visible = visible
  }

  function addFlowWire(wire) { _state.wires.push(wire) }

  function removeWire(id) {
    _state.wires = _state.wires.filter(w => w.id !== id)
  }

  function addDocCard(doc) {
    if (!_state.docs.find(d => d.id === doc.id)) _state.docs.push(doc)
  }

  function updateDocPosition(id, x, y) {
    const d = _state.docs.find(d => d.id === id)
    if (d) { d.x = x; d.y = y }
  }

  function addStoryStop(stop) { _state.story_stops.push(stop) }

  function removeStoryStop(id) {
    _state.story_stops = _state.story_stops.filter(s => s.id !== id)
  }

  function saveDownload() {
    const blob = new Blob([JSON.stringify(_state, null, 2)], { type: 'application/json' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = 'canvas-state.json'
    a.click()
    URL.revokeObjectURL(a.href)
  }

  function applyImported(raw) {
    _state = migrateState(raw)
    document.dispatchEvent(new CustomEvent('state:loaded', { detail: _state }))
  }

  document.addEventListener('dragover', e => e.preventDefault())
  document.addEventListener('drop', e => {
    const file = e.dataTransfer?.files?.[0]
    if (!file?.name.endsWith('.json')) return
    file.text().then(t => applyImported(JSON.parse(t)))
  })

  return {
    get state() { return _state },
    set state(v) { _state = v },
    migrateState, generateDefaultLayout, getState,
    updateFramePosition, setFrameVisible,
    addFlowWire, removeWire,
    addDocCard, updateDocPosition,
    addStoryStop, removeStoryStop,
    saveDownload, applyImported,
  }
})()
```

- [ ] **Step 4: Run tests — expect pass**

```
node tests/test_state_manager.js
```

- [ ] **Step 5: Commit**

```
git add canvas-app/state-manager.js tests/test_state_manager.js
git commit -m "feat(ui-preview): state manager — load, save, migrate, drag-drop import"
```

---

## Task 9: Canvas CSS + HTML shell

**Files:**
- Create: `canvas-app/canvas.css`
- Create: `canvas-app/index.template.html`

**Interfaces:**
- Produces: HTML shell with toolbar, layers panel, canvas container, minimap area, presentation bar
- Produces: CSS with all layout, frame card styles, interaction blocker

- [ ] **Step 1: Create `canvas.css`**

```css
/* canvas-app/canvas.css */
:root {
  --toolbar-h: 48px;
  --layers-w: 220px;
  --bg: #111827;
  --surface: #1f2937;
  --border: #374151;
  --text: #f3f4f6;
  --text-muted: #9ca3af;
  --accent: #3b82f6;
  --accent-hover: #2563eb;
  --frame-radius: 8px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  display: grid;
  grid-template:
    "toolbar  toolbar" var(--toolbar-h)
    "layers   canvas " 1fr
    / var(--layers-w) 1fr;
  height: 100dvh;
  overflow: hidden;
  background: var(--bg);
  color: var(--text);
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 13px;
}

/* Toolbar */
#toolbar {
  grid-area: toolbar;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0 12px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  user-select: none;
}
.tool-sep { width: 1px; height: 24px; background: var(--border); margin: 0 6px; }
.tool-btn {
  padding: 5px 10px;
  border: 1px solid var(--border);
  border-radius: 5px;
  background: transparent;
  color: var(--text);
  cursor: pointer;
  font-size: 12px;
  transition: background 0.1s;
}
.tool-btn:hover  { background: var(--border); }
.tool-btn.active { background: var(--accent); border-color: var(--accent); }
.tool-btn.primary { background: var(--accent); border-color: var(--accent); }
.tool-btn.primary:hover { background: var(--accent-hover); }
#zoom-display { font-size: 12px; color: var(--text-muted); min-width: 38px; text-align: center; }

/* Layers panel */
#layers-panel {
  grid-area: layers;
  overflow-y: auto;
  background: var(--surface);
  border-right: 1px solid var(--border);
  padding: 6px 0;
}
.layer-group-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px;
  cursor: pointer;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  font-size: 10px;
  letter-spacing: 0.05em;
}
.layer-group-header:hover { background: rgba(255,255,255,0.04); }
.layer-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px 4px 22px;
  cursor: pointer;
  border-radius: 4px;
  margin: 1px 4px;
}
.layer-item:hover { background: rgba(255,255,255,0.06); }
.layer-item.active { background: rgba(59,130,246,0.2); }
.eye-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  padding: 0 2px;
  font-size: 14px;
  line-height: 1;
  flex-shrink: 0;
}
.eye-btn:hover { color: var(--text); }

/* Canvas container */
#canvas-container {
  grid-area: canvas;
  position: relative;
  overflow: hidden;
  background: var(--bg);
  background-image: radial-gradient(circle, #374151 1px, transparent 1px);
  background-size: 24px 24px;
  cursor: default;
}
#canvas-viewport {
  position: absolute;
  top: 0;
  left: 0;
  transform-origin: 0 0;
  will-change: transform;
}
#wires-svg {
  position: absolute;
  top: 0; left: 0;
  pointer-events: none;
  overflow: visible;
}

/* Frame cards */
.frame-card {
  position: absolute;
  display: flex;
  flex-direction: column;
  border: 2px solid var(--border);
  border-radius: var(--frame-radius);
  background: #fff;
  box-shadow: 0 4px 24px rgba(0,0,0,0.5);
  overflow: hidden;
  transition: box-shadow 0.15s;
}
.frame-card:hover { box-shadow: 0 6px 32px rgba(0,0,0,0.6); }
.frame-card.focused { border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent); }
.frame-title-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 8px;
  background: var(--surface);
  cursor: grab;
  user-select: none;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.frame-title-bar:active { cursor: grabbing; }
.frame-title { font-size: 12px; font-weight: 500; color: var(--text); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.frame-group-badge { font-size: 10px; padding: 1px 5px; border-radius: 3px; background: var(--border); color: var(--text-muted); }
.frame-close { background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 14px; padding: 0 2px; line-height: 1; flex-shrink: 0; }
.frame-close:hover { color: #ef4444; }
.frame-body { position: relative; flex: 1; overflow: hidden; }
.frame-body iframe { width: 100%; height: 100%; border: none; display: block; }
.interaction-blocker {
  position: absolute;
  inset: 0;
  z-index: 10;
  cursor: default;
}
.frame-card.preview-mode .interaction-blocker { display: none; }
.preview-toggle {
  flex-shrink: 0;
  font-size: 11px;
  padding: 3px 8px;
  background: var(--surface);
  border: none;
  border-top: 1px solid var(--border);
  color: var(--text-muted);
  cursor: pointer;
  text-align: left;
}
.preview-toggle:hover { background: var(--accent); color: #fff; }

/* Minimap */
#minimap-container {
  position: absolute;
  bottom: 16px;
  right: 16px;
  z-index: 50;
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  background: rgba(17,24,39,0.9);
  backdrop-filter: blur(4px);
}
#minimap-canvas { display: block; }

/* Presentation bar */
#presentation-bar {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(0,0,0,0.85);
  backdrop-filter: blur(8px);
  padding: 10px 24px;
  border-radius: 40px;
  z-index: 200;
  color: #fff;
  font-size: 14px;
}
.stop-nav-btn {
  background: none;
  border: 1px solid rgba(255,255,255,0.3);
  color: #fff;
  border-radius: 50%;
  width: 32px; height: 32px;
  cursor: pointer;
  font-size: 16px;
  display: flex; align-items: center; justify-content: center;
}
.stop-nav-btn:hover { background: rgba(255,255,255,0.15); }

/* Doc cards */
.doc-card {
  position: absolute;
  width: 400px;
  min-height: 200px;
  max-height: 500px;
  background: #fff;
  border: 2px solid var(--border);
  border-radius: var(--frame-radius);
  box-shadow: 0 4px 24px rgba(0,0,0,0.4);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.doc-card-title-bar {
  display: flex;
  align-items: center;
  padding: 5px 8px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  cursor: grab;
  user-select: none;
}
.doc-card-title-bar:active { cursor: grabbing; }
.doc-card-title { font-size: 12px; font-weight: 500; color: var(--text); flex: 1; }
.doc-card-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px 14px;
  font-size: 13px;
  line-height: 1.6;
  color: #1f2937;
}
.doc-card-body h1,.doc-card-body h2,.doc-card-body h3 { margin: 0.8em 0 0.3em; font-weight: 600; }
.doc-card-body p { margin: 0.4em 0; }
.doc-card-body code { background: #f3f4f6; padding: 1px 4px; border-radius: 3px; font-size: 12px; }
.doc-card-body pre { background: #f3f4f6; padding: 10px; border-radius: 4px; overflow-x: auto; }
.doc-card-body ul { padding-left: 18px; }
.doc-card-body a { color: #3b82f6; }
.doc-resize-handle {
  position: absolute;
  bottom: 0; right: 0;
  width: 12px; height: 12px;
  cursor: se-resize;
}

/* Presentation mode overrides */
body.presenting #toolbar,
body.presenting #layers-panel,
body.presenting #minimap-container { display: none; }
body.presenting {
  grid-template:
    "canvas" 1fr
    / 1fr;
}
body.presenting #canvas-container { grid-area: canvas; }
```

- [ ] **Step 2: Create `index.template.html`**

```html
<!-- canvas-app/index.template.html -->
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{PROJECT}} — UI Preview</title>
<style>
{{CSS}}
</style>
</head>
<body>
<div id="toolbar">
  <div class="tool-group">
    <button id="tool-select" class="tool-btn active" title="Select [V]">Select</button>
    <button id="tool-pan"    class="tool-btn"        title="Pan [H]">Pan</button>
    <button id="tool-wire"   class="tool-btn"        title="Wire [W]">Wire</button>
  </div>
  <div class="tool-sep"></div>
  <button id="tool-add-doc" class="tool-btn" title="Add documentation card">+ Doc</button>
  <div class="tool-sep"></div>
  <button id="toggle-nav-wires" class="tool-btn" title="Toggle nav wires">Nav Wires</button>
  <div class="tool-sep"></div>
  <span id="zoom-display">100%</span>
  <button id="zoom-in"  class="tool-btn" title="Zoom in [+]">+</button>
  <button id="zoom-out" class="tool-btn" title="Zoom out [−]">−</button>
  <div class="tool-sep"></div>
  <button id="add-stop-btn" class="tool-btn" title="Add story stop">+ Stop</button>
  <button id="present-btn"  class="tool-btn" title="Presentation mode [F5]">▶ Present</button>
  <button id="save-btn"     class="tool-btn primary" title="Save layout">Save</button>
</div>
<div id="layers-panel">
  <div id="layers-content"></div>
</div>
<div id="canvas-container">
  <div id="canvas-viewport">
    <svg id="wires-svg" width="0" height="0">
      <defs>
        <marker id="arrow-flow" markerWidth="8" markerHeight="6"
                refX="7" refY="3" orient="auto">
          <path d="M0,0 L8,3 L0,6 Z" fill="#3b82f6"/>
        </marker>
        <marker id="arrow-nav" markerWidth="6" markerHeight="5"
                refX="5" refY="2.5" orient="auto">
          <path d="M0,0 L6,2.5 L0,5 Z" fill="#94a3b8"/>
        </marker>
      </defs>
    </svg>
  </div>
</div>
<canvas id="minimap-canvas" width="180" height="140"></canvas>
<div id="minimap-container"></div>
<div id="presentation-bar" hidden>
  <button class="stop-nav-btn" id="prev-stop">‹</button>
  <span id="stop-label"></span>
  <span id="stop-counter" style="color:#9ca3af; font-size:12px"></span>
  <button class="stop-nav-btn" id="next-stop">›</button>
</div>
<script>
const MANIFEST_URL = './manifest.json'
const STATE_URL    = './canvas-state.json'
{{JS}}
</script>
</body>
</html>
```

- [ ] **Step 3: Visual verification — open in browser**

Open `canvas-app/index.template.html` directly in a browser (substitute `{{CSS}}` → empty, `{{JS}}` → empty for manual check).

Acceptance criteria:
- Body is dark (`#111827`)
- Toolbar visible at top (48px height)
- Left panel area visible (220px width)
- Canvas area fills remaining space

- [ ] **Step 4: Commit**

```
git add canvas-app/canvas.css canvas-app/index.template.html
git commit -m "feat(ui-preview): canvas CSS layout and HTML shell template"
```

---

## Task 10: Canvas core — infinite pan + zoom

**Files:**
- Create: `canvas-app/canvas-core.js`

**Interfaces:**
- Produces: global `CanvasCore` with `zoom(delta,ox,oy)`, `pan(dx,dy)`, `screenToCanvas(sx,sy)`, `canvasToScreen(cx,cy)`, `fitAll(frames)`, `animateTo(x,y,zoom)`, `getTransform()`
- Note: `animateTo` returns a Promise that resolves after 300ms CSS transition

- [ ] **Step 1: Create `canvas-core.js`**

```js
// canvas-app/canvas-core.js
const CanvasCore = (() => {
  let tx = 0, ty = 0, scale = 1
  const MIN_ZOOM = 0.1, MAX_ZOOM = 3.0
  let _container, _viewport, _zoomDisplay

  function init() {
    _container   = document.getElementById('canvas-container')
    _viewport    = document.getElementById('canvas-viewport')
    _zoomDisplay = document.getElementById('zoom-display')
    _bindEvents()
  }

  function applyTransform(animate = false) {
    if (animate) {
      _viewport.style.transition = 'transform 300ms ease-in-out'
      setTimeout(() => { _viewport.style.transition = '' }, 320)
    }
    _viewport.style.transform = `translate(${tx}px,${ty}px) scale(${scale})`
    if (_zoomDisplay) _zoomDisplay.textContent = `${Math.round(scale * 100)}%`
    document.dispatchEvent(new CustomEvent('canvas:transformed'))
  }

  function zoom(delta, originX, originY) {
    const newScale = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, scale * (1 + delta)))
    tx = originX - (originX - tx) * (newScale / scale)
    ty = originY - (originY - ty) * (newScale / scale)
    scale = newScale
    applyTransform()
  }

  function pan(dx, dy) { tx += dx; ty += dy; applyTransform() }

  function screenToCanvas(sx, sy) {
    return { x: (sx - tx) / scale, y: (sy - ty) / scale }
  }

  function canvasToScreen(cx, cy) {
    return { x: cx * scale + tx, y: cy * scale + ty }
  }

  function fitAll(frames) {
    if (!frames || !frames.length) return
    const vis = frames.filter(f => f.visible !== false)
    if (!vis.length) return
    const minX = Math.min(...vis.map(f => f.x))
    const minY = Math.min(...vis.map(f => f.y))
    const maxX = Math.max(...vis.map(f => f.x + f.width))
    const maxY = Math.max(...vis.map(f => f.y + f.height))
    const pad = 60
    const cw = _container.clientWidth
    const ch = _container.clientHeight
    scale = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM,
      Math.min((cw - pad*2) / (maxX - minX), (ch - pad*2) / (maxY - minY))
    ))
    tx = pad - minX * scale + (cw - (maxX - minX) * scale) / 2
    ty = pad - minY * scale + (ch - (maxY - minY) * scale) / 2
    applyTransform()
  }

  function animateTo(x, y, z) {
    tx = x; ty = y; scale = z
    applyTransform(true)
    return new Promise(r => setTimeout(r, 320))
  }

  function getTransform() { return { tx, ty, scale } }

  function _bindEvents() {
    let panning = false, startX = 0, startY = 0
    _container.addEventListener('mousedown', e => {
      if (e.target !== _container && e.target !== _viewport) return
      if (e.button !== 0) return
      panning = true; startX = e.clientX; startY = e.clientY
      _container.style.cursor = 'grabbing'
    })
    window.addEventListener('mousemove', e => {
      if (!panning) return
      pan(e.clientX - startX, e.clientY - startY)
      startX = e.clientX; startY = e.clientY
    })
    window.addEventListener('mouseup', () => {
      panning = false; _container.style.cursor = ''
    })
    _container.addEventListener('wheel', e => {
      e.preventDefault()
      const r = _container.getBoundingClientRect()
      zoom(-e.deltaY * 0.001, e.clientX - r.left, e.clientY - r.top)
    }, { passive: false })
    document.addEventListener('keydown', e => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return
      if (e.key === '=' || e.key === '+') zoom(0.1, _container.clientWidth/2, _container.clientHeight/2)
      if (e.key === '-') zoom(-0.1, _container.clientWidth/2, _container.clientHeight/2)
      if ((e.ctrlKey||e.metaKey) && e.key === '0') { e.preventDefault(); fitAll(StateManager.state?.frames) }
    })
    document.getElementById('zoom-in')?.addEventListener('click',  () => zoom(0.1, _container.clientWidth/2, _container.clientHeight/2))
    document.getElementById('zoom-out')?.addEventListener('click', () => zoom(-0.1, _container.clientWidth/2, _container.clientHeight/2))
  }

  return { init, zoom, pan, screenToCanvas, canvasToScreen, fitAll, animateTo, getTransform, applyTransform }
})()
```

- [ ] **Step 2: Manual browser test**

After Task 18 integration, open `ui-preview/index.html`. Acceptance criteria:
- Scroll wheel zooms toward cursor
- Drag on background pans the canvas
- `+` / `−` keys zoom; `Ctrl+0` fits all frames
- Zoom display shows correct percentage (10%–300%)

- [ ] **Step 3: Commit**

```
git add canvas-app/canvas-core.js
git commit -m "feat(ui-preview): infinite canvas core — pan, zoom, fit-all, animate-to"
```

---

## Task 11: Frame cards + interaction blocker + drag reposition

**Files:**
- Create: `canvas-app/frame-manager.js`

**Interfaces:**
- Consumes: `CanvasCore.screenToCanvas()`, `CanvasCore.canvasToScreen()`, `CanvasCore.getTransform()`, `StateManager.updateFramePosition()`, `StateManager.setFrameVisible()`
- Produces: global `FrameManager` with `init(manifest,state)`, `createFrame(page,frameState)`, `focusFrame(id)`, `setVisible(id,v)`, `getAllBounds()` (returns array of `{id,x,y,w,h}` in canvas coords)

- [ ] **Step 1: Create `frame-manager.js`**

```js
// canvas-app/frame-manager.js
const FrameManager = (() => {
  const _frames = new Map()  // id → {el, page, state}
  let _viewport, _container
  let _wireRefresh = null   // set by Wiring after init

  function init(manifest, state) {
    _viewport  = document.getElementById('canvas-viewport')
    _container = document.getElementById('canvas-container')
    const stateMap = Object.fromEntries(state.frames.map(f => [f.id, f]))
    for (const page of manifest.pages) {
      const fs = stateMap[page.id]
      if (!fs) continue
      const el = createFrame(page, fs)
      _viewport.appendChild(el)
      _frames.set(page.id, { el, page, state: fs })
    }
    _container.addEventListener('click', e => {
      if (e.target === _container || e.target === _viewport) _clearFocus()
    })
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') _clearFocus()
    })
  }

  function createFrame(page, fs) {
    const el = document.createElement('div')
    el.className = 'frame-card'
    el.dataset.id = page.id
    if (!fs.visible) el.style.display = 'none'
    el.style.transform = `translate(${fs.x}px,${fs.y}px)`
    el.style.width  = fs.width  + 'px'
    el.style.height = fs.height + 'px'

    el.innerHTML = `
      <div class="frame-title-bar">
        <span class="frame-title">${page.title}</span>
        <span class="frame-group-badge">${page.group}</span>
        <button class="frame-close" title="Hide">×</button>
      </div>
      <div class="frame-body">
        <iframe src="${page.file}" loading="lazy" title="${page.title}"></iframe>
        <div class="interaction-blocker"></div>
      </div>
      <button class="preview-toggle">Preview Mode</button>`

    el.querySelector('.frame-close').addEventListener('click', e => {
      e.stopPropagation()
      setVisible(page.id, false)
    })
    el.querySelector('.preview-toggle').addEventListener('click', e => {
      e.stopPropagation()
      el.classList.toggle('preview-mode')
      e.target.textContent = el.classList.contains('preview-mode') ? 'Exit Preview' : 'Preview Mode'
    })
    el.addEventListener('dblclick', e => {
      if (e.target.classList.contains('frame-title-bar') || e.target.closest('.frame-title-bar'))
        return
      focusFrame(page.id)
    })

    _bindDrag(el, page.id, fs)
    return el
  }

  function _bindDrag(el, id, fs) {
    const titleBar = el.querySelector('.frame-title-bar')
    let dragging = false, startMX, startMY, startFX, startFY

    titleBar.addEventListener('mousedown', e => {
      if (e.button !== 0) return
      e.stopPropagation()
      dragging = true
      startMX = e.clientX; startMY = e.clientY
      startFX = fs.x; startFY = fs.y
      window.addEventListener('mousemove', onMove)
      window.addEventListener('mouseup', onUp)
    })

    function onMove(e) {
      if (!dragging) return
      const { scale } = CanvasCore.getTransform()
      const dx = (e.clientX - startMX) / scale
      const dy = (e.clientY - startMY) / scale
      fs.x = startFX + dx
      fs.y = startFY + dy
      el.style.transform = `translate(${fs.x}px,${fs.y}px)`
      StateManager.updateFramePosition(id, fs.x, fs.y)
      if (_wireRefresh) _wireRefresh()
    }

    function onUp() {
      dragging = false
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
    }
  }

  function focusFrame(id) {
    _clearFocus()
    const entry = _frames.get(id)
    if (!entry) return
    entry.el.classList.add('focused')
    const fs = entry.state
    const cont = document.getElementById('canvas-container')
    const padX = 80, padY = 80
    const { scale: newScale } = CanvasCore.getTransform()
    const zoom = Math.min(3, Math.max(0.2,
      Math.min((cont.clientWidth  - padX*2) / fs.width,
               (cont.clientHeight - padY*2) / fs.height)
    ))
    const tx = padX - fs.x * zoom + (cont.clientWidth  - fs.width  * zoom) / 2
    const ty = padY - fs.y * zoom + (cont.clientHeight - fs.height * zoom) / 2
    CanvasCore.animateTo(tx, ty, zoom)
  }

  function _clearFocus() {
    _frames.forEach(e => e.el.classList.remove('focused'))
  }

  function setVisible(id, visible) {
    const entry = _frames.get(id)
    if (!entry) return
    entry.state.visible = visible
    entry.el.style.display = visible ? '' : 'none'
    StateManager.setFrameVisible(id, visible)
    document.dispatchEvent(new CustomEvent('layers:refresh'))
  }

  function getAllBounds() {
    return Array.from(_frames.values())
      .filter(e => e.state.visible !== false)
      .map(e => ({ id: e.page.id, x: e.state.x, y: e.state.y, w: e.state.width, h: e.state.height }))
  }

  function setWireRefreshCallback(fn) { _wireRefresh = fn }

  return { init, createFrame, focusFrame, setVisible, getAllBounds, setWireRefreshCallback }
})()
```

- [ ] **Step 2: Manual acceptance criteria**

After Task 18 integration, open `ui-preview/index.html`:
- All 26 pages appear as floating cards
- Dragging the title bar repositions the frame (wires follow — after Task 14/15)
- Clicking `×` hides the frame
- "Preview Mode" button makes links in the iframe clickable; clicking again re-enables blocker
- Double-clicking a frame animates canvas to fill it edge-to-edge

- [ ] **Step 3: Commit**

```
git add canvas-app/frame-manager.js
git commit -m "feat(ui-preview): frame cards — iframe, blocker overlay, drag, focus"
```

---

## Task 12: Layers panel

**Files:**
- Create: `canvas-app/layers-panel.js`

**Interfaces:**
- Consumes: `FrameManager.setVisible()`, `FrameManager.focusFrame()`, `StateManager.getState()`
- Produces: global `LayersPanel` with `init(manifest,state)`, `refresh()`

- [ ] **Step 1: Create `layers-panel.js`**

```js
// canvas-app/layers-panel.js
const LayersPanel = (() => {
  let _manifest, _state, _el

  function init(manifest, state) {
    _manifest = manifest; _state = state
    _el = document.getElementById('layers-content')
    render()
    document.addEventListener('layers:refresh', render)
  }

  function render() {
    if (!_el) return
    _el.innerHTML = ''
    _renderGroup('Pages', _manifest.pages, 'frame')
    _renderGroup('Flow Wires', _state.wires, 'wire')
    _renderGroup('Docs', _state.docs, 'doc')
  }

  function _renderGroup(label, items, type) {
    if (!items.length) return
    const vis = items.filter(i => i.visible !== false).length
    const header = document.createElement('div')
    header.className = 'layer-group-header'
    header.innerHTML = `<span>▾</span><span>${label}</span><span style="margin-left:auto;font-size:10px;font-weight:400">${vis}/${items.length}</span>`
    _el.appendChild(header)

    const list = document.createElement('div')
    for (const item of items) {
      const row = document.createElement('div')
      row.className = 'layer-item'
      const isVisible = item.visible !== false
      const label = item.title ?? item.label ?? item.id
      row.innerHTML = `<button class="eye-btn" title="Toggle visibility">${isVisible ? '👁' : '⊘'}</button><span>${label}</span>`
      row.querySelector('.eye-btn').addEventListener('click', e => {
        e.stopPropagation()
        const newVis = item.visible === false
        if (type === 'frame') FrameManager.setVisible(item.id, newVis)
        else { item.visible = newVis; render() }
      })
      row.addEventListener('click', () => {
        if (type === 'frame') FrameManager.focusFrame(item.id)
      })
      list.appendChild(row)
    }
    _el.appendChild(list)
  }

  function refresh() { render() }

  return { init, refresh }
})()
```

- [ ] **Step 2: Manual acceptance criteria**

- Pages/Wires/Docs groups show in left panel
- Eye icon toggles visibility; frame disappears from canvas
- Clicking a page name animates canvas to that frame

- [ ] **Step 3: Commit**

```
git add canvas-app/layers-panel.js
git commit -m "feat(ui-preview): layers panel — groups, visibility toggle, click to focus"
```

---

## Task 13: Minimap

**Files:**
- Create: `canvas-app/minimap.js`

**Interfaces:**
- Consumes: `FrameManager.getAllBounds()`, `CanvasCore.getTransform()`, `CanvasCore.animateTo()`
- Produces: global `Minimap` with `init()`, `render()`

- [ ] **Step 1: Create `minimap.js`**

```js
// canvas-app/minimap.js
const Minimap = (() => {
  const W = 180, H = 140
  let _canvas, _ctx, _container, _canvasContainer

  function init() {
    _container      = document.getElementById('minimap-container')
    _canvasContainer = document.getElementById('canvas-container')
    _canvas = document.createElement('canvas')
    _canvas.width = W; _canvas.height = H
    _canvas.style.display = 'block'
    _container.appendChild(_canvas)
    _ctx = _canvas.getContext('2d')
    document.addEventListener('canvas:transformed', render)
    _canvas.addEventListener('click', _onClick)
  }

  function render() {
    if (!_ctx) return
    const bounds = FrameManager.getAllBounds()
    if (!bounds.length) return
    _ctx.clearRect(0, 0, W, H)

    const minX = Math.min(...bounds.map(b => b.x))
    const minY = Math.min(...bounds.map(b => b.y))
    const maxX = Math.max(...bounds.map(b => b.x + b.w))
    const maxY = Math.max(...bounds.map(b => b.y + b.h))
    const pad = 8
    const scaleX = (W - pad*2) / (maxX - minX || 1)
    const scaleY = (H - pad*2) / (maxY - minY || 1)
    const s = Math.min(scaleX, scaleY)

    // store for click mapping
    _canvas._minX = minX; _canvas._minY = minY; _canvas._s = s; _canvas._pad = pad

    // draw frames
    _ctx.fillStyle = '#3b82f6'
    for (const b of bounds) {
      _ctx.fillRect(
        pad + (b.x - minX) * s,
        pad + (b.y - minY) * s,
        Math.max(2, b.w * s),
        Math.max(2, b.h * s)
      )
    }

    // draw viewport
    const { tx, ty, scale } = CanvasCore.getTransform()
    const cw = _canvasContainer.clientWidth
    const ch = _canvasContainer.clientHeight
    const vx1 = (-tx / scale - minX) * s + pad
    const vy1 = (-ty / scale - minY) * s + pad
    const vw  = (cw / scale) * s
    const vh  = (ch / scale) * s
    _ctx.strokeStyle = '#fbbf24'
    _ctx.lineWidth = 1.5
    _ctx.strokeRect(vx1, vy1, vw, vh)
  }

  function _onClick(e) {
    const r = _canvas.getBoundingClientRect()
    const mx = e.clientX - r.left, my = e.clientY - r.top
    const { _minX, _minY, _s, _pad } = _canvas
    if (_s === undefined) return
    const { scale } = CanvasCore.getTransform()
    const cx = (mx - _pad) / _s + _minX
    const cy = (my - _pad) / _s + _minY
    const cw = _canvasContainer.clientWidth
    const ch = _canvasContainer.clientHeight
    CanvasCore.animateTo(-cx * scale + cw/2, -cy * scale + ch/2, scale)
  }

  return { init, render }
})()
```

- [ ] **Step 2: Manual acceptance criteria**

- Minimap shows blue rectangles for all visible frames
- Yellow rectangle shows current viewport
- Clicking minimap jumps canvas view to that region

- [ ] **Step 3: Commit**

```
git add canvas-app/minimap.js
git commit -m "feat(ui-preview): minimap — frame thumbnails, viewport indicator, click navigation"
```

---

## Task 14: Nav wire rendering (SVG from manifest)

**Files:**
- Create: `canvas-app/wiring.js` (nav wire portion only)

**Interfaces:**
- Consumes: `FrameManager.getAllBounds()`, manifest `nav_wires`, `StateManager.state.wires`
- Produces: global `Wiring` with `init(manifest,state)`, `renderAll()`, `setNavWiresVisible(v)`, `updatePositions()`

- [ ] **Step 1: Create `wiring.js` with nav wire support**

```js
// canvas-app/wiring.js
const Wiring = (() => {
  let _svg, _manifest, _state, _navVisible = false
  const FLOW_COLORS = ['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6','#ec4899']
  let _colorIndex = 0

  function init(manifest, state) {
    _manifest = manifest; _state = state
    _svg = document.getElementById('wires-svg')
    FrameManager.setWireRefreshCallback(updatePositions)
    renderAll()
    document.getElementById('toggle-nav-wires')?.addEventListener('click', e => {
      _navVisible = !_navVisible
      e.target.classList.toggle('active', _navVisible)
      renderAll()
    })
  }

  function renderAll() {
    // remove all existing wire paths (keep defs)
    _svg.querySelectorAll('.wire-path, .wire-label').forEach(e => e.remove())
    if (_navVisible) _renderNavWires()
    _renderFlowWires()
    _resizeSVG()
  }

  function _renderNavWires() {
    for (const w of _manifest.nav_wires ?? []) {
      _drawWire(w.from, w.to, '', '#94a3b8', 1.5, true, 'arrow-nav')
    }
  }

  function _renderFlowWires() {
    for (const w of _state.wires) {
      if (w.visible === false) continue
      _drawWire(w.from, w.to, w.label ?? '', w.color ?? '#3b82f6', 2.5, false, 'arrow-flow', w.id)
    }
  }

  function _drawWire(fromId, toId, label, color, width, dashed, markerId, wireId) {
    const from = _centerOf(fromId), to = _centerOf(toId)
    if (!from || !to) return

    const dx = to.x - from.x
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
    path.classList.add('wire-path')
    if (wireId) path.dataset.wireId = wireId
    const cp = Math.abs(dx) * 0.5 + 80
    path.setAttribute('d', `M${from.x},${from.y} C${from.x+cp},${from.y} ${to.x-cp},${to.y} ${to.x},${to.y}`)
    path.setAttribute('stroke', color)
    path.setAttribute('stroke-width', width)
    path.setAttribute('fill', 'none')
    path.setAttribute('marker-end', `url(#${markerId})`)
    if (dashed) path.setAttribute('stroke-dasharray', '5 3')
    _svg.appendChild(path)

    if (label) {
      const mx = (from.x + to.x) / 2, my = (from.y + to.y) / 2
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g')
      g.classList.add('wire-label')
      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect')
      rect.setAttribute('x', mx - label.length * 3 - 6)
      rect.setAttribute('y', my - 10)
      rect.setAttribute('width', label.length * 6 + 12)
      rect.setAttribute('height', 18)
      rect.setAttribute('rx', 4)
      rect.setAttribute('fill', color)
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text')
      text.setAttribute('x', mx); text.setAttribute('y', my + 4)
      text.setAttribute('text-anchor', 'middle')
      text.setAttribute('fill', '#fff')
      text.setAttribute('font-size', '10')
      text.textContent = label
      g.appendChild(rect); g.appendChild(text)
      _svg.appendChild(g)
    }
  }

  function _centerOf(id) {
    const bounds = FrameManager.getAllBounds().find(b => b.id === id)
    if (!bounds) return null
    return { x: bounds.x + bounds.w / 2, y: bounds.y + bounds.h / 2 }
  }

  function _resizeSVG() {
    const bounds = FrameManager.getAllBounds()
    if (!bounds.length) return
    const maxX = Math.max(...bounds.map(b => b.x + b.w)) + 200
    const maxY = Math.max(...bounds.map(b => b.y + b.h)) + 200
    _svg.setAttribute('width', maxX); _svg.setAttribute('height', maxY)
  }

  function updatePositions() { renderAll() }

  function setNavWiresVisible(v) { _navVisible = v; renderAll() }

  function nextColor() {
    const c = FLOW_COLORS[_colorIndex % FLOW_COLORS.length]
    _colorIndex++
    return c
  }

  return { init, renderAll, setNavWiresVisible, updatePositions, nextColor }
})()
```

- [ ] **Step 2: Manual acceptance criteria**

- "Nav Wires" button is off by default — no nav wires visible
- Clicking "Nav Wires" shows thin grey dashed bezier curves between connected pages
- Clicking again hides them
- Wires connect page centers with cubic bezier curves

- [ ] **Step 3: Commit**

```
git add canvas-app/wiring.js
git commit -m "feat(ui-preview): SVG nav wire rendering from manifest — toggle on/off"
```

---

## Task 15: Flow wire drawing (Wire mode)

**Files:**
- Modify: `canvas-app/wiring.js` — add `enterWireMode()`, `exitWireMode()`, `addFlowWire()`

- [ ] **Step 1: Add Wire mode to `wiring.js`**

Add these functions inside the `Wiring` IIFE, before the `return`:

```js
  let _wireMode = false, _wireSource = null

  function enterWireMode() {
    _wireMode = true
    _wireSource = null
    document.getElementById('canvas-container').style.cursor = 'crosshair'
    document.dispatchEvent(new CustomEvent('wire:mode-on'))
    // clicking a frame sets source; clicking another frame completes the wire
    document.addEventListener('click', _onWireClick)
  }

  function exitWireMode() {
    _wireMode = false
    _wireSource = null
    document.getElementById('canvas-container').style.cursor = ''
    document.removeEventListener('click', _onWireClick)
    document.dispatchEvent(new CustomEvent('wire:mode-off'))
  }

  function _onWireClick(e) {
    const card = e.target.closest('.frame-card')
    if (!card) return
    const id = card.dataset.id
    if (!_wireSource) {
      _wireSource = id
      card.style.outline = '2px solid #3b82f6'
    } else {
      if (id === _wireSource) { card.style.outline = ''; _wireSource = null; return }
      const label = prompt('Wire label (optional):') ?? ''
      card.style.outline = ''
      document.querySelector(`[data-id="${_wireSource}"]`).style.outline = ''
      addFlowWire(_wireSource, id, label)
      exitWireMode()
      document.getElementById('tool-wire')?.classList.remove('active')
      document.getElementById('tool-select')?.classList.add('active')
    }
  }

  function addFlowWire(fromId, toId, label) {
    const wire = {
      id:      'wire_' + Math.random().toString(16).slice(2, 8),
      from:    fromId,
      to:      toId,
      label:   label,
      type:    'flow',
      color:   nextColor(),
      visible: true,
    }
    StateManager.addFlowWire(wire)
    renderAll()
    LayersPanel.refresh()
  }
```

Update `return` to include: `enterWireMode, exitWireMode, addFlowWire`

- [ ] **Step 2: Wire toolbar buttons in `app.js` (add to app.js step in Task 20)**

The toolbar wiring is handled in `app.js`. Note the interface here:
```js
document.getElementById('tool-wire').addEventListener('click', () => {
  Wiring.enterWireMode()
  // set active state on wire button, remove from others
})
```

- [ ] **Step 3: Manual acceptance criteria**

- Click "Wire" button — cursor becomes crosshair
- Click a source frame (outline appears)
- Click a destination frame — label prompt appears
- Wire is drawn as bold colored bezier with label pill at midpoint
- Wire appears in Layers panel under "Flow Wires"
- Dragging either frame re-routes the wire

- [ ] **Step 4: Commit**

```
git add canvas-app/wiring.js
git commit -m "feat(ui-preview): manual flow wire drawing — click source, click target, label"
```

---

## Task 16: Markdown doc cards

**Files:**
- Create: `canvas-app/doc-cards.js`

**Interfaces:**
- Consumes: `parseMarkdown()`, `CanvasCore.screenToCanvas()`, `StateManager.addDocCard()`, `StateManager.updateDocPosition()`
- Produces: global `DocCards` with `init(manifest,state)`, `addCard(docId)`, `renderAll()`

- [ ] **Step 1: Create `doc-cards.js`**

```js
// canvas-app/doc-cards.js
const DocCards = (() => {
  let _manifest, _state, _viewport
  const _cards = new Map()  // docId → {el, docState}

  function init(manifest, state) {
    _manifest = manifest; _state = state
    _viewport = document.getElementById('canvas-viewport')
    renderAll()
    _setupToolbar()
  }

  function renderAll() {
    for (const docState of _state.docs) {
      if (!_cards.has(docState.id)) _createCard(docState)
    }
  }

  function addCard(docId) {
    const existing = _state.docs.find(d => d.id === docId)
    if (existing) { FrameManager.focusFrame && _scrollToDoc(docId); return }
    const { tx, ty, scale } = CanvasCore.getTransform()
    const cont = document.getElementById('canvas-container')
    const docState = { id: docId, x: -tx/scale + cont.clientWidth/(scale*2), y: -ty/scale + 40, width: 400, visible: true }
    StateManager.addDocCard(docState)
    _createCard(docState)
    LayersPanel.refresh()
  }

  function _createCard(docState) {
    const docMeta = _manifest.docs.find(d => d.id === docState.id)
    if (!docMeta) return
    const el = document.createElement('div')
    el.className = 'doc-card'
    el.dataset.docId = docState.id
    el.style.transform = `translate(${docState.x}px,${docState.y}px)`
    el.style.width = (docState.width || 400) + 'px'
    el.innerHTML = `
      <div class="doc-card-title-bar">
        <span class="doc-card-title">📄 ${docMeta.title}</span>
        <button class="frame-close" style="color:#9ca3af">×</button>
      </div>
      <div class="doc-card-body">Loading…</div>`

    el.querySelector('.frame-close').addEventListener('click', () => {
      el.remove(); _cards.delete(docState.id)
      _state.docs = _state.docs.filter(d => d.id !== docState.id)
      LayersPanel.refresh()
    })

    _bindDocDrag(el, docState)
    _viewport.appendChild(el)
    _cards.set(docState.id, { el, docState })

    // fetch and render markdown
    fetch(docMeta.file).then(r => r.text()).then(md => {
      el.querySelector('.doc-card-body').innerHTML = parseMarkdown(md)
    }).catch(() => {
      el.querySelector('.doc-card-body').textContent = 'Could not load ' + docMeta.file
    })
  }

  function _bindDocDrag(el, docState) {
    const titleBar = el.querySelector('.doc-card-title-bar')
    let dragging = false, startMX, startMY, startX, startY
    titleBar.addEventListener('mousedown', e => {
      if (e.button !== 0) return
      e.stopPropagation()
      dragging = true
      startMX = e.clientX; startMY = e.clientY
      startX = docState.x; startY = docState.y
      window.addEventListener('mousemove', onMove)
      window.addEventListener('mouseup', onUp)
    })
    function onMove(e) {
      if (!dragging) return
      const { scale } = CanvasCore.getTransform()
      docState.x = startX + (e.clientX - startMX) / scale
      docState.y = startY + (e.clientY - startMY) / scale
      el.style.transform = `translate(${docState.x}px,${docState.y}px)`
      StateManager.updateDocPosition(docState.id, docState.x, docState.y)
    }
    function onUp() { dragging = false; window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp) }
  }

  function _setupToolbar() {
    const btn = document.getElementById('tool-add-doc')
    if (!btn) return
    btn.addEventListener('click', () => {
      if (!_manifest.docs.length) { alert('No docs found in ui-preview/docs/'); return }
      const opts = _manifest.docs.map((d,i) => `${i+1}. ${d.title}`).join('\n')
      const input = prompt('Add doc card:\n' + opts + '\n\nEnter number:')
      if (!input) return
      const idx = parseInt(input) - 1
      if (idx >= 0 && idx < _manifest.docs.length) addCard(_manifest.docs[idx].id)
    })
  }

  return { init, addCard, renderAll }
})()
```

- [ ] **Step 2: Manual acceptance criteria**

- Click "+ Doc" → prompt shows list of docs
- Enter number → a card appears on canvas with rendered markdown content
- Card is draggable by title bar
- Clicking `×` removes the card
- Markdown renders headers, bold, lists, code correctly

- [ ] **Step 3: Commit**

```
git add canvas-app/doc-cards.js
git commit -m "feat(ui-preview): markdown doc cards — add from toolbar, drag, render, remove"
```

---

## Task 17: Presentation mode + story stops

**Files:**
- Create: `canvas-app/presentation.js`

**Interfaces:**
- Consumes: `CanvasCore.animateTo()`, `CanvasCore.getTransform()`, `StateManager.addStoryStop()`, `StateManager.state.story_stops`
- Produces: global `Presentation` with `init()`, `enter()`, `exit()`, `addStop()`, `goTo(i)`

- [ ] **Step 1: Create `presentation.js`**

```js
// canvas-app/presentation.js
const Presentation = (() => {
  let _active = false, _current = 0

  function init() {
    document.getElementById('present-btn')?.addEventListener('click', enter)
    document.getElementById('add-stop-btn')?.addEventListener('click', addStop)
    document.getElementById('prev-stop')?.addEventListener('click', prev)
    document.getElementById('next-stop')?.addEventListener('click', next)
    document.addEventListener('keydown', e => {
      if (_active && e.key === 'ArrowRight') next()
      if (_active && e.key === 'ArrowLeft')  prev()
      if (_active && e.key === 'Escape')     exit()
      if (!_active && e.key === 'F5') { e.preventDefault(); enter() }
    })
  }

  function enter() {
    const stops = StateManager.state.story_stops
    if (!stops.length) { alert('No story stops yet.\n\nArrange the canvas view and click "+ Stop" to add one.'); return }
    _active = true
    _current = 0
    document.body.classList.add('presenting')
    document.getElementById('presentation-bar').hidden = false
    document.documentElement.requestFullscreen?.().catch(() => {})
    _showStop(_current)
  }

  function exit() {
    _active = false
    document.body.classList.remove('presenting')
    document.getElementById('presentation-bar').hidden = true
    document.exitFullscreen?.().catch(() => {})
  }

  function addStop() {
    const { tx, ty, scale } = CanvasCore.getTransform()
    const label = prompt('Story stop label:')
    if (!label) return
    const stop = {
      id:       'stop_' + Math.random().toString(16).slice(2, 8),
      label,
      viewport: { x: tx, y: ty, zoom: scale }
    }
    StateManager.addStoryStop(stop)
    LayersPanel.refresh()
  }

  function goTo(i) {
    const stops = StateManager.state.story_stops
    if (!stops.length) return
    _current = Math.max(0, Math.min(stops.length - 1, i))
    _showStop(_current)
  }

  function _showStop(i) {
    const stops = StateManager.state.story_stops
    if (!stops[i]) return
    const s = stops[i]
    CanvasCore.animateTo(s.viewport.x, s.viewport.y, s.viewport.zoom)
    document.getElementById('stop-label').textContent   = s.label
    document.getElementById('stop-counter').textContent = `${i+1} / ${stops.length}`
    Wiring.setNavWiresVisible(false)
  }

  function next() { goTo(_current + 1) }
  function prev() { goTo(_current - 1) }

  return { init, enter, exit, addStop, goTo, next, prev }
})()
```

- [ ] **Step 2: Manual acceptance criteria**

- Click "+ Stop" with a canvas view → prompt for label → stop saved
- Click "▶ Present" → fullscreen, toolbar/panel/minimap hidden, nav bar shown
- `←` `→` keys navigate story stops with smooth animated transition
- Stop counter shows `2 / 4` style indicator
- `Esc` exits presentation mode and returns to normal canvas

- [ ] **Step 3: Commit**

```
git add canvas-app/presentation.js
git commit -m "feat(ui-preview): presentation mode — fullscreen, story stop navigation"
```

---

## Task 18: Python script — inline canvas app into `index.html`

**Files:**
- Modify: `scripts/ui_preview_workflow.py` — replace `_write_index_html()` with full inline assembly
- Create: `canvas-app/app.js` — entry point

**Interfaces:**
- Consumes: all `canvas-app/` files (read by Python, inlined)
- Produces: fully self-contained `ui-preview/index.html` with zero external refs

- [ ] **Step 1: Create `app.js`**

```js
// canvas-app/app.js
async function main() {
  const [manifest, rawState] = await Promise.all([
    fetch(MANIFEST_URL).then(r => r.json()),
    fetch(STATE_URL).then(r => r.json()).catch(() => null)
  ])

  const state = StateManager.migrateState(
    rawState ?? StateManager.generateDefaultLayout(manifest)
  )
  StateManager.state = state

  CanvasCore.init()
  FrameManager.init(manifest, state)
  LayersPanel.init(manifest, state)
  Wiring.init(manifest, state)
  DocCards.init(manifest, state)
  Minimap.init()
  Presentation.init()

  // Toolbar mode buttons
  const modes = ['select','pan','wire']
  modes.forEach(m => {
    document.getElementById(`tool-${m}`)?.addEventListener('click', () => {
      modes.forEach(x => document.getElementById(`tool-${x}`)?.classList.remove('active'))
      document.getElementById(`tool-${m}`)?.classList.add('active')
      if (m === 'wire') Wiring.enterWireMode()
      else Wiring.exitWireMode?.()
    })
  })

  document.getElementById('save-btn')?.addEventListener('click', () => StateManager.saveDownload())

  // Fit all frames on load
  setTimeout(() => CanvasCore.fitAll(state.frames), 100)

  // GitHub Pages onboarding banner (dismiss after first view)
  if (!localStorage.getItem('ui-preview:onboarded')) {
    const banner = document.createElement('div')
    banner.style.cssText = 'position:fixed;top:56px;left:50%;transform:translateX(-50%);background:#1e40af;color:#fff;padding:10px 20px;border-radius:6px;font-size:12px;z-index:999;cursor:pointer;'
    banner.textContent = '💡 Push ui-preview/ to GitHub → Settings → Pages → /ui-preview folder. Click to dismiss.'
    banner.addEventListener('click', () => { banner.remove(); localStorage.setItem('ui-preview:onboarded','1') })
    document.body.appendChild(banner)
  }
}

main().catch(console.error)
```

- [ ] **Step 2: Replace `_write_index_html()` in Python script**

```python
# In scripts/ui_preview_workflow.py
# replace the entire _write_index_html function with:

def _write_index_html(out: Path, project: str) -> None:
    skill_dir = Path(__file__).parent.parent  # ui-gernreate-from-plan/
    app_dir   = skill_dir / "canvas-app"

    template = (app_dir / "index.template.html").read_text(encoding="utf-8")
    css_text  = (app_dir / "canvas.css").read_text(encoding="utf-8")

    # inline JS modules in dependency order
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
        "app.js",
    ]
    js_parts = []
    for name in js_modules:
        js_path = app_dir / name
        if js_path.exists():
            js_parts.append(f"/* --- {name} --- */\n" + js_path.read_text(encoding="utf-8"))
        else:
            print(f"  [warn] missing canvas-app/{name}", file=sys.stderr)
    js_text = "\n\n".join(js_parts)

    html = template.replace("{{PROJECT}}", project) \
                   .replace("{{CSS}}", css_text) \
                   .replace("{{JS}}", js_text)

    (out / "index.html").write_text(html, encoding="utf-8")
    print(f"  [ok] index.html — {len(html):,} bytes")
```

- [ ] **Step 3: Write integration test for self-containment**

```python
def test_index_html_has_no_external_refs(tmp_path):
    """index.html must have no <link>, no <script src>, no CDN refs."""
    wf = load_script()
    proto = tmp_path / "p"; proto.mkdir()
    (proto / "index.html").write_text('<html><body></body></html>')
    specs = tmp_path / "s"; specs.mkdir()
    pm_data = {"pages":[{"slug":"index","title":"Home","group":"G","direction":"ltr"}]}
    pm = tmp_path/"pm.json"; pm.write_text(json.dumps(pm_data))
    out = tmp_path / "out"

    wf.run(str(proto), str(specs), str(out), str(pm), "Test")

    html = (out / "index.html").read_text()
    assert '<link ' not in html.lower(), "Found <link> external ref"
    assert 'script src=' not in html.lower(), "Found <script src> external ref"
    assert 'cdn.' not in html.lower(), "Found CDN reference"
    assert 'parseMarkdown' in html, "markdown-parser.js not inlined"
    assert 'StateManager' in html, "state-manager.js not inlined"
    assert 'CanvasCore' in html, "canvas-core.js not inlined"
```

- [ ] **Step 4: Run tests**

```
pytest tests/test_ui_preview.py::test_index_html_has_no_external_refs -v
```
Expected: PASS

- [ ] **Step 5: Full end-to-end run against the EdTech project**

```
python ui-gernreate-from-plan/scripts/ui_preview_workflow.py \
  --prototype-dir ui-prototypes \
  --spec-dir specs/001-edtech-marketing-crm \
  --output-dir ui-preview \
  --page-map .ui-bridge/page-map.json \
  --project "EdTech Platform"
```

Then open `ui-preview/index.html` in a browser (requires a local server since it uses `fetch`):
```
cd ui-preview && python -m http.server 8080
```
Open `http://localhost:8080`. Verify:
- All 26 pages appear as floating frames
- Drag a frame — it repositions
- Scroll wheel zooms
- "Nav Wires" toggle works
- "Wire" mode draws flow wires
- "+ Stop" adds story stops; "Present" enters fullscreen presentation

- [ ] **Step 6: Commit**

```
git add canvas-app/app.js scripts/ui_preview_workflow.py tests/test_ui_preview.py
git commit -m "feat(ui-preview): inline assembly — fully self-contained index.html"
```

---

## Task 19: Subskill SKILL.md

**Files:**
- Create: `subskills/ui-preview/SKILL.md`

- [ ] **Step 1: Create the subskill file**

```markdown
# Subskill: ui-into-preview

**Command**: `/ui-into-preview`
**Parent skill**: `../../SKILL.md` (ui-bridge)
**Previous command**: `/ui-link-html-to-plan`
**Next command**: `/speckit-implement`

---

## When to Use

Activate for any of these: "ui-into-preview", "preview the UI", "show pages to
client", "build the canvas", "generate preview", "deploy to GitHub Pages",
"create presentation", or any request to show/share/present HTML prototypes to
a client or stakeholder.

---

## Pre-Flight Checklist

Before running, verify:

- [ ] `[PROTOTYPE_DIR]/*.html` files exist (generated by `/ui-implement`)
- [ ] `.ui-bridge/page-map.json` exists
- [ ] Spec folder with at least one `.md` file exists

---

## How to Run

```bash
python [SKILL_DIR]/scripts/ui_preview_workflow.py \
  --prototype-dir [PROTOTYPE_DIR] \
  --spec-dir      [SPEC_DIR] \
  --output-dir    ui-preview \
  --page-map      .ui-bridge/page-map.json \
  --project       "[PROJECT_NAME]"
```

Replace:
- `[SKILL_DIR]` — path to `ui-gernreate-from-plan/` (e.g. `ui-gernreate-from-plan`)
- `[PROTOTYPE_DIR]` — folder with HTML prototypes (e.g. `ui-prototypes`)
- `[SPEC_DIR]` — folder with spec `.md` files (e.g. `specs/001-my-feature`)
- `[PROJECT_NAME]` — shown in the canvas title bar

---

## Output

```
ui-preview/
├── index.html          ← Open in browser or deploy to GitHub Pages
├── manifest.json       ← Page registry + auto nav wires (always fresh)
├── canvas-state.json   ← Designer layout (never overwritten by re-run)
├── pages/              ← Copies of HTML prototypes
└── docs/               ← Copies of spec .md files
```

---

## GitHub Pages Deployment

1. Commit and push `ui-preview/` to GitHub
2. Go to repo Settings → Pages → Source: `main` branch, `/ui-preview` folder
3. Wait ~60 seconds
4. Share `https://[username].github.io/[repo-name]/`

---

## Saving Layout Changes

After arranging frames on the canvas:
1. Click **Save** → downloads `canvas-state.json`
2. Replace `ui-preview/canvas-state.json` in the repo with the downloaded file
3. Commit and push → the live GitHub Pages URL shows the updated layout

Re-running the command after adding new prototype pages preserves all existing
frame positions and only appends the new pages.

---

## Presentation Mode

1. Arrange the canvas to a view you want to present → click **+ Stop** → type a label
2. Repeat for each view in your client narrative
3. Click **▶ Present** (or press `F5`) → fullscreen opens
4. Use `←` `→` arrow keys to navigate story stops
5. Press `Esc` to exit

---

## Re-run Safety

- `manifest.json` — always regenerated (nav wires stay fresh)
- `canvas-state.json` — **never** regenerated if it exists; new pages are appended
- `index.html` — always regenerated (canvas app code updates)
- `pages/*.html` and `docs/*.md` — always copied fresh from source
```

- [ ] **Step 2: Commit**

```
git add subskills/ui-preview/SKILL.md
git commit -m "feat(ui-preview): subskill SKILL.md — command docs and GitHub Pages guide"
```

---

## Task 20: Update main `SKILL.md` + final commit

**Files:**
- Modify: `SKILL.md` — add `/ui-into-preview` to command table + workflow diagram

- [ ] **Step 1: Read the current SKILL.md command table section**

Open `SKILL.md` and locate the `| Command | Subskill file | When to use |` table.

- [ ] **Step 2: Add the new row**

```markdown
| `/ui-into-preview` | `subskills/ui-preview/SKILL.md` | After `/ui-link` — generate GitHub Pages canvas presentation from HTML prototypes |
```

- [ ] **Step 3: Update the workflow diagram**

Find the workflow code block and add the new step:

```
/ui-link-html-to-plan
        ↓
/ui-into-preview       ← canvas presentation tool, GitHub Pages deploy
        ↓
/speckit-implement
```

- [ ] **Step 4: Run all tests one final time**

```
pytest tests/test_ui_preview.py -v
node tests/test_markdown_parser.js
node tests/test_state_manager.js
```
Expected: all pass

- [ ] **Step 5: Final commit**

```
git add SKILL.md
git commit -m "feat(ui-preview): register /ui-into-preview in main SKILL.md workflow"
```

---

## Self-Review

**Spec coverage check:**

| Spec Section | Covered by Task(s) |
|---|---|
| Output structure (manifest, state, pages, docs) | T2, T5, T6 |
| manifest.json schema + nav_wires in manifest | T2, T3 |
| canvas-state.json schema + versioning | T5, T8 |
| Interaction blocker overlay (not JS injection) | T11 |
| Preview Mode toggle | T11 |
| Layers panel | T12 |
| Minimap | T13 |
| Nav wires from manifest, toggleable | T14 |
| Flow wire drawing (Wire mode) | T15 |
| Markdown doc cards | T7, T16 |
| Presentation mode + Story Stops | T17 |
| Auto layout grouped by role | T4 |
| State persistence: export download + drag-drop | T8 |
| canvas-state.json never overwritten | T5, T6 |
| New pages appended on re-run | T5, T6 |
| GitHub Pages deployable (self-contained HTML) | T18 |
| Python CLI + full run | T1, T6 |
| Subskill SKILL.md | T19 |
| Main SKILL.md updated | T20 |

All spec sections covered. No gaps found.
