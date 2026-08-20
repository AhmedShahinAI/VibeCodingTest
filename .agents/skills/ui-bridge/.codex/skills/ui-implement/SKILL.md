---
name: ui-implement
description: Alias skill command for ui-bridge. Use when the user invokes $ui-implement, says /ui-implement, asks to generate self-contained HTML prototypes from the UI plan, create ui-prototypes HTML files, or turn Spec Kit UI planning artifacts into page prototypes.
---

# UI Implement

Alias for the `ui-bridge` workflow.

Use the installed `ui-gernreate-from-plan` skill and route to `subskills/ui-implement/SKILL.md`.

Run the UI implementation workflow from the project root:

1. Read `subskills/ui-implement/SKILL.md` completely before acting.
2. Run the executable staged workflow:

   ```bash
   python scripts/ui_implement_workflow.py --root .
   ```

3. This wrapper follows `.ui-bridge/phase0-plan.json` so UI work runs page-by-page in Phase 0 order.
4. It also scaffolds `ui-prototypes/design-tokens.css`, `_partials/`, and `compile-partials.py` automatically.
5. Use `--page`, `--group`, `--max-pages=N`, or `--resume` only for intentionally scoped runs.
6. Use `--draft` only for internal unapproved stage files; draft output is not client-presentable.
