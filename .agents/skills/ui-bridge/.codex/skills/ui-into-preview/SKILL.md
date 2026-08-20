---
name: ui-into-preview
description: Alias skill command for ui-bridge. Use when the user invokes $ui-into-preview, says /ui-into-preview, asks to generate the UI preview canvas, prepare a deployable client preview, or turn ui-prototypes into ui-preview.
---

# UI Into Preview

Alias for the `ui-bridge` workflow.

Use the installed `ui-gernreate-from-plan` skill and route to `subskills/ui-preview/SKILL.md`.

Run the preview workflow from the project root:

1. Read `subskills/ui-preview/SKILL.md` completely before acting.
2. Run the executable wrapper:

   ```bash
   python scripts/ui_preview_workflow.py --root .
   ```

3. The wrapper auto-resolves `ui-prototypes/`, the active Spec Kit feature folder, `.ui-bridge/page-map.json`, and writes `ui-preview/`.
