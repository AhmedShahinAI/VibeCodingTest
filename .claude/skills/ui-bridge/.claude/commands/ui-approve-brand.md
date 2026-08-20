Approve a generated UI Bridge brand proposal.

Usage:

```bash
python scripts/approve_brand.py --root . --proposal A
python scripts/run_detection.py --command ui-plan --brand-policy=strict --root .
```

Only approve a proposal the user explicitly selected. Approval is written to
`.ui-bridge/approvals.json` and unlocks the next strict workflow stages.
