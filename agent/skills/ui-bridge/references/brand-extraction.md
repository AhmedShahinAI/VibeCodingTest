# Reference: Brand Signal Extraction

UI Bridge discovers project-owned visual identity. It must not invent final
colors or fonts from industry/category defaults.

## Signal Priority

1. Explicit project signals:
   - CSS custom properties such as `--color-primary`
   - Tailwind or theme config colors
   - project-owned logo files
   - approved brand documents supplied by the user

2. Repeated project signals:
   - repeated colors in real app/source files
   - repeated font-family declarations in real app/source files
   - project-owned design tokens

3. Approval-required state:
   - strict mode writes `brand_intake_required` and stops
   - proposal mode writes unapproved Direction A/B/C
   - fallback mode is internal only and cannot create client-presentable HTML

## Excluded Sources

Never use signals from:

- `.claude/`
- `.codex/`
- `.ui-bridge/`
- `ui-gernreate-from-plan/`
- `references/`
- `templates/`
- generated prototypes
- build output, caches, or git metadata

## CSS Extraction Examples

Examples must use placeholders, not reusable brand defaults:

```css
:root {
  --color-primary: #123456;
  --color-accent: #654321;
  --color-bg: #ffffff;
  --font-heading: "Project Heading Font", sans-serif;
  --font-body: "Project Body Font", sans-serif;
}
```

Only extract these values when they appear in real project-owned files.

## Project Type

Project type can inform proposal copy, competitor research, content density,
layout DNA, and narrative strategy. It must not select final colors, fonts,
radii, shadows, imagery, or icon style.

If no approved brand exists:

```text
strict mode -> brand_intake_required -> stop
proposal mode -> brand-proposals.vN.json -> user approval required
fallback mode -> unapproved internal draft only
```

## No Industry Defaults

There is deliberately no industry color/font table in this reference.

Do not infer:

- EdTech blue palettes
- SaaS purple/blue palettes
- cool gray backgrounds
- Inter defaults
- Cairo/Tajawal defaults unless the project or user approves them

## RTL And Arabic

Arabic/RTL detection can set direction and language expectations. It cannot
choose a font family by itself. Arabic typography must come from project-owned
signals or an approved proposal.

## Brand Decision Log

Every accepted decision must include:

- value
- source file or approved proposal version
- confidence
- approval state
- rationale

If a decision cannot be sourced or approved, write an intake requirement instead
of filling the gap with defaults.
