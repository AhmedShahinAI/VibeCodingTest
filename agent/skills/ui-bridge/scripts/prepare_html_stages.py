"""
Prepare resumable multi-stage HTML generation state.

This does not generate final HTML by itself; it selects pages, creates stage
folders, and persists run state for agent-driven /ui-implement work.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ui_bridge_core import ensure_bridge, read_json, utc_now, write_json
from ui_bridge_core import ApprovalStore


STAGES = [
    "skeleton",
    "content",
    "layout",
    "styling",
    "interactions",
    "accessibility",
    "anti-slop",
    "reviewers",
]


STAGE_FILENAMES = {
    "skeleton": "01-skeleton.html",
    "content": "02-content.html",
    "layout": "03-layout.html",
    "styling": "04-styling.html",
    "interactions": "05-interactions.html",
    "accessibility": "06-accessibility.html",
    "anti-slop": "07-anti-slop-candidate.html",
    "reviewers": "08-reviewed-final-candidate.html",
}


def select_pages(pages, page=None, group=None, max_pages=None):
    selected = pages
    if page:
        selected = [p for p in selected if p.get("slug") == page]
    if group == "public":
        selected = [p for p in selected if not p.get("is_admin")]
    elif group == "admin":
        selected = [p for p in selected if p.get("is_admin")]
    if max_pages is not None:
        selected = selected[:max_pages]
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare HTML stage state")
    parser.add_argument("--root", default=".")
    parser.add_argument("--page")
    parser.add_argument("--group", choices=["public", "admin"])
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-pages", type=int)
    parser.add_argument("--draft", action="store_true", help="Prepare draft stages without approval gates")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    bridge = ensure_bridge(root)
    stage_root = bridge / "html-stages"
    stage_root.mkdir(exist_ok=True)
    state_path = stage_root / "run-state.json"

    if args.resume and state_path.exists():
        print(state_path.read_text(encoding="utf-8"))
        return

    if not args.draft:
        missing = ApprovalStore(root).require([
            "brand_direction",
            "moodboard",
            "visual_layout_dna",
            "design_system",
        ])
        if missing:
            print(
                "ERROR: approval gate failed before HTML staging. Missing: %s. "
                "Use --draft only for internal, non-client stage prep." % ", ".join(missing),
                file=sys.stderr,
            )
            sys.exit(1)

    page_map = read_json(bridge / "page-map.json", default={})
    pages = page_map.get("pages", [])
    selected = select_pages(pages, page=args.page, group=args.group, max_pages=args.max_pages)
    if not selected:
        print("ERROR: no pages selected for HTML staging.", file=sys.stderr)
        sys.exit(1)

    for page in selected:
        page_dir = stage_root / page["slug"]
        page_dir.mkdir(parents=True, exist_ok=True)
        for stage in STAGES:
            stage_file = page_dir / STAGE_FILENAMES[stage]
            if not stage_file.exists():
                stage_file.write_text(
                    "<!-- %s stage for %s. Agent must complete this stage before final HTML. -->\n"
                    % (stage, page["slug"]),
                    encoding="utf-8",
                )
        write_json(page_dir / "stage-state.json", {
            "slug": page["slug"],
            "html_output": page["html_output"],
            "current_stage": STAGES[0],
            "stages": STAGES,
            "stage_files": STAGE_FILENAMES,
            "completed": [],
            "updated_at": utc_now(),
        })

    state = {
        "generated_at": utc_now(),
        "page": args.page,
        "group": args.group,
        "max_pages": args.max_pages,
        "selected_pages": [p["slug"] for p in selected],
        "stages": STAGES,
        "max_review_fix_rounds": 2,
        "draft": args.draft,
    }
    write_json(state_path, state)
    print("Prepared HTML stage state for %d page(s): %s" % (len(selected), state_path))


if __name__ == "__main__":
    main()
