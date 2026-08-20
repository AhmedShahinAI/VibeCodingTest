import subprocess, sys
import importlib.util, json
from pathlib import Path

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
    # Second Public page is below first (480 height + 40 gap)
    assert frames["page_courses"]["y"] == 520
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
    assert state["frames"][0]["height"] == 480
    assert state["frames"][0]["visible"] is True

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
    assert len(manifest["nav_wires"]) >= 2  # index<->courses both directions
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
    spec_dir = tmp_path / "specs"
    spec_dir.mkdir()
    pm_data = {"pages": [{"slug": "index", "title": "Home", "group": "G", "direction": "ltr"}]}
    pm = tmp_path / "pm.json"
    pm.write_text(json.dumps(pm_data))
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

    html = (out / "index.html").read_text(encoding="utf-8")
    assert '<link ' not in html.lower(), "Found <link> external ref"
    assert 'script src=' not in html.lower(), "Found <script src> external ref"
    assert 'cdn.' not in html.lower(), "Found CDN reference"
    assert 'parseMarkdown' in html, "markdown-parser.js not inlined"
    assert 'StateManager' in html, "state-manager.js not inlined"
    assert 'CanvasCore' in html, "canvas-core.js not inlined"
