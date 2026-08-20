"""
Approve one generated brand proposal.

Usage:
    python scripts/approve_brand.py --proposal A --root .
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from ui_bridge_core import ApprovalStore, SchemaValidator, VersionedArtifacts, ensure_bridge, read_json, write_json


def latest_proposals(root: Path) -> Path:
    bridge = ensure_bridge(root)
    latest = read_json(bridge / "latest.json", default={}) or {}
    name = latest.get("brand-proposals")
    if name and (bridge / name).exists():
        return bridge / name
    candidates = sorted(bridge.glob("brand-proposals.v*.json"))
    if not candidates:
        raise RuntimeError("No brand proposals found. Run extract_brand.py --brand-policy=proposal first.")
    return candidates[-1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Approve a brand proposal")
    parser.add_argument("--root", default=".")
    parser.add_argument("--proposal", required=True, help="Proposal ID, e.g. A, B, or C")
    parser.add_argument("--approved-by", default="user")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    proposal_id = args.proposal.strip().upper()
    proposal_path = latest_proposals(root)
    proposals = read_json(proposal_path, default={})
    direction = None
    for item in proposals.get("directions", []):
        if str(item.get("id", "")).upper() == proposal_id:
            direction = item
            break
    if not direction:
        raise SystemExit("ERROR: Proposal %s not found in %s" % (proposal_id, proposal_path))
    font_values = " ".join(str(v) for v in direction.get("fonts", {}).values())
    if "USER_APPROVED_" in font_values:
        raise SystemExit(
            "ERROR: Proposal %s still requires user-approved fonts. "
            "Add real project fonts or edit the proposal artifact before approving." % proposal_id
        )

    store = VersionedArtifacts(root)
    intake = {
        "state": "approved_brand",
        "policy": "proposal",
        "proposal_id": proposal_id,
        "approved_direction": direction,
        "signals": proposals.get("raw_signals", {}),
        "required_user_action": [],
    }
    errors = SchemaValidator().validate("brand-intake", intake)
    if errors:
        raise SystemExit("ERROR: approved brand intake schema failed: %s" % "; ".join(errors))
    intake_path = store.write_new("brand-intake", intake)
    version_match = re.search(r"\.v(\d+)\.json$", intake_path.name)
    version = "v%s" % version_match.group(1) if version_match else "v1"

    approvals = ApprovalStore(root).approve(
        "brand_direction",
        version,
        approved_by=args.approved_by,
        extra={"proposal": proposal_id, "artifact": intake_path.name},
    )

    bridge = ensure_bridge(root)
    brand_signals = read_json(bridge / "brand-signals.json", default={}) or {}
    brand_signals["state"] = "approved_brand"
    brand_signals["brand_decisions"] = intake
    write_json(bridge / "brand-signals.json", brand_signals)

    print("Approved brand proposal %s -> %s" % (proposal_id, intake_path))
    print("Updated approvals: %s" % (bridge / "approvals.json"))
    print(json.dumps(approvals, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
