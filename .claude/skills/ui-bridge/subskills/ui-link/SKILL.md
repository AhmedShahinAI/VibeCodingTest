# Subskill: ui-link-html-to-plan

**Command**: `/ui-link-html-to-plan`
**Parent skill**: `../../SKILL.md` (ui-bridge)
**Previous command**: `/ui-implement`
**Next command**: `/speckit-implement`

## Purpose

Link approved HTML prototypes back into Spec Kit `plan.md` and `tasks.md`.

This command does not make visual decisions. It reads generated prototypes and
approved `.ui-bridge` artifacts only.

## Required Inputs

- `ui-prototypes/*.html`
- `.ui-bridge/parsed-speckit.json`
- `.ui-bridge/page-map.json`
- `.ui-bridge/approvals.json`
- Spec Kit `plan.md`
- Spec Kit `tasks.md`

## Mandatory Command

Run:

```bash
python scripts/ui_link_workflow.py --root .
```

The wrapper runs `scripts/link_html.py`, which must:

- Scan `ui-prototypes/*.html`
- Extract page titles, IDs, and sections
- Write `.ui-bridge/task-html-map.json`
- Match prototypes to frontend tasks
- Mark matching Phase 0 prototype tasks complete
- Append UI Reference blocks to matched implementation tasks
- Append a UI Prototype Index to `plan.md` if missing
- Write `.ui-bridge/link-report.md`

## Safety Rules

- Never alter brand, design-system, or HTML content during linking.
- Never add colors/fonts from detection reports.
- Never duplicate an existing UI Reference block.
- Never remove task IDs, tags, checkboxes, or implementation text.
- Only append a `## UI Prototype Index` once.

## Done When

- `.ui-bridge/task-html-map.json` exists.
- `.ui-bridge/link-report.md` exists.
- Matching Phase 0 tasks are marked complete.
- Matched frontend tasks contain UI Reference blocks.
- `plan.md` contains one UI Prototype Index.
