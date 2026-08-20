---
description: "Activate for any of the following: \"ui-plan\", \"ui-implement\", \"ui-link\", \"build the UI\", \"design the pages\", \"prototype the screens\", \"turn the plan into HTML\", \"show me what it looks like\", \"create the frontend prototype\", \"link the html to the plan\", or any request to generate, build, design, or preview HTML pages from a Spec Kit plan or tasks file.\n"
---
# UI Bridge

UI Bridge transforms Spec Kit planning artifacts into production-quality, self-contained
HTML prototypes that can be shown to clients immediately and used by developers as
pixel-perfect implementation references.

It sits between `/speckit-tasks` and `/speckit-implement` in the Spec Kit workflow.

---

## Commands

Claude Code uses slash commands. Codex uses the matching alias skills installed from
`.codex/skills/`:

- `$ui-plan`
- `$ui-implement`
- `$ui-link-html-to-plan`
- `$ui-into-preview`
- `python scripts/approve_brand.py --proposal A --root .`

This skill exposes four sub-commands. Each has its own detailed SKILL.md in `subskills/`.
**Always read the relevant subskill SKILL.md before executing a command.**

| Command | Subskill file | When to use |
|---------|---------------|-------------|
| `/ui-plan` | `subskills/ui-plan/SKILL.md` | After `/speckit-tasks` — discover pages, install Impeccable, build Phase 0 plan |
| `/ui-implement` | `subskills/ui-implement/SKILL.md` | After `/ui-plan` — generate one HTML file per page |
| `/ui-link-html-to-plan` | `subskills/ui-link/SKILL.md` | After `/ui-implement` — link HTML files back into tasks.md and plan.md |
| `/ui-into-preview` | `subskills/ui-preview/SKILL.md` | After `/ui-link` — generate GitHub Pages canvas presentation from HTML prototypes |

---

## Full Workflow

```
/speckit-constitution
        ↓
/speckit-specify
        ↓
/speckit-plan
        ↓
/speckit-tasks
        ↓
/ui-plan               ← discovers pages, installs Impeccable, adds Phase 0 to plan + tasks
        ↓
/ui-implement          ← generates ui-prototypes/*.html (one per page, fully self-contained)
        ↓
/ui-link-html-to-plan  ← links each HTML file back into plan.md + tasks.md as references
        ↓
/ui-into-preview       ← canvas presentation tool, GitHub Pages deploy
        ↓
/speckit-implement     ← begin actual code implementation using HTML as reference
```

---

## Core Principles

1. **Never invent a visual identity.** Strict mode is default. If no approved brand
   exists, stop and write `.ui-bridge/brand-intake.vN.json`. Do not silently apply
   EdTech/category colors, Cairo/Inter, or colors found inside skill files. Proposal
   mode may generate three unapproved directions, but one must be approved in
   `.ui-bridge/approvals.json` before Impeccable, design-system, or HTML generation.

2. **Every HTML file is token-driven and portable.** Shared visual values come from
   `ui-prototypes/design-tokens.css`, while each page also copies the required core
   tokens inline in `:root` so raw-file reviewers and anti-slop checks see the exact
   approved values.

3. **One sub-phase = one page. One task = one section or component on that page.**
   Granularity must match tasks.md exactly so tasks can be checked off as HTML sections
   are built.

4. **Impeccable must be verified before any HTML is generated.** `PRODUCT.md` and
   `DESIGN.md` must be real verified outputs, with `.ui-bridge/impeccable-run.json`
   proving the files exist, are not unresolved templates, and have recorded hashes.

5. **The HTML prototype IS the final design — not a wireframe.** It must use real content
   in the project language, real entity names from the data model, and accurate form
   fields. Clients approve it. Developers implement from it.

6. **Spec Kit artifacts are sacred.** Phase 0 may be inserted or replaced only when an
   existing Phase 0 is polluted/stale. Never reorder implementation phases.

7. **Static prototypes contain static content.** Page maps use `static_content_needed`
   for prototype content and keep implementation-only API notes separate as
   `api_contract_notes`.

8. **Design direction is a gated artifact chain.** Moodboard, visual DNA, layout DNA,
   hero diversity, narrative patterns, content realism, and design system are versioned
   artifacts. Blocking reviewer issues stop the next stage.

---

## File Locations

`.ui-bridge/` is runtime output/state created inside the target project. It is
not copied into the skill. The skill must contain the scripts, schemas, and
instructions that regenerate and validate those artifacts.

| Path | Purpose |
|------|---------|
| `ui-prototypes/` | Generated HTML files, one per page |
| `.ui-bridge/` | Working state — never committed to client repos |
| `.ui-bridge/PRODUCT.md` | Impeccable product descriptor (source) |
| `.ui-bridge/DESIGN.md` | Impeccable design descriptor (source) |
| `.ui-bridge/brand-decisions.md` | Log of all brand/color/font decisions with rationale |
| `.ui-bridge/brand-intake.vN.json` | Approved brand or blocking intake request |
| `.ui-bridge/brand-proposals.vN.json` | Proposal-mode directions A/B/C |
| `.ui-bridge/approvals.json` | File-backed human approvals |
| `.ui-bridge/impeccable-run.json` | Impeccable verification report |
| `.ui-bridge/reviews/` | Reviewer reports with blocking/advisory severities |
| `.ui-bridge/html-stages/` | Multi-stage HTML generation state and intermediate files |
| `.ui-bridge/layout-dna.vN.json` | Layout rhythm, symmetry, density, grid, and alignment rules |
| `.ui-bridge/hero-diversity.vN.json` | Per-page hero pattern assignments and anti-repetition rules |
| `.ui-bridge/narrative-patterns.vN.json` | Per-page storytelling pattern assignments |
| `.ui-bridge/content-realism.vN.json` | Rules for metrics, names, titles, testimonials, and forbidden placeholders |
| `.ui-bridge/page-map.md` | Complete list of pages, slugs, sections, and data needs |
| `PRODUCT.md` | Copy at project root for Impeccable to read |
| `DESIGN.md` | Copy at project root for Impeccable to read |
| `plan.md` | Spec Kit plan — Phase 0 appended by `/ui-plan` |
| `tasks.md` | Spec Kit tasks — Phase 0 tasks appended by `/ui-plan` |

---

## Reference Files

| File | What it covers |
|------|---------------|
| `references/impeccable-integration.md` | How to use Impeccable with this skill |
| `references/html-standards.md` | Self-contained HTML output standards |
| `references/speckit-artifacts.md` | Where to find and parse plan.md / tasks.md |
| `references/brand-extraction.md` | Brand signal discovery process and industry defaults |
