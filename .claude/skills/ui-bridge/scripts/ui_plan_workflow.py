"""
Executable $ui-plan workflow wrapper.

This script is intentionally strict: it reads real Spec Kit artifacts, enforces
brand approval, verifies Impeccable, generates page maps/design artifacts, runs
artifact validation/review, and updates Phase 0.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from ui_bridge_core import ensure_bridge, read_json


SCRIPT_DIR = Path(__file__).resolve().parent


def run(args: list[str], root: Path, allow_fail: bool = False) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-u", str(SCRIPT_DIR / args[0])] + args[1:]
    proc = subprocess.run(cmd, cwd=root, text=True, capture_output=True)
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="")
    if proc.returncode and not allow_fail:
        raise SystemExit(proc.returncode)
    return proc


def latest_files(root: Path, names: list[str]) -> list[str]:
    bridge = ensure_bridge(root)
    latest = read_json(bridge / "latest.json", default={}) or {}
    paths = []
    for name in names:
        filename = latest.get(name)
        if filename:
            paths.append(str(bridge / filename))
    return paths


def approvals(root: Path) -> dict:
    return read_json(ensure_bridge(root) / "approvals.json", default={}) or {}


def gate_approved(root: Path, key: str) -> bool:
    item = approvals(root).get(key, {})
    return bool(item.get("approved"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the executable UI planning workflow")
    parser.add_argument("--root", default=".")
    parser.add_argument("--brand-policy", choices=["strict", "proposal", "fallback"], default="strict")
    parser.add_argument("--proposal", default="A")
    parser.add_argument("--draft", action="store_true", help="Generate draft direction artifacts for proposal review")
    parser.add_argument("--page", help="Scope planning artifacts to one page slug, e.g. index or home")
    parser.add_argument("--group", choices=["public", "admin"], help="Scope planning artifacts to public or admin pages")
    parser.add_argument("--max-pages", type=int, help="Limit scoped planning artifacts to N pages")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    run(["parse_speckit.py", "--root", str(root)], root)
    brand_proc = run(
        ["extract_brand.py", "--root", str(root), "--brand-policy", args.brand_policy],
        root,
        allow_fail=args.brand_policy == "strict",
    )
    if brand_proc.returncode:
        if args.brand_policy == "strict":
            print(
                "UI plan stopped: strict brand policy requires an approved brand direction. "
                "Run proposal mode and approve a direction before continuing.",
                file=sys.stderr,
            )
        raise SystemExit(brand_proc.returncode)

    if args.brand_policy == "strict":
        run(["run_detection.py", "--command", "ui-plan", "--brand-policy", "strict", "--root", str(root)], root)
        run(["verify_impeccable.py", "--root", str(root)], root)
        page_map_cmd = ["generate_page_map.py", "--root", str(root)]
        if args.page:
            page_map_cmd += ["--page", args.page]
        if args.group:
            page_map_cmd += ["--group", args.group]
        if args.max_pages:
            page_map_cmd += ["--max-pages", str(args.max_pages)]
        run(page_map_cmd, root)
        direction_gates_ready = gate_approved(root, "moodboard") and gate_approved(root, "visual_layout_dna")
        if not direction_gates_ready:
            run(["generate_direction_artifacts.py", "--root", str(root)], root)
            artifacts = latest_files(root, [
                "moodboard",
                "visual-dna",
                "layout-dna",
                "photography-system",
                "iconography-system",
                "hero-diversity",
                "narrative-patterns",
                "section-diversity",
                "content-realism",
            ])
            run(["validate_artifacts.py", *artifacts], root)
            run(["review_artifacts.py", "--root", str(root), *artifacts], root)
            print(
                "UI plan stopped: approve latest moodboard and visual/layout DNA before design-system generation.",
                file=sys.stderr,
            )
            raise SystemExit(1)

        artifacts = latest_files(root, [
            "moodboard",
            "visual-dna",
            "layout-dna",
            "photography-system",
            "iconography-system",
            "hero-diversity",
            "narrative-patterns",
            "section-diversity",
            "content-realism",
        ])
        run(["validate_artifacts.py", *artifacts], root)
        run(["review_artifacts.py", "--root", str(root), *artifacts], root)
        run(["infer_master.py", "--root", str(root)], root)
        run(["update_plan.py", "--root", str(root)], root)
    elif args.brand_policy == "proposal" and args.draft:
        page_map_cmd = ["generate_page_map.py", "--root", str(root)]
        if args.page:
            page_map_cmd += ["--page", args.page]
        if args.group:
            page_map_cmd += ["--group", args.group]
        if args.max_pages:
            page_map_cmd += ["--max-pages", str(args.max_pages)]
        run(page_map_cmd, root)
        run(["generate_direction_artifacts.py", "--root", str(root), "--draft", "--proposal", args.proposal], root)
        artifacts = latest_files(root, [
            "brand-proposals",
            "moodboard",
            "visual-dna",
            "layout-dna",
            "photography-system",
            "iconography-system",
            "hero-diversity",
            "narrative-patterns",
            "section-diversity",
            "content-realism",
        ])
        run(["validate_artifacts.py", *artifacts], root)
        run(["review_artifacts.py", "--root", str(root), *artifacts], root)


if __name__ == "__main__":
    main()
