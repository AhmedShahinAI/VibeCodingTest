---
name: ui-plan
description: Alias skill command for ui-bridge. Use when the user invokes $ui-plan, says /ui-plan, asks to discover UI pages from Spec Kit plan.md/tasks.md, build the UI Phase 0 plan, generate page-map/design-system artifacts, or prepare HTML prototype planning from Spec Kit artifacts.
---

# UI Plan

Alias for the `ui-bridge` workflow.

Use the installed `ui-gernreate-from-plan` skill and route to `subskills/ui-plan/SKILL.md`.

Run the UI planning workflow from the project root:

1. Read `subskills/ui-plan/SKILL.md` completely before acting.
2. Run the executable wrapper:

   ```bash
   python scripts/ui_plan_workflow.py --root . --brand-policy=strict
   ```

3. If strict brand policy blocks the run, use proposal mode only for review:

   ```bash
   python scripts/ui_plan_workflow.py --root . --brand-policy=proposal --draft --proposal A
   ```

   For an explicitly scoped home-page-only planning run:

   ```bash
   python scripts/ui_plan_workflow.py --root . --brand-policy=proposal --draft --proposal A --page home
   ```

4. Approve a brand only after the user chooses it:

   ```bash
   python scripts/approve_brand.py --root . --proposal A
   ```

5. Continue strict mode after file-backed approvals exist.
