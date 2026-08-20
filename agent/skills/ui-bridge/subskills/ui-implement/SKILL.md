# Subskill: ui-implement

**Command**: `/ui-implement`
**Parent skill**: `../../SKILL.md` (ui-bridge)
**Previous command**: `/ui-plan`
**Next command**: `/ui-link-html-to-plan`

---

## How This Skill Works — Read First

**Claude writes every page's HTML directly. The Python script does NOT write content.**

The `ui_implement_workflow.py` script handles only two things:
1. Approval gating (checks `.ui-bridge/approvals.json` before any file is written)
2. Publishing the final file to `ui-prototypes/[slug].html`

**Claude writes the actual HTML** — complete, final, self-contained, in one pass — following all rules in this file. Do not delegate content generation to `run_html_stage.py`. That script's `full_document()` function produces identical scaffolding for every page and must not be used for content.

---

## Mandatory Pre-Flight

Verify these files exist before generating any HTML:

- `.ui-bridge/design-system.json`
- `.ui-bridge/design-system.css`
- `.ui-bridge/page-map.json`
- `.ui-bridge/visual-research.json`
- `.ui-bridge/approvals.json` (must contain `design_system: approved`)

If any are missing, stop and run `/ui-plan` first.

---

## Required Inputs — Read Before Every Page

Read all three files before writing a single line of HTML:

1. `.ui-bridge/design-system.json` — typography, colors, component patterns, hero assignments, section assignments
2. `.ui-bridge/page-map.json` — page list, section hints, `static_content_needed`
3. `.ui-bridge/visual-research.json` — real product references, `do_this`, `not_this`

---

## Single-Pass Generation Rule

Generate each page as a **complete, final, self-contained HTML file in one pass**.

- All CSS embedded in `<style>` — no external stylesheets
- No CDN links, no external scripts (Google Fonts `<link>` is the one allowed exception)
- All JavaScript for interactions inline in `<script>`
- Every page is immediately openable in a browser with no build step

Write the whole page. Do not split into stages.

---

## Brand Logo Requirements

**FORBIDDEN**: A single letter in a colored square is not a logo. Never produce `<div>م</div>` as a logomark.

Every prototype must have a **custom SVG logomark** with a distinctive geometric shape:

### Logomark Design Rules

1. Abstract geometric shape reflecting brand personality — ascending bars, interlocking arcs, shield, faceted gem, etc.
2. Recognizable at 20px and at 200px
3. Brand primary color as fill, lighter/darker accent for depth
4. Embed as inline `<svg>` with `viewBox` — never `<img>` for logos
5. No generic icons (lightbulb, graduation cap, book, globe) unless visually reimagined
6. Arabic-first brands: wordmark text in Arabic with optional Latin subtitle

### Logo Placement

- **Nav** (compact): SVG mark (32–40px height) + brand name + tagline alongside
- **Footer** (full): Same SVG, slightly larger

```html
<!-- Replace [BRAND_NAME], [BRAND_COLOR], [HOME_URL], [TAGLINE] with project values -->
<a href="[HOME_URL]" class="nav-logo" aria-label="[BRAND_NAME]">
  <svg class="logo-mark" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <!-- Design a custom geometric shape using var(--color-primary) as the base fill -->
    <rect width="40" height="40" rx="9" fill="var(--color-primary)"/>
    <!-- Add 2-3 geometric elements that form a distinctive, abstract mark -->
  </svg>
  <div class="logo-text">
    <span class="logo-name">[BRAND_NAME]</span>
    <span class="logo-tagline">[TAGLINE]</span>
  </div>
</a>
```

> Read the project's brand guidelines or `.ui-bridge/design-system.json` for the exact logo SVG shapes, colors, and brand name. Do NOT copy colors or text from another project's partials.

---

## Partner / Client Logo Requirements

**FORBIDDEN**: Plain text `<span>أرامكو السعودية</span>` for partner logos.

