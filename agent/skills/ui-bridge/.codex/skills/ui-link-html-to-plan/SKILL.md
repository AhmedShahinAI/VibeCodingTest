---
description: "Alias skill command for ui-bridge. Use when the user invokes $ui-link-html-to-plan, says /ui-link-html-to-plan, asks to link generated HTML prototypes back into plan.md/tasks.md, scan ui-prototypes, or produce the UI link report."
---
# UI Link HTML To Plan

Alias for the `ui-bridge` workflow.

Use the installed `ui-gernreate-from-plan` skill and route to `subskills/ui-link/SKILL.md`.

Run the UI link workflow from the project root:

1. Read `subskills/ui-link/SKILL.md` completely before acting.
2. Run the executable wrapper:

   ```bash
   python scripts/ui_link_workflow.py --root .
   ```

3. The wrapper scans `ui-prototypes`, writes `.ui-bridge/task-html-map.json`, updates safe Spec Kit references, and writes `.ui-bridge/link-report.md`.
