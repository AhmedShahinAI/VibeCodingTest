# Reference: Impeccable Integration

How ui-bridge uses impeccable.style to generate production-quality HTML prototypes.

---

## 1. What Is Impeccable

Impeccable (impeccable.style) is a design-quality AI layer that enforces
professional visual standards in HTML output. It works by reading two files
from the project root — `PRODUCT.md` and `DESIGN.md` — and using them as
the source of truth for brand, color, typography, and component style.

ui-bridge does NOT call Impeccable's CDN at runtime in generated HTML.
All design tokens are extracted from DESIGN.md and written inline into
each HTML file so the prototype works without internet access.

---

## 2. Check If Impeccable Is Available

Before running `/ui-plan`, check:

```bash
npx impeccable --version
```

If it returns a version number → Impeccable is installed. Proceed normally.

If it fails with `command not found` → Install it:

```bash
npx impeccable install --providers=claude
```

You do NOT need Impeccable installed for ui-bridge to work. The skill reads
DESIGN.md directly and applies the same design tokens to all HTML generation.
Impeccable is optional — it adds extra validation and AI-assisted refinement.

---

## 3. The Two Required Files

### PRODUCT.md

Tells Impeccable (and the generating AI) **what** the product is.

Filled from `templates/PRODUCT.md.template` by `/ui-plan`.
Written to: **project root** (not `.ui-bridge/`).

Required sections:

```markdown
# [Project Name]

## What is this product?
[What the product does in 1–3 sentences]

## Who uses it?
[Target audience description]

## Core problems it solves
[List of 3–5 user problems this product addresses]

## Key capabilities (Phase 1)
[Bulleted list of Phase 1 features]

## Register
[Tone: "professional", "approachable", "authoritative", "friendly"]

## Users
[Persona-level description: "Arabic-speaking professionals seeking training"]

## Voice
[How the product speaks: "Direct, clear, zero-jargon. Uses active voice."]

## Anti-references
[Brands this should NOT look like: "Avoid: consumer apps, social media aesthetic"]

## Goals
[Primary design objectives: "Build trust. Reduce registration friction. Show expertise."]

## Language and text direction
[LTR or RTL, primary language]
```

---

### DESIGN.md

Tells Impeccable **how** the product looks.

Filled from `templates/DESIGN.md.template` by `/ui-plan`.
Written to: **project root** (not `.ui-bridge/`).

Required sections:

```markdown
# Design System: [Project Name]

## Brand Colors
[Color table with hex values for all roles]

## Typography
[Font table for Latin and Arabic fonts]

## Layout
[Direction, max-width, spacing unit, border radius, shadow style]

## Component Style
[Descriptions for buttons, cards, inputs, tables, badges]

## Spacing Scale
[4px base unit, named sizes: xs=8px, sm=12px, md=16px, lg=24px, xl=40px, xxl=64px]

## Breakpoints
[Mobile: 375px, Tablet: 768px, Desktop: 1280px]

## Accessibility
[Minimum contrast ratio, focus indicator style, motion preference]

## Overall Aesthetic
[2–3 sentence description of the visual direction]
```

---

## 4. The 23 Impeccable Commands

When Impeccable is installed, these commands are available. ui-bridge uses
them in the order shown during `/ui-implement`:

| # | Command | When ui-bridge uses it |
|---|---------|----------------------|
| 1 | `impeccable init` | First run — creates `.impeccable/` config |
| 2 | `impeccable context read PRODUCT.md` | Loads product context |
| 3 | `impeccable context read DESIGN.md` | Loads design tokens |
| 4 | `impeccable tokens extract` | Extracts CSS custom properties |
| 5 | `impeccable palette validate` | Checks color contrast ratios |
| 6 | `impeccable palette suggest primary` | Suggests primary colors if none found |
| 7 | `impeccable typography suggest` | Suggests font pairings |
| 8 | `impeccable spacing scale` | Generates spacing scale from base unit |
| 9 | `impeccable layout suggest` | Suggests layout patterns for page type |
| 10 | `impeccable component card` | Generates a card component spec |
| 11 | `impeccable component button` | Generates button states spec |
| 12 | `impeccable component form` | Generates form + input spec |
| 13 | `impeccable component table` | Generates data table spec |
| 14 | `impeccable component nav` | Generates navigation spec |
| 15 | `impeccable component modal` | Generates modal spec |
| 16 | `impeccable component badge` | Generates badge/tag spec |
| 17 | `impeccable rtl apply` | Converts LTR CSS to logical properties |
| 18 | `impeccable html validate <file>` | Validates generated HTML against rules |
| 19 | `impeccable html fix <file>` | Auto-fixes common violations |
| 20 | `impeccable antipattern check <file>` | Scans for the 46 anti-patterns |
| 21 | `impeccable antipattern report` | Full anti-pattern report |
| 22 | `impeccable responsive check <file>` | Checks responsive breakpoints |
| 23 | `impeccable export tokens --format css` | Exports tokens as CSS variables |