Every partner/client logo must be an **inline `<svg>` wordmark** with:
- `role="img"` and `aria-label="[Full brand name]"`
- Brand's primary color as `fill`
- `viewBox` sized to content (90–150px wide × 36–44px tall)

```css
.partner-logo { filter: grayscale(1) opacity(0.45); transition: filter 220ms; }
.partner-logo:hover { filter: grayscale(0) opacity(1); }
```

### Partner Brand Colors

Always look up official brand colors from:
1. The client's official brand guidelines
2. `.ui-bridge/design-system.json` under `"partners"` (if present)
3. The partner's own website CSS

Do NOT guess or use remembered colors — brand colors must come from the project's source of truth.

---

## Shared Design System Files — MANDATORY

**THESE ARE NON-NEGOTIABLE RULES. VIOLATING ANY OF THEM IS A BLOCKER.**

The prototype folder has FOUR shared infrastructure files. Never bypass them.

### `[PROTOTYPE_DIR]/design-tokens.css` — Single Source of Truth for CSS Vars

> **`[PROTOTYPE_DIR]`** = the project's prototype output folder (e.g., `ui-prototypes/`). Check the project root or `page-map.json` to find the actual path.

**RULE**: All CSS custom property VALUES are authoritative in `design-tokens.css`.
Before writing any `:root {}` block, READ `design-tokens.css` from the current project and copy the exact values.
Never invent color or spacing values. Never use hardcoded hex colors when a CSS variable exists.

**RULE**: Every HTML file must contain `<link rel="stylesheet" href="design-tokens.css">` in `<head>`.

### `[PROTOTYPE_DIR]/_partials/` — Shared Header / Sidebar / Footer

Partials are project-specific. A project may have any combination of:
- `sidebar-admin.html` — admin/dashboard sidebar navigation
- `nav-public.html` — public-facing header navigation
- `footer-public.html` — public-facing footer
- Any other shared structural component

**Before building pages**: check what partials already exist in the project's `_partials/` folder. If none exist yet, create them as part of initial page setup, then use them on every page.

### `[PROTOTYPE_DIR]/compile-partials.py` — Partial Stamping Script

This script reads `_partials/*.html` and stamps their content into every HTML page between PARTIAL markers. Check whether the project has this script (or an equivalent) before using.

**RULE — ZERO TOLERANCE**: NEVER write shared nav/sidebar/footer HTML directly in individual page files. 100% of shared structural HTML lives in `_partials/`. Writing it directly in a page breaks consistency across the prototype.

**RULE — MANDATORY WORKFLOW**: After generating ANY new page OR modifying any partial file, run the compile script:
```bash
python [PROTOTYPE_DIR]/compile-partials.py
```
This is not optional. Skipping it leaves pages inconsistent.

**RULE — TO CHANGE SHARED SECTIONS**: Edit ONLY the `_partials/*.html` file, then run the compile script. Never edit individual page files' nav/sidebar/footer HTML directly.

### How to Mark a New Page (PARTIAL Marker Syntax)

Wrap shared sections with PARTIAL markers. The marker name must match the partial filename (without `.html`):

```html
<!-- For an admin sidebar partial named sidebar-admin.html: -->
<aside class="sidebar" aria-label="Main navigation">
<!-- PARTIAL:sidebar-admin -->
<!-- /PARTIAL:sidebar-admin -->
</aside>

<!-- For a public nav partial named nav-public.html: -->
<header>
<!-- PARTIAL:nav-public -->
<!-- /PARTIAL:nav-public -->
</header>

<!-- For a footer partial named footer-public.html: -->
<footer>
<!-- PARTIAL:footer-public -->
<!-- /PARTIAL:footer-public -->
</footer>
```

Leave the content between markers **empty on creation** — `compile-partials.py` fills it. Do NOT hand-write content between the markers.

### Active Item Highlighting — SELF-CONTAINED IN PARTIAL

**RULE**: Do NOT add per-page active-item scripts. Each partial should include a self-contained JavaScript block that reads `location.pathname` and auto-highlights the current page's nav item. This makes the partial truly portable.

