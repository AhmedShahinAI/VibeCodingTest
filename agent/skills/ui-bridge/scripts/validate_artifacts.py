"""
Validate UI Bridge JSON artifacts against strict minimum schemas.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ui_bridge_core import SchemaValidator, read_json


def infer_type(path: Path) -> str:
    stem = path.name
    for suffix in (".v1.json", ".v2.json", ".v3.json", ".json"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
            break
    return stem


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate UI Bridge artifacts")
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()

    validator = SchemaValidator()
    errors = []
    for raw in args.paths:
        path = Path(raw)
        data = read_json(path, default=None)
        if data is None:
            errors.append("%s is missing or invalid JSON" % path)
            continue
        artifact_type = infer_type(path)
        errors.extend("%s: %s" % (path, err) for err in validator.validate(artifact_type, data))

    if errors:
        print("Artifact validation failed:", file=sys.stderr)
        for err in errors:
            print("  - %s" % err, file=sys.stderr)
        sys.exit(1)
    print("Artifact validation passed.")


if __name__ == "__main__":
    main()