**Note**: All 23 commands are optional. ui-bridge applies the same logic
internally when Impeccable is not installed.

---

## 5. The 44 Detector Rules

Impeccable's validator checks 44 rules across 8 categories.
These map directly to the 46 anti-patterns in `references/html-standards.md`
(the overlap is intentional — some rules cover multiple anti-patterns).

### Color Rules (7)

| Rule ID | Description | Maps to AP# |
|---------|-------------|-------------|
| COL-01 | Primary palette must not be purple-to-blue gradient | AP#1 |
| COL-02 | Accent colors must not exceed HSL saturation 90% on white | AP#2 |
| COL-03 | Professional tools must not use pastel primary palette | AP#3 |
| COL-04 | State must not rely on color alone | AP#4 |
| COL-05 | Gray text on colored backgrounds must pass 4.5:1 contrast | AP#5 |
| COL-06 | Text gradient on headings is forbidden | AP#6 |
| COL-07 | Background pattern z-index must not exceed foreground content | AP#7 |

### Typography Rules (6)

| Rule ID | Description | Maps to AP# |
|---------|-------------|-------------|
| TYP-01 | Default font requires brand justification in DESIGN.md | AP#8 |
| TYP-02 | Body text must not use display/decorative fonts | AP#9 |
| TYP-03 | Max 3 font-weight values per component | AP#10 |
| TYP-04 | Headings must not mix text-transform: uppercase with title case | AP#11 |
| TYP-05 | Paragraphs > 1 line must be text-align: start, not center | AP#12 |
| TYP-06 | Body font-size minimum 14px at any breakpoint | AP#13 |

### Layout Rules (9)

| Rule ID | Description | Maps to AP# |
|---------|-------------|-------------|
| LAY-01 | .card must not nest inside another .card | AP#14 |
| LAY-02 | Cards must not have border-inline-start as primary visual accent | AP#15 |
| LAY-03 | Feature icons must not stack as tiles above every heading | AP#16 |
| LAY-04 | Headings must not include numbering pseudo-elements (01, 02) | AP#17 |
| LAY-05 | Footer must not exceed 4 columns at 1280px | AP#18 |
| LAY-06 | No overflow-x: visible on any element at mobile breakpoint | AP#19 |
| LAY-07 | Section margin-bottom minimum 24px | AP#20 |
| LAY-08 | Hero overlays must maintain text contrast ratio ≥ 4.5:1 | AP#21 |
| LAY-09 | Sibling elements of same type must use consistent spacing | AP#22, AP#23 |

### Animation Rules (3)

| Rule ID | Description | Maps to AP# |
|---------|-------------|-------------|
| ANI-01 | No bounce or elastic keyframe animation | AP#24 |
| ANI-02 | No scroll-behavior: smooth combined with IntersectionObserver hijacking | AP#25 |
| ANI-03 | Transition-duration on interactive elements must be ≤ 400ms | AP#26 |

### Interactive Rules (7)

| Rule ID | Description | Maps to AP# |
|---------|-------------|-------------|
| INT-01 | Button padding minimum 12px vertical, 24px horizontal | AP#27 |
| INT-02 | Buttons must not be styled as plain text links | AP#28 |
| INT-03 | Every input must have an associated <label> | AP#29 |
| INT-04 | Clickable elements min-height 44px on mobile breakpoints | AP#30 |
| INT-05 | Active nav item must have a visible, non-color indicator | AP#31 |
| INT-06 | Dropdowns with > 10 items must include search/filter | AP#32 |
| INT-07 | Tooltips must not overlap primary content on trigger | AP#33 |

