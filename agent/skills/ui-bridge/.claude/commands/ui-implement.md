Read and follow `subskills/ui-implement/SKILL.md` completely before acting.

Run the executable implementation wrapper from the project root:

```bash
python scripts/ui_implement_workflow.py --root .
```

This wrapper now:

- follows the Phase 0 page order from `.ui-bridge/phase0-plan.json`
- scaffolds `ui-prototypes/design-tokens.css`, `_partials/`, and `compile-partials.py`
- generates and publishes pages one page sub-phase at a time
- stamps shared partials after publication

Use `--page`, `--group`, `--max-pages`, or `--resume` only when you intentionally want a scoped Phase 0 run.
