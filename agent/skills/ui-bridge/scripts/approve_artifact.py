"""
Approve a versioned UI Bridge artifact gate.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from ui_bridge_core import ApprovalStore, ensure_bridge, read_json


GATE_MAP = {
    "moodboard": "moodboard",
    "visual-dna": "visual_layout_dna",
    "layout-dna": "visual_layout_dna",
    "visual-layout-dna": "visual_layout_dna",
    "design-system": "design_system",
    "html-review": "final_html_review",
}


def latest_version(root: Path, artifact: str) -> tuple[str, str]:
    bridge = ensure_bridge(root)
    latest = read_json(bridge / "latest.json", default={}) or {}
    filename = latest.get(artifact)
    if not filename:
        candidates = sorted(bridge.glob("%s.v*.json" % artifact))
        if not candidates:
            raise SystemExit("ERROR: no %s artifact found." % artifact)
        filename = candidates[-1].name
    match = re.search(r"\.v(\d+)\.json$", filename)
    version = "v%s" % match.group(1) if match else "v1"
    return version, filename


def main() -> None:
    parser = argparse.ArgumentParser(description="Approve a workflow artifact")
    parser.add_argument("--root", default=".")
    parser.add_argument("--artifact", required=True, choices=sorted(GATE_MAP))
    parser.add_argument("--approved-by", default="user")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    gate = GATE_MAP[args.artifact]
    if args.artifact == "visual-layout-dna":
        visual_version, visual_file = latest_version(root, "visual-dna")
        layout_version, layout_file = latest_version(root, "layout-dna")
        if visual_version != layout_version:
            raise SystemExit("ERROR: visual-dna and layout-dna latest versions differ.")
        ApprovalStore(root).approve(
            gate,
            visual_version,
            approved_by=args.approved_by,
            extra={"artifacts": [visual_file, layout_file]},
        )
        print("Approved %s + %s (%s) as gate %s" % (visual_file, layout_file, visual_version, gate))
        return

    version, filename = latest_version(root, args.artifact)
    ApprovalStore(root).approve(gate, version, approved_by=args.approved_by, extra={"artifact": filename})
    print("Approved %s (%s) as gate %s" % (filename, version, gate))


if __name__ == "__main__":
    main()