### Hierarchy Rules (4)

| Rule ID | Description | Maps to AP# |
|---------|-------------|-------------|
| HIE-01 | Max 1 .btn-primary per viewport section | AP#34 |
| HIE-02 | Max 3 badge/tag class variants per card | AP#35 |
| HIE-03 | Sibling elements must not have competing box-shadow values | AP#36 |
| HIE-04 | Pages must have measurable z-axis depth (shadow or elevation system) | AP#37 |

### Accessibility Rules (4)

| Rule ID | Description | Maps to AP# |
|---------|-------------|-------------|
| ACC-01 | Text contrast ≥ 4.5:1 (WCAG AA normal text) | AP#38 |
| ACC-02 | Large text (18pt+) contrast ≥ 3:1 | AP#39 |
| ACC-03 | All img elements must have non-empty alt attribute | AP#40 |
| ACC-04 | All interactive elements must have tabindex ≥ 0 or be native focusable | AP#41 |

### Component Rules (4)

| Rule ID | Description | Maps to AP# |
|---------|-------------|-------------|
| CMP-01 | Modals must not exceed 90vw on mobile breakpoints | AP#42 |
| CMP-02 | Empty states must have a CTA or guidance message | AP#43 |
| CMP-03 | Loading indicators must be styled, not bare border-radius spinners | AP#44 |
| CMP-04 | Border-radius on cards ≤ 12px; on inputs ≤ 8px | AP#45, AP#46 |

---

## 6. Common Mistakes and Fixes

### Mistake: PRODUCT.md missing Register section

**Symptom**: Impeccable cannot infer tone → uses generic neutral voice
**Fix**: Add the `## Register` section to PRODUCT.md:
```markdown
## Register
Professional, authoritative, approachable. Never salesy.
```

---

### Mistake: DESIGN.md has no Arabic font

**Symptom**: RTL pages use Latin font → Arabic text renders with fallback
**Fix**: Add Arabic font to DESIGN.md Typography table:
```markdown
| Heading (Arabic) | Cairo | 700 | 2rem–3rem |
| Body (Arabic) | Cairo | 400 | 1rem |
```
And add the `@import` inside `<style>` in the generated HTML:
```css
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
```

---

### Mistake: Forgetting CSS logical properties for RTL

**Symptom**: Layout breaks in RTL — margins/paddings flip incorrectly
**Fix**: Replace all directional CSS with logical properties:
```css
/* Wrong */  margin-left: 16px; padding-right: 8px; border-left: 2px solid;
/* Right */  margin-inline-start: 16px; padding-inline-end: 8px; border-inline-start: 2px solid;
```

---

### Mistake: External image in prototype

**Symptom**: Images don't load when prototype is viewed offline
**Fix**: Replace `<img src="https://...">` with:
```html
<!-- Option A: CSS placeholder -->
<div class="img-placeholder" style="width:100%; aspect-ratio:16/9; background:var(--color-border);"></div>

<!-- Option B: inline SVG -->
<svg width="400" height="225" viewBox="0 0 400 225" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="225" fill="#E2E8F0"/>
  <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="#94A3B8" font-size="14">Image</text>
</svg>
```

---

### Mistake: Using Lorem Ipsum for Arabic content

**Symptom**: Prototype feels fake → client cannot evaluate the UX
**Fix**: Use realistic Arabic content from the project domain:
- Course names: "قيادة الفرق الفعّالة", "التفاوض الاحترافي", "إدارة المشاريع الاحترافية"
- Expert names: "د. أحمد الخولي", "م. فاطمة العلي", "أ. محمد حسين"
- Governorates: القاهرة، الإسكندرية، الجيزة، المنصورة، أسيوط

---

## 7. Skipping Impeccable (No Node.js Available)

If Node.js is not available, ui-bridge runs in standalone mode:
- `/ui-plan` still reads brand signals and writes PRODUCT.md + DESIGN.md
- `/ui-implement` still generates full production-quality HTML
- All 8 HTML generation rules still apply
- All 44 detector rules are applied by the generating AI, not by Impeccable CLI
- The only difference: no `impeccable html validate` step at the end

Standalone mode produces identical output. Impeccable CLI is useful for
repeatable validation in CI/CD pipelines, not for one-off prototype generation.