Pattern to include at the bottom of each nav/sidebar partial:
```javascript
<script>
(function(){
  var map = { 'page-a.html': 'key-a', 'page-b.html': 'key-b' /* ... */ };
  var key = map[location.pathname.split('/').pop()];
  if (key) {
    var el = document.querySelector('[data-page="' + key + '"]');
    if (el) el.classList.add('active');
  }
})();
</script>
```

Replace the `map` object and `data-page` attributes with the actual page filenames and keys for the current project.

### The Correct 3-Step Workflow for Every New Page

1. Write the page HTML with **EMPTY** PARTIAL markers (open/close comments, no content between them)
2. Run `python [PROTOTYPE_DIR]/compile-partials.py` to stamp shared sections into the markers
3. Run the anti-slop checker on the new file to verify zero violations

All three steps are mandatory for every page, every time.

---

## Required CSS Variables — Every File

The anti-slop checker scans each HTML file's RAW content for required token names.
Because it reads HTML files directly (not the linked CSS), EVERY file must declare all required tokens in an inline `:root {}` — even if `design-tokens.css` is linked.

**RULE**: Read `[PROTOTYPE_DIR]/design-tokens.css` first. Copy the exact values from it into the inline `:root {}`. Never invent values or use values from a different project.

The required token NAMES (values come from your project's `design-tokens.css`):

```css
:root {
  --color-primary:   /* brand primary color from design-tokens.css */;
  --color-accent:    /* brand accent color */;
  --color-bg:        /* page background color */;
  --font-heading:    /* heading font stack */;
  --font-body:       /* body font stack */;
  --text-h1:         /* H1 font size (clamp recommended) */;
  --space-4:         /* base spacing unit (typically 16px) */;
  --radius-md:       /* medium border radius */;
  --duration-base:   /* base transition duration */;
  --ease-primary:    /* base easing function */;
}
```

The inline `:root {}` block is REQUIRED in every HTML file (anti-slop checker reads only the raw HTML, not linked CSS files). You may add aliases but the canonical names above must be present.

**NEVER copy color values from another project's `:root {}` blocks.** Always source values from the current project's `design-tokens.css`.

---

## Required Responsive and Accessibility Rules — Every File

```css
@media (max-width: 768px) { /* tablet breakpoint — required */ }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; }
}
```

Every file must also include:
- `class="container"` wrapper on the main content area
- A skip link as first child of `<body>`: `<a class="skip-link" href="#main">[Skip to main content in the project's language]</a>`
  - English: "Skip to main content"
  - Arabic: "تجاوز إلى المحتوى الرئيسي"
  - Use the project's primary language

---

## Prototype Nav — Required on Every Page

**REQUIRED**: `class="prototype-nav"` (not `proto-nav`). Fixed bottom bar, always `dir="ltr"` regardless of page language, dark background, links to ALL pages in the prototype set.

```html
<nav class="prototype-nav" aria-label="Prototype navigation" dir="ltr">
  <!-- List EVERY page in the project's page-map.json here.
       Check page-map.json or the plan.md for the complete list. -->
  <a href="[page-a].html">[Label A]</a> |
  <a href="[page-b].html">[Label B]</a> |
  <!-- ... one link per page ... -->
</nav>
```

Required CSS (include in every page, do not change class name):
```css
.prototype-nav { position: fixed; bottom: 0; left: 0; right: 0; background: rgba(10,10,10,.96);
  color: rgba(255,255,255,.6); padding: 8px clamp(12px,3vw,32px); display: flex; align-items: center;
  gap: 6px; font-size: .72rem; z-index: 9999; flex-wrap: wrap; font-family: sans-serif;
  border-top: 1px solid rgba(255,255,255,.08); }
.prototype-nav a { color: var(--color-primary); padding: 2px 4px; border-radius: 3px; }
```

Always include a spacer `<div class="proto-spacer" aria-hidden="true"></div>` before `</body>` so the prototype nav doesn't overlap page content.

---

## Nav Bar — Solid Background Required

**FORBIDDEN**: `backdrop-filter: blur` on the nav or any sticky header (triggers `transparent_with_blur`).

```css
/* CORRECT — solid opaque background (class name varies per project) */
header { background: var(--color-surface); border-bottom: 1px solid var(--color-border); }
/* FORBIDDEN — semi-transparent with blur */
header { background: rgba(255,255,255,.9); backdrop-filter: blur(14px); }
```

The header element MUST use `position: sticky; top: 0`. Verify the CSS selector actually matches the HTML element — a class not present on any element does nothing.
The canonical nav layout (flex, sticky, mobile toggle) belongs in `design-tokens.css` — not repeated inline on every page.

---

## Anti-Slop Rules — Apply Before Writing Each Section

**Every item below is a known reviewer finding that BLOCKS production:**

### Structure
- [ ] `<main id="main">` wraps all page content between header and footer
- [ ] `class="container"` wrapper present
- [ ] All 9 required CSS variables present in `:root {}`
- [ ] `class="prototype-nav"` present (not `proto-nav`)
- [ ] No `{{...}}`, `[PLACEHOLDER]`, `TODO`, `REPLACE_ME` in final HTML
- [ ] `@media (max-width: 768px)` present
- [ ] `@media (prefers-reduced-motion: reduce)` present

### Nav
- [ ] Solid background — no `backdrop-filter: blur` (triggers `transparent_with_blur`)

### Hero
- [ ] No pill/chip/badge above H1 (triggers `hero_eyebrow_chip`)
- [ ] No overlapping avatar circles for trust (triggers `hero_avatar_stack`)
- [ ] Floating panel uses solid dark bg — no `backdrop-filter: blur` (triggers `glassmorphism`)
- [ ] Floating panel CSS classes do NOT contain substring "card" nested inside another card element (triggers `card_inside_card`)

### Icons
- [ ] Step/process icons are inline SVG — NO emoji 🔍📋🎓🏅 (triggers `oversized_emoji_as_icon`)

### Quotes/Cards
- [ ] No `border-inline-start: 3px solid` or thicker (triggers `side_tab_card_border`)
- [ ] Use CSS `::before` quote mark instead of side border

### Stats
- [ ] One stat cell has distinct visual treatment (triggers `stat_card_four_identical` if all identical)

### Content
- [ ] Logo is custom SVG geometric mark — NOT a single letter in a box
- [ ] Partner logos are inline SVG wordmarks — NOT plain text
- [ ] No generic placeholder text: "Item 1", "John Doe", "99%", "Company Name", "24/7"
- [ ] All copy is in the project's primary language — no unexplained language mixing in content
- [ ] Testimonial quotes reference a specific product/course/outcome, not generic praise
- [ ] Events and dates are specific and real (use correct future dates based on current date) — no "Coming soon" or TBD
- [ ] Focus states and aria-labels on all interactive elements
- [ ] No external CDN script tags

---

## Page-by-Page Blueprints

**Source of truth**: Page blueprints come from the project's `page-map.json` (or equivalent planning file), NOT from this SKILL.md. Read `page-map.json` to find the required sections, content types, and layout for each page.

If no `page-map.json` exists, read the project's `plan.md` or `spec.md` for the page list.

### How to Write a Blueprint

When you find a page to build in `page-map.json`, structure your implementation plan like this:

```
PAGE: [page-slug].html
Language/Direction: [lang="xx" dir="rtl/ltr"]
Layout: [public / admin-sidebar / standalone]

Required sections in order:
1. [Section name] — [brief description of purpose and key content]
2. [Section name] — [requirements]
...

Content to include (from page-map.json or plan.md):
- [Specific data points, names, dates that must appear — read from project source]
```

### Blueprint Rules (Apply to Every Page)

**Public pages**:
- ALWAYS start with `<!-- PARTIAL:nav-public -->` markers wrapped in `<header>` (do not hand-write the nav)
- ALWAYS end with `<!-- PARTIAL:footer-public -->` markers wrapped in `<footer>` (do not hand-write the footer)
- Content sections go in `<main id="main">`
- Language and direction attributes come from the project's language setting

**Admin pages**:
- ALWAYS include `<!-- PARTIAL:sidebar-admin -->` markers in `<aside class="sidebar">`
- Admin layout is LTR regardless of the project's public language
- Structure: `<aside>` sidebar + `<div class="admin-main">` with `.topbar` + `<main id="main">`

**All pages**:
- Skip link is the FIRST element in `<body>`
- `class="prototype-nav"` bar links to ALL project pages
- All 9 required CSS tokens present in inline `:root {}`

---

### PUBLIC PAGE: [page-slug].html — Generic Example

`lang="[project-lang]" dir="[rtl/ltr]"` | Hero: `[hero-type from design-system.json]`

**Required sections in order (read actual requirements from page-map.json):**

1. **Sticky Header** — uses `<!-- PARTIAL:nav-public -->` markers, DO NOT write nav HTML here
2. **Page Header / Hero** — H1 from page-map.json, breadcrumb if applicable, subtitle
3. **[Primary content type]** — grid / list / form / whatever the page requires. Read page-map.json for minimum item counts and specific data fields.
4. **[Secondary section]** — CTA strip, related items, or supporting content
5. **Footer** — uses `<!-- PARTIAL:footer-public -->` markers, DO NOT write footer HTML here

**Content to include**: Read from `page-map.json` or `plan.md` for this project. All content must be realistic and specific — no generic placeholders. See Content Rules below.

---

### ADMIN PAGE: [admin-page].html — Generic Example

`dir="ltr"` (Admin is always LTR regardless of public-facing language)

**Layout**: Fixed left sidebar + main content area (`.admin-main`)

**Required structure:**
```html
<body class="admin-body">
  <aside class="sidebar">
    <!-- PARTIAL:sidebar-admin -->
    <!-- /PARTIAL:sidebar-admin -->
  </aside>
  <div class="admin-main">
    <div class="topbar">...</div>
    <main id="main" class="page-main">
      <!-- Page content -->
    </main>
  </div>
</body>
```

**Required elements in main content:**
1. **Topbar** — breadcrumb + page title + action button (e.g. "+ Add [Entity]")
2. **[Primary interface]** — data table / form / grid (read page-map.json for the specific layout)
3. **[Supporting elements]** — filters, pagination, modals as needed

---

## Content Rules — No Placeholder Text

- No "Item 1", "Item 2" — use specific, realistic item names appropriate to the project domain
- No "John Doe", "Jane Smith" — use real-sounding full names in the project's language
- No "500+", "99%", "24/7", "#1 rated" — use specific verifiable numbers
- No "Lorem ipsum" or foreign-language placeholder text
- No "Coming soon", "Details TBD", "Information unavailable"
- No generic testimonials — quotes must reference a specific product, outcome, or experience
- Contact info: realistic format matching the project's region and conventions
- Unsplash images: use real known photo IDs, not made-up ones
- Dates: use real future dates based on today's date (2026-06-21), not "July 2026" vaguely

---

## Done When

- One `[slug].html` file exists for each page in the project's page list (check `page-map.json`)
- Every file links to `design-tokens.css` and is otherwise self-contained (no external CSS/JS except font services)
- Every file passes the anti-slop checker with exit code 0
- Logo is a custom SVG geometric mark on every page — NOT a single letter in a colored box
- Partner logos (if applicable) are inline SVG wordmarks with `role="img"` + `aria-label`
- Anti-slop checklist passes for every section on every page
- Public pages use correct language/direction per project settings; admin pages are always LTR
- Prototype nav links to ALL pages in the project's page list
- `index.html` (if included) lists all prototypes with working links
- `compile-partials.py` was run after all pages were created (to stamp shared nav/sidebar/footer)
