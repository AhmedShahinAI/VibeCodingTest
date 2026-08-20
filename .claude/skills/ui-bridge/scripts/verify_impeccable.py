"""
Verify Impeccable outputs before design/HTML generation.

This script cannot press slash commands for the agent; it verifies that the
expected files exist, are not unresolved templates, and records hashes. If the
files are missing or template-like, it fails hard.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from ui_bridge_core import ensure_bridge, file_sha256, utc_now, write_json


def command_version() -> str | None:
    for cmd in ("impeccable", "npx"):
        if not shutil.which(cmd):
            continue
        try:
            args = [cmd, "--version"] if cmd == "impeccable" else [cmd, "impeccable", "--version"]
            proc = subprocess.run(args, capture_output=True, text=True, timeout=8)
            if proc.returncode == 0:
                return proc.stdout.strip() or proc.stderr.strip()
        except Exception:
            continue
    return None


def is_template_like(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return "{{" in text or "}}" in text or "PLACEHOLDER" in text.upper()


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Impeccable output files")
    parser.add_argument("--root", default=".")
    parser.add_argument("--require-cli", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    bridge = ensure_bridge(root)
    product = root / "PRODUCT.md"
    design = root / "DESIGN.md"
    version = command_version()

    failures = []
    if args.require_cli and not version:
        failures.append("Impeccable CLI was not found.")
    for path in (product, design):
        if not path.exists():
            failures.append("%s missing." % path.name)
        elif is_template_like(path):
            failures.append("%s still contains template placeholders." % path.name)

    report = {
        "timestamp": utc_now(),
        "success": not failures,
        "command_required": ["/impeccable init", "/impeccable document"],
        "version": version,
        "input_hashes": {
            "PRODUCT.md": file_sha256(product),
            "DESIGN.md": file_sha256(design),
        },
        "output_hashes": {
            ".ui-bridge/PRODUCT.md": file_sha256(bridge / "PRODUCT.md"),
            ".ui-bridge/DESIGN.md": file_sha256(bridge / "DESIGN.md"),
        },
        "failures": failures,
    }
    write_json(bridge / "impeccable-run.json", report)

    if failures:
        print("ERROR: Impeccable verification failed:", file=sys.stderr)
        for failure in failures:
            print("  - %s" % failure, file=sys.stderr)
        sys.exit(1)

    print("Impeccable verification passed. Report: %s" % (bridge / "impeccable-run.json"))


if __name__ == "__main__":
    main()
