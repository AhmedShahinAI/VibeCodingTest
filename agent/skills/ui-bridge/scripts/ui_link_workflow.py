"""
Executable $ui-link-html-to-plan workflow wrapper.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Link generated HTML prototypes back to Spec Kit artifacts")
    parser.add_argument("--root", default=".")
    parser.add_argument("--prototypes-dir", default="ui-prototypes")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "link_html.py"),
            "--root",
            str(root),
            "--prototypes-dir",
            args.prototypes_dir,
        ],
        cwd=root,
        text=True,
    )
    raise SystemExit(proc.returncode)


if __name__ == "__main__":
    main()
