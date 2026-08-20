# Subskill: ui-plan

**Command**: `/ui-plan`
**Parent skill**: `../../SKILL.md` (ui-bridge)
**Next command**: `/ui-implement`

## Prerequisites

- `/speckit-plan` has produced `plan.md`
- `/speckit-tasks` has produced `tasks.md`

## Step 1 — Parse Spec Kit

Run:

```bash
python scripts/parse_speckit.py --json --root .
```

Output must include non-empty phases when `plan.md` contains phase headings.
Fails clearly if artifacts are missing.

## Step 2 — Brand Extraction

Run:

```bash
python scripts/extract_brand.py --root .
```

Rules:
- Scan only real project sources — never `.claude/`, `.codex/`, `ui-gernreate-from-plan/`,
  `references/`, `templates/`, `.ui-bridge/`, build or cache folders.
- Do not infer final colors or fonts from project type alone.
- Do not silently choose EdTech blue, cyan accents, Cairo, Inter, or gray backgrounds
  unless those signals exist in the project.
- If no approved brand direction exists, write `brand-intake.vN.json` with proposal directions
  and stop. Report the proposals to the user; they must select one before continuing.

When a brand direction is approved, `approvals.json` must contain:
```json
{
  "brand_direction": { "approved": true, "version": "vN", "proposal": "A" }
}
```

## Step 3 — Generate Page Map

Run:

```bash
python scripts/generate_page_map.py --root .
```

Rules:
- Include all detected public, detail, admin, form, dashboard, and error pages.
- Do not silently reduce to home-page-only.
- Pages must include `static_content_needed` (not `api_data_needed`).

## Step 4 — Generate Design Direction Artifacts

After brand approval, generate the 11 direction artifacts by writing them as JSON
to `.ui-bridge/`. Each artifact name is listed below with its required keys.
Claude generates these from the approved brand direction and project plan signals.

Required artifacts and their top-level keys:

| Artifact | Required keys |
|---|---|
| `competitive-analysis.vN.json` | `patterns_to_copy`, `patterns_to_avoid`, `hero_types`, `section_types`, `copy_tone`, `spacing_observations` |
| `moodboard.vN.json` | `photography`, `density`, `card_style`, `spacing_style`, `icon_style`, `color_temperature` |
| `visual-dna.vN.json` | `personality`, `geometry`, `density`, `motion`, `contrast`, `photography_style`, `iconography` |
| `layout-dna.vN.json` | `state`, `symmetry`, `editorialness`, `card_density`, `grid_style`, `alignment_style`, `section_rhythm`, `asymmetry_level`, `page_assignments` |
| `photography-system.vN.json` | `style`, `aspect_ratios`, `color_grading`, `background_style`, `portrait_rules` |
| `iconography-system.vN.json` | `style`, `stroke_width`, `corner_radius`, `density`, `placement` |
| `hero-diversity.vN.json` | `patterns`, `page_assignments`, `anti_repetition_rules` |
| `component-personality.vN.json` | `buttons`, `cards`, `badges`, `stats`, `forms`, `tables` |
| `content-realism.vN.json` | `numbers`, `names`, `titles`, `testimonials`, `forbidden` |
| `narrative-patterns.vN.json` | `patterns`, `page_assignments`, `anti_repetition_rules` |
| `section-diversity.vN.json` | `patterns`, `page_assignments`, `anti_repetition_rules` |

After generating, update `approvals.json`:
```json
{
  "moodboard": { "approved": true, "version": "v1" },
  "visual_layout_dna": { "approved": true, "version": "v1" }
}
```

## Step 5 — Generate Design System

Run after all direction artifacts exist and approvals are in place:

```bash
python scripts/infer_master.py --root .
```

This writes `.ui-bridge/design-system.json` and `.ui-bridge/design-system.css`.

Update approvals after generation:
```json
{
  "design_system": { "approved": true, "version": "v1" }
}
```

## Step 6 — Update Spec Kit Phase 0

Run:

```bash
python scripts/update_plan.py --root .
```

Rules:
- Insert Phase 0 when missing.
- Replace stale Phase 0 when present.
- Never reorder implementation phases.

## Done When

- `parsed-speckit.json` has non-empty phases.
- `brand-intake.vN.json` has an approved direction (not just signals).
- `approvals.json` contains approved `brand_direction`, `moodboard`, `visual_layout_dna`, `design_system`.
- `page-map.json` includes all detected pages with `static_content_needed`.
- `design-system.json` and `design-system.css` exist.
- Phase 0 in `plan.md` is full-scope.
