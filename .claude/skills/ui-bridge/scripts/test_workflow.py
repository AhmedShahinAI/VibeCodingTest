"""
Focused regression tests for the executable brand-led workflow.
Uses temporary projects so no client repo artifacts are modified.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent


def run(cmd, cwd, expect=0):
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if proc.returncode != expect:
        raise AssertionError(
            "Command failed: %s\nexpected=%s actual=%s\nstdout=%s\nstderr=%s"
            % (" ".join(cmd), expect, proc.returncode, proc.stdout, proc.stderr)
        )
    return proc


def write_project(root: Path) -> None:
    spec_dir = root / "specs" / "001-demo"
    spec_dir.mkdir(parents=True)
    (spec_dir / "plan.md").write_text(
        "# Implementation Plan: Demo\n\n## Phase 1: Setup\n\n## Phase 2 - Build\n",
        encoding="utf-8",
    )
    (spec_dir / "tasks.md").write_text(
        "# Tasks\n\n## Phase 1: Setup\n\n"
        "- [ ] T001 Create homepage at `apps/web/pages/index.vue`\n"
        "- [ ] T002 Create admin dashboard at `apps/web/pages/admin/index.vue`\n",
        encoding="utf-8",
    )
    (spec_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
    (root / "PRD.md").write_text("Arabic training CRM website.\n", encoding="utf-8")
    styles = root / "src" / "styles"
    styles.mkdir(parents=True)
    (styles / "brand.css").write_text(
        ":root { --brand-primary: #29435C; --font-heading: Madani; --font-body: Nassim; }\n"
        "body { font-family: Madani, Nassim, sans-serif; }\n",
        encoding="utf-8",
    )


def test_parse_and_strict_block() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_project(root)
        proc = run([sys.executable, str(SCRIPT_DIR / "parse_speckit.py"), "--json", "--root", str(root)], root)
        data = json.loads((root / ".ui-bridge" / "parsed-speckit.json").read_text(encoding="utf-8"))
        assert data["plan"]["phases"], "phases should not be empty"

        proc = run(
            [sys.executable, str(SCRIPT_DIR / "extract_brand.py"), "--root", str(root), "--brand-policy", "strict"],
            root,
            expect=1,
        )
        brand = json.loads((root / ".ui-bridge" / "brand-signals.json").read_text(encoding="utf-8"))
        assert brand["state"] == "brand_intake_required"
        sources = json.dumps(brand["raw_signals"])
        assert "ui-gernreate-from-plan" not in sources
        assert ".claude" not in sources


def test_proposal_approval_and_page_map() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_project(root)
        run([sys.executable, str(SCRIPT_DIR / "parse_speckit.py"), "--root", str(root)], root)
        run([sys.executable, str(SCRIPT_DIR / "extract_brand.py"), "--root", str(root), "--brand-policy", "proposal"], root)
        proposals = json.loads(next((root / ".ui-bridge").glob("brand-proposals.v*.json")).read_text(encoding="utf-8"))
        assert len(proposals["directions"]) == 3
        assert proposals["project_type"]["category"] != "unknown"
        proposal_text = json.dumps(proposals)
        assert "Harvard Online" not in proposal_text
        assert "MIT Professional Education" not in proposal_text
        for direction in proposals["directions"]:
            for key in ("palette", "fonts", "references", "photography", "iconography", "density", "personality", "layout_style", "hero_style", "cta_tone", "competitive_basis"):
                assert key in direction
        competitive = json.loads(next((root / ".ui-bridge").glob("competitive-analysis.v*.json")).read_text(encoding="utf-8"))
        assert competitive["patterns_to_copy"]

        run([sys.executable, str(SCRIPT_DIR / "approve_brand.py"), "--root", str(root), "--proposal", "A"], root)
        approvals = json.loads((root / ".ui-bridge" / "approvals.json").read_text(encoding="utf-8"))
        assert approvals["brand_direction"]["approved"] is True

        run([sys.executable, str(SCRIPT_DIR / "generate_page_map.py"), "--root", str(root)], root)
        page_map = json.loads((root / ".ui-bridge" / "page-map.json").read_text(encoding="utf-8"))
        assert len(page_map["pages"]) == 2
        assert "api_data_needed" not in json.dumps(page_map)
        assert "static_content_needed" in json.dumps(page_map)

        run([sys.executable, str(SCRIPT_DIR / "generate_direction_artifacts.py"), "--root", str(root)], root)
        layout = json.loads(next((root / ".ui-bridge").glob("layout-dna.v*.json")).read_text(encoding="utf-8"))
        assert layout["page_assignments"], "layout DNA must include page-level assignments"
        hero = json.loads(next((root / ".ui-bridge").glob("hero-diversity.v*.json")).read_text(encoding="utf-8"))
        narrative = json.loads(next((root / ".ui-bridge").glob("narrative-patterns.v*.json")).read_text(encoding="utf-8"))
        section = json.loads(next((root / ".ui-bridge").glob("section-diversity.v*.json")).read_text(encoding="utf-8"))
        assert hero["assignment_logic"].startswith("page-type aware")
        assert narrative["assignment_logic"].startswith("page-purpose aware")
        assert section["assignment_logic"].startswith("content-structure aware")
        run([sys.executable, str(SCRIPT_DIR / "validate_artifacts.py"), str(next((root / ".ui-bridge").glob("layout-dna.v*.json")))], root)
        run([
            sys.executable,
            str(SCRIPT_DIR / "review_artifacts.py"),
            "--root",
            str(root),
            str(next((root / ".ui-bridge").glob("layout-dna.v*.json"))),
            str(next((root / ".ui-bridge").glob("hero-diversity.v*.json"))),
            str(next((root / ".ui-bridge").glob("narrative-patterns.v*.json"))),
            str(next((root / ".ui-bridge").glob("section-diversity.v*.json"))),
            str(next((root / ".ui-bridge").glob("content-realism.v*.json"))),
        ], root)


def test_no_category_presets() -> None:
    engine = (SCRIPT_DIR / "infer_engine.py").read_text(encoding="utf-8")
    colors = (SCRIPT_DIR / "infer_colors.py").read_text(encoding="utf-8")
    assert "PRESETS = {" not in engine
    assert "COLOR_PALETTES_BY_CATEGORY" not in colors
    assert "--infer', 'preset'" not in engine


def test_reviewer_blocks_arabic_mojibake() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        broken = root / "broken.html"
        broken.write_text(
            '<!DOCTYPE html><html lang="ar" dir="rtl"><body><main>Ù…Ø±ÙƒØ² Ø§Ù„ØªØ¯Ø±ÙŠØ¨</main></body></html>',
            encoding="utf-8",
        )
        run([sys.executable, str(SCRIPT_DIR / "review_artifacts.py"), "--root", str(root), str(broken)], root, expect=1)
        report = json.loads((root / ".ui-bridge" / "reviews" / "review-report.json").read_text(encoding="utf-8"))
        ids = {finding["id"] for finding in report["findings"]}
        assert "mojibake_text" in ids
        assert "missing_arabic_text" in ids

        fixed = root / "fixed.html"
        fixed.write_text(
            '<!DOCTYPE html><html lang="ar" dir="rtl"><body><main>مركز التدريب يقدم برامج عربية واضحة للمشاركين والمدربين.</main></body></html>',
            encoding="utf-8",
        )
        run([sys.executable, str(SCRIPT_DIR / "review_artifacts.py"), "--root", str(root), str(fixed)], root)


def test_workflow_wrappers_and_linking() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_project(root)
        run([
            sys.executable,
            str(SCRIPT_DIR / "ui_plan_workflow.py"),
            "--root",
            str(root),
            "--brand-policy",
            "proposal",
            "--draft",
            "--proposal",
            "A",
        ], root)
        assert (root / ".ui-bridge" / "page-map.json").exists()
        assert list((root / ".ui-bridge").glob("layout-dna.v*.json"))

        run([
            sys.executable,
            str(SCRIPT_DIR / "ui_implement_workflow.py"),
            "--root",
            str(root),
            "--page",
            "index",
            "--draft",
        ], root)
        candidate = root / ".ui-bridge" / "html-stages" / "index" / "08-reviewed-final-candidate.html"
        assert candidate.exists()
        candidate_text = candidate.read_text(encoding="utf-8")
        assert "<section data-section=" not in candidate_text
        assert "data-content-slot" not in candidate_text
        assert "specific Arabic value proposition" not in candidate_text
        assert "course title" not in candidate_text
        assert "class=\"evidence-card\"" not in candidate_text
        assert "border-inline-start" not in candidate_text
        run([sys.executable, str(SCRIPT_DIR / "review_artifacts.py"), "--root", str(root), str(candidate)], root)

        proto_dir = root / "ui-prototypes"
        proto_dir.mkdir()
        (proto_dir / "index.html").write_text(
            "<!DOCTYPE html><html><head><title>Index</title></head><body>"
            "<main id=\"main\"><section id=\"hero\"><h1>Index</h1></section></main>"
            "</body></html>",
            encoding="utf-8",
        )
        run([sys.executable, str(SCRIPT_DIR / "ui_link_workflow.py"), "--root", str(root)], root)
        home_map = json.loads((root / ".ui-bridge" / "task-html-map.json").read_text(encoding="utf-8"))
        assert home_map["total_pages"] == 1
        assert home_map["pages"][0]["slug"] == "index"
        assert home_map["total_matches"] == 0

        (proto_dir / "courses.html").write_text(
            "<!DOCTYPE html><html><head><title>Courses</title></head><body>"
            "<main id=\"courses\"><section id=\"hero\"><h1>Courses</h1></section></main>"
            "</body></html>",
            encoding="utf-8",
        )
        run([sys.executable, str(SCRIPT_DIR / "ui_link_workflow.py"), "--root", str(root)], root)
        all_map = json.loads((root / ".ui-bridge" / "task-html-map.json").read_text(encoding="utf-8"))
        assert all_map["total_pages"] == 2
        assert (root / ".ui-bridge" / "link-report.md").exists()


def main() -> None:
    test_parse_and_strict_block()
    test_proposal_approval_and_page_map()
    test_no_category_presets()
    test_reviewer_blocks_arabic_mojibake()
    test_workflow_wrappers_and_linking()
    print("workflow regression tests passed")


if __name__ == "__main__":
    main()
