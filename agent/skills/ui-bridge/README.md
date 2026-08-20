# ui-generate-from-plan

> A multi-agent skill for Codex and Claude Code that turns **Spec Kit** planning artifacts (`plan.md` + `tasks.md`)
> into fully self-contained, production-quality HTML prototypes — backed by a
> 14-layer automated design system and enforced by 52 anti-slop rules.

---

## Installation

Install from your project root with:

```bash
npx skills add rakymat-plugins/ui-gernreate-from-plan --all
```

### Windows PowerShell note

If PowerShell blocks `npx` with `running scripts is disabled on this system`, use `npx.cmd` instead:

```powershell
npx.cmd skills add rakymat-plugins/ui-gernreate-from-plan --all
```

If you specifically want to use `npx` inside the current PowerShell session, you can temporarily allow local script execution for that session only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
npx skills add rakymat-plugins/ui-gernreate-from-plan --all
```

This does not change the machine-wide policy. You can also run the same command from `cmd.exe` instead of PowerShell.

### Windows

```powershell
git clone https://github.com/rakymat-plugins/ui-gernreate-from-plan.git
cd ui-gernreate-from-plan
.\install.ps1
```

### macOS / Linux

```bash
git clone https://github.com/rakymat-plugins/ui-gernreate-from-plan.git
cd ui-gernreate-from-plan
bash install.sh
```

This installs the skill globally and also adds the local project aliases used by Codex and Claude Code.

Then run these commands from the new project after Spec Kit has generated `plan.md` and `tasks.md`:

```text
$ui-plan
$ui-implement
$ui-link-html-to-plan
$ui-into-preview
```

---

## Repository and Project Links

| Area | Repository | Branch | Branch link |
|---|---|---|---|
| Skill source | `rakymat-plugins/ui-gernreate-from-plan` | `master` | https://github.com/rakymat-plugins/ui-gernreate-from-plan/tree/master |
| Current EdTech integration project | `yousefabdallah171/EdTech-platform` | `main` | https://github.com/yousefabdallah171/EdTech-platform/tree/main |

In the EdTech platform workspace, this skill is installed locally at:

```text
C:\Users\yosea\Desktop\projects\EdTech-platform\ui-gernreate-from-plan
```

It generates and links the project UI prototypes in:

```text
C:\Users\yosea\Desktop\projects\EdTech-platform\ui-prototypes
```

For the EdTech project, the active Spec Kit feature is:

```text
specs/001-edtech-marketing-crm
```

The approved UI artifacts for that project are:

- `.ui-bridge/page-map.md`
- `.ui-bridge/design-system.json`
- `.ui-bridge/link-report.md`
- `PRODUCT.md`
- `DESIGN.md`
- `ui-prototypes/*.html`

Keep skill changes on the skill repository branch and project changes on the platform repository branch.

---

## Canvas Preview Viewer

The canvas/offcanvas viewer is the presentation layer generated from this skill. It lets a project browse generated HTML pages inside a zoomable canvas with a left layers panel. It is separate from any mobile sidebar offcanvas inside a generated admin page.

### Source And Generated Locations

Skill source template:

```text
canvas-app/
```

Generated project copy:

```text
ui-preview/
  index.html             # Canvas viewer entry point
  server.py              # Local save/load server
  pages/                 # HTML pages shown inside the canvas
  manifest.json          # Page list and metadata
  canvas-state.json      # Saved positions, zoom, and layout state
```

For the current EdTech project:

```text
C:\Users\yosea\Desktop\projects\EdTech-platform\ui-preview
```

### Run The Viewer

Recommended mode, with save/load state:

```powershell
cd C:\Users\yosea\Desktop\projects\EdTech-platform\ui-preview
python server.py
```

Then open:

```text
http://localhost:5555
```

Direct mode, without save/load state:

```text
Double-click ui-preview/index.html
```

### How Pages Show Inside It

The viewer reads `ui-preview/manifest.json` and loads HTML from `ui-preview/pages/`. Click any page name in the left layers panel to show that page inside the canvas iframe.

To add a page manually:

1. Copy the HTML file into `ui-preview/pages/`.
2. Add the page entry to `ui-preview/manifest.json`.
3. Restart `python server.py` or refresh the browser.

### Clone Into Another Project

Install the skill once:

```powershell
git clone https://github.com/rakymat-plugins/ui-gernreate-from-plan.git
cd ui-gernreate-from-plan
git checkout master
.\install.ps1
```

On Mac or Linux:

```bash
git clone https://github.com/rakymat-plugins/ui-gernreate-from-plan.git
cd ui-gernreate-from-plan
git checkout master
bash install.sh
```

Then run these commands from the new project after Spec Kit has generated `plan.md` and `tasks.md`:

```text
$ui-plan
$ui-implement
$ui-link-html-to-plan
$ui-into-preview
```

This creates a fresh project-specific `ui-preview/` folder from `canvas-app/`.

### Phase 0-First Flow

`$ui-plan` now:

- creates `plan.md.backup` and `tasks.md.backup`
- creates archival copies in `.ui-bridge/backups/`
- writes `.ui-bridge/phase0-plan.md`
- writes `.ui-bridge/phase0-tasks.md`
- writes `.ui-bridge/phase0-plan.json` so `$ui-implement` follows the UI page order safely

`$ui-implement` now:

- works page by page in Phase 0 order
- scaffolds `ui-prototypes/design-tokens.css`
- scaffolds `ui-prototypes/_partials/`
- scaffolds `ui-prototypes/compile-partials.py`

Generated pages link `design-tokens.css`, copy the required root tokens inline, and use CSS variables so future color and brand changes cascade across the whole feature.

---

## What It Does

After `/speckit-tasks` produces your task list, this skill:

1. **Detects** project category, language, RTL direction, brand colors, and fonts automatically
2. **Resolves** a complete design system — typography, colors, images, icons, animations, layout, components — in 14 sequential inference layers
3. **Builds** `.ui-bridge/design-system.json` and `design-system.css` — the single source of truth for all visual decisions
4. **Finds** real-world design references from Dribbble, Behance, Mobbin, Refero, Awwwards, and more — so prototypes are inspired by actual high-quality UI, not AI defaults
5. **Generates** one fully self-contained HTML file per page — client-presentable, not wireframes
6. **Enforces** 52 forbidden design patterns across 8 categories and 17 required elements per file
7. **Links** every HTML prototype back into `tasks.md` so developers have a pixel-perfect reference for every frontend task

---

## Prerequisites

| Dependency | Required | Notes |
|---|---|---|
| Codex or Claude Code | Required | Codex uses `$ui-*` skills; Claude Code uses `/ui-*` commands |
| Python 3.8+ | Required | All scripts use stdlib only — zero `pip` dependencies |
| Node.js + npx | Optional | Only needed for `npx impeccable` validation step |
| Spec Kit | Required | `plan.md` + `tasks.md` must exist in the project |

---

## Installation

### One command (recommended)

```bash
npx skills add rakymat-plugins/ui-gernreate-from-plan --all
```

**Windows PowerShell:** if `npx` fails with a script execution policy error, run:

```powershell
npx.cmd skills add rakymat-plugins/ui-gernreate-from-plan --all
```

Temporary PowerShell-session workaround:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
npx skills add rakymat-plugins/ui-gernreate-from-plan --all
```

This downloads the skill, installs Claude command files into `~/.claude/commands/`,
installs Codex aliases into `~/.codex/skills/`, checks for Python 3, and installs
Impeccable if Node.js is available.

Then run these commands from the new project after Spec Kit has generated `plan.md` and `tasks.md`:

```text
$ui-plan
$ui-implement
$ui-link-html-to-plan
$ui-into-preview
```

---

### Manual — Mac / Linux

```bash
git clone https://github.com/rakymat-plugins/ui-gernreate-from-plan.git
cd ui-gernreate-from-plan
bash install.sh
```

---

### Manual — Windows

```powershell
git clone https://github.com/rakymat-plugins/ui-gernreate-from-plan.git
cd ui-gernreate-from-plan
.\install.ps1
```

---

### What the installer does

1. Copies skill files to `~/.claude/skills/ui-gernreate-from-plan/`
2. Copies skill files to `~/.codex/skills/ui-gernreate-from-plan/`
3. Installs `/ui-plan`, `/ui-implement`, `/ui-link-html-to-plan`, `/ui-into-preview` into `~/.claude/commands/`
4. Installs `$ui-plan`, `$ui-implement`, `$ui-link-html-to-plan`, `$ui-into-preview` into `~/.codex/skills/`
5. Installs local project aliases into `.claude/commands/` and `.codex/skills/`
6. Checks for Python 3.8+
7. Installs Impeccable via `npx impeccable install --providers=claude` (optional)

**After installation, restart your agent** to pick up the new commands or skills.

Codex invocations:

```text
$ui-plan
$ui-implement
$ui-link-html-to-plan
$ui-into-preview
```

---

## The 4 Commands

### `/ui-plan` — Discover pages and build the design system

Run **after** `/speckit-tasks` and **before** starting implementation.

```
/ui-plan
```

**What it does:**

1. Finds `plan.md` and `tasks.md` via Spec Kit artifact search
2. Runs `python scripts/run_detection.py` — 7-layer project detection
3. Runs `python scripts/infer_master.py` — 14-layer design system inference
4. Writes `visual-research.json` — real-world design references for the project category
5. Writes `PRODUCT.md` and `DESIGN.md` to the project root (Impeccable source files)
6. Builds `.ui-bridge/page-map.md` — every page with sections, direction, and API data needs
7. Inserts **Phase 0** into `plan.md` and `tasks.md` — one sub-phase per page, one task per section
8. Writes machine-readable Phase 0 order and reusable backup files for safe reruns

**Output files:**
```
.ui-bridge/
  design-system.json      ← complete resolved design system (14-layer output)
  design-system.css       ← ready-to-embed CSS with all tokens + keyframes
  visual-research.json    ← real-world design references + visual brief
  page-map.md             ← pages, slugs, sections, API data needs
  page-map.json           ← machine-readable page map
  brand-signals.json      ← raw detected colors + fonts
  parsed-speckit.json     ← parsed plan.md + tasks.md
  detection-report.json   ← full 7-layer detection result
PRODUCT.md                ← product descriptor (Impeccable input)
DESIGN.md                 ← design descriptor (Impeccable input)
```

---

### `/ui-implement` — Generate the HTML prototypes

Run **after** `/ui-plan`.

```
/ui-implement
```

**What it does:**

1. Reads `design-system.json` — ALL visual decisions come from here
2. Reads the `visual_brief` key — design feel, real product references, color rationale
3. Reads the stored Phase 0 order from `.ui-bridge/phase0-plan.json`
4. Scaffolds `design-tokens.css`, shared partials, and `compile-partials.py`
5. For each page: generates one fully self-contained HTML file in Phase 0 order
6. Applies the 52 anti-slop rules and required-elements checks on every file
7. Generates `ui-prototypes/index.html` — visual navigation index

**Every generated HTML file is:**
- Self-contained — all CSS and JS inline, zero internet required
- Production quality — real content, fully styled, every state defined
- Responsive — 375px mobile, 768px tablet, 1280px desktop breakpoints
- Impeccable-compliant — 52 forbidden patterns checked and blocked
- Arabic/RTL-ready — logical CSS properties, `dir="rtl"`, Cairo/Tajawal fonts when needed
- Interactive — hamburger menu, tabs, modals, forms via vanilla JS
- Diverse — 5+ page projects get unique hero patterns (no two pages share a pattern)

**Output files:**
```
ui-prototypes/
  index.html              ← prototype index, open in browser
  design-tokens.css       ← shared token file for all prototype pages
  _partials/              ← shared nav, footer, and sidebar fragments
  compile-partials.py     ← stamps shared partials into page markers
  [slug].html             ← one file per page
```

---

### `/ui-link-html-to-plan` — Link prototypes back into the plan

Run **after** `/ui-implement`.

```
/ui-link-html-to-plan
```

**What it does:**

1. Scans all `ui-prototypes/*.html` files
2. Matches each HTML file to its Phase 0 tasks in `tasks.md`
3. Marks matched Phase 0 tasks as complete `[x]`
4. Inserts **UI Reference blocks** into every matched frontend implementation task
5. Appends a **Prototype Index** to `plan.md`
6. Writes `.ui-bridge/link-report.md`

**UI Reference block example:**
```markdown
- [ ] T043 [US1] Create courses list page at apps/web/pages/courses/index.vue
  > **UI Reference**: `ui-prototypes/courses.html`
  > **Sections**: hero → `#hero`, course-grid → `#course-grid`, pagination → `#pagination`
  > **Design tokens**: Use the approved design-system artifact only
  > **Rule**: Match the HTML prototype exactly. Visual changes require client approval.
```

---

### `/ui-into-preview` — Build a deployable client preview

Run **after** `/ui-link-html-to-plan`.

```
/ui-into-preview
```

**What it does:**

1. Auto-detects `ui-prototypes/`, the active Spec Kit feature folder, and `.ui-bridge/page-map.json`
2. Builds `ui-preview/` with `index.html`, `manifest.json`, `canvas-state.json`, `pages/`, and `docs/`
3. Preserves existing canvas positions on rerun and appends only new pages
4. Produces an output folder ready for local review or GitHub Pages deployment

---

## Full Workflow

```
/speckit-constitution   →  Define project principles
/speckit-specify        →  Write spec.md
/speckit-plan           →  Generate plan.md, data-model.md, contracts/
/speckit-tasks          →  Generate tasks.md

         ↓
  ┌─────────────────┐
  │  /ui-plan       │  Reads: plan.md + tasks.md + source files
  │                 │  Runs: 14-layer design system inference
  │                 │  Writes: design-system.json, PRODUCT.md, DESIGN.md, page-map.md
  │                 │  Updates: plan.md + tasks.md (adds Phase 0)
  └────────┬────────┘
           ↓
  ┌────────────────────┐
  │  /ui-implement     │  Reads: design-system.json + page-map.md
  │                    │  Writes: ui-prototypes/*.html (one per page)
  │                    │  Enforces: 52 anti-slop rules per file
  └────────┬───────────┘
           ↓
  ┌──────────────────────────┐
  │  /ui-link-html-to-plan   │  Updates: tasks.md (UI Reference blocks)
  │                          │  Updates: plan.md (Prototype Index)
  └────────┬─────────────────┘
           ↓

/speckit-implement      →  Build the application using HTML as reference
```

---

## The 14-Layer Inference System

`infer_master.py` runs automatically during `/ui-plan`. It resolves all design
decisions in a fixed sequence — no layer can override a previous layer's output.

| Layer | Module | What It Resolves |
|---|---|---|
| 0 | `infer_engine.py` | Raw data collection — text lines + file contents across all extensions |
| 1 | `infer_engine.py` | Project type (EdTech, Fintech, Healthcare, SaaS, etc.) from 11 categories |
| 2 | `infer_engine.py` | Language detection — Arabic/RTL flag, effective category (`EdTech_Arabic`) |
| 3 | `infer_engine.py` | Brand color discovery — scans Tailwind config, CSS vars, hex literals |
| 4 | `infer_engine.py` | Font detection — Google Fonts imports, `font-family` declarations |
| 5 | `infer_engine.py` | Spec Kit artifact parsing — `plan.md`, `tasks.md`, page inventory |
| 6 | `infer_engine.py` | Brand policy state — strict intake, approved proposal, or unsafe fallback |
| 7 | `infer_typography.py` | Font pair recommendation — 6 type tiers, 11 category profiles, Arabic support |
| 8 | `infer_colors.py` | Full palette generation — primary, secondary, accent, neutrals, semantic colors as CSS vars |
| 9 | `infer_images.py` | Image strategy — 35 specific Unsplash photo IDs per category, CSS helpers |
| 10 | `infer_icons.py` | Icon set recommendation — Lucide / Heroicons / Phosphor per category |
| 11 | `infer_animations.py` | Animation profiles — 10 keyframes, utility classes, per-category easing |
| 12 | `infer_layout.py` | Header/footer patterns, page structure standards for 6 page types |
| 13 | `infer_components.py` | Component library — 16+ universal + category-specific HTML components |
| 14 | `infer_quality.py` + `visual_research.py` | Hero diversity engine (12 patterns), anti-slop enforcement, real design references |

**Key outputs from `design-system.json`:**

| JSON path | Used for |
|---|---|
| `category` | Page-type decisions, section ordering |
| `is_arabic` / `is_rtl` | `dir="rtl"`, logical CSS properties, Arabic font imports |
| `typography.font_pair` | Heading + body + display fonts with Google Fonts URL |
| `typography.css_variables` | `--font-heading`, `--font-body`, `--type-*` scale vars |
| `colors.palette` | All color roles with hex values |
| `colors.css_variables` | `--color-primary`, `--color-text-*`, `--color-bg-*` vars |
| `images.strategy` | Which Unsplash photo IDs to use by image type |
| `animations.profile` | Easing functions, durations, utility classes |
| `layout.header` | Header pattern type, logo/nav positions |
| `layout.page_structures` | Section order for each page type |
| `quality.hero_assignments` | Per-page slug → `{hero_pattern, gradient, description}` — MUST follow |
| `quality.section_assignments` | Per-page slug → section variant per section type |
| `quality.type_css` | Type-hierarchy CSS vars — paste verbatim |
| `visual_research.visual_brief` | Design feel, photography mood, typography personality |
| `visual_research.top_3_products` | Real products to match quality of |

---

## Anti-Slop System (52 Rules)

`anti_slop_database.py` encodes 52 forbidden patterns across 8 categories.
Every generated HTML file is checked against all 52 before it is returned.

| Category | Count | Example forbidden pattern |
|---|---|---|
| Colors | 9 | Purple-to-blue gradient as primary palette |
| Typography | 8 | `background-clip: text` gradient on headings |
| Layout | 12 | `.card` nested inside `.card` |
| Animations | 7 | Bounce / elastic keyframe (`cubic-bezier > 1.0`) |
| Content | 6 | `Lorem ipsum` placeholder text |
| Headers | 4 | Centered logo with centered nav |
| Footers | 2 | `border-top: 4px solid var(--color-primary)` accent strip |
| Sections | 4 | "How it works" with 3 numbered icon tiles |
| **Total** | **52** | |

**17 required elements** — every HTML file must include:
`design-system.css` embed, Google Fonts import, `--color-primary` var, `dir` attribute,
semantic heading hierarchy, `<nav>` landmark, skip link, viewport meta, lang attribute,
unique hero pattern, real content (no Lorem), `<footer>`, responsive breakpoints,
interactive JS, WCAG contrast, Unsplash-only images, and `<title>`.

---

## File Structure

```
ui-gernreate-from-plan/
│
├── SKILL.md                              ← Root skill router (Claude reads this)
├── package.json                          ← npm package manifest + skill metadata
├── requirements.txt                      ← Python stdlib only (no pip needed)
├── install.sh                            ← Mac/Linux installer
├── install.ps1                           ← Windows installer
│
├── .claude/
│   └── commands/
│       ├── ui-plan.md                    ← /ui-plan command definition
│       ├── ui-implement.md               ← /ui-implement command definition
│       └── ui-link-html-to-plan.md       ← /ui-link-html-to-plan command definition
│
├── subskills/
│   ├── ui-plan/SKILL.md                  ← Full /ui-plan logic
│   ├── ui-implement/SKILL.md             ← Full /ui-implement logic
│   └── ui-link/SKILL.md                  ← Full /ui-link-html-to-plan logic
│
├── scripts/
│   │
│   ├── ── Detection ──
│   ├── run_detection.py                  ← 7-layer project detection (runs first on every command)
│   ├── parse_speckit.py                  ← Find + parse plan.md and tasks.md
│   ├── extract_brand.py                  ← Discover brand signals from source files
│   ├── generate_page_map.py              ← Build .ui-bridge/page-map.md
│   ├── update_plan.py                    ← Safely insert Phase 0 into plan + tasks
│   ├── link_html.py                      ← Scan HTML + match to tasks
│   │
│   ├── ── Inference engine (14 layers) ──
│   ├── infer_master.py                   ← Orchestrator: runs all layers, writes design-system.json
│   ├── infer_engine.py                   ← Layers 0–6: detection, brand, fonts, pages, presets
│   ├── infer_typography.py               ← Layer 7: font pair + type scale CSS vars
│   ├── infer_colors.py                   ← Layer 8: full color palette + CSS custom properties
│   ├── infer_images.py                   ← Layer 9: Unsplash photo IDs + CSS image helpers
│   ├── infer_icons.py                    ← Layer 10: icon set recommendation per category
│   ├── infer_animations.py               ← Layer 11: animation profiles + keyframes + utilities
│   ├── infer_layout.py                   ← Layer 12: header/footer patterns + page structures
│   ├── infer_components.py               ← Layer 13: component library as HTML strings
│   ├── infer_quality.py                  ← Layer 14a: hero diversity + anti-slop enforcement
│   ├── anti_slop_database.py             ← Layer 14b: 52 forbidden patterns database
│   ├── visual_research.py                ← Layer 14c: real-world design references engine
│   │
│   └── install.js                        ← Node.js installer (used by npx skills add)
│
├── references/
│   ├── workflow-master.md                ← Single authoritative workflow reference
│   ├── html-standards.md                 ← HTML output rules + 46 anti-patterns
│   ├── impeccable-integration.md         ← Impeccable commands + 44 detector rules
│   ├── speckit-artifacts.md              ← How to parse plan.md and tasks.md
│   ├── brand-extraction.md               ← Brand signal discovery + industry defaults
│   ├── detection-layers.md               ← 7 detection layers documented
│   └── output-consistency.md             ← Cross-page consistency rules
│
├── templates/
│   ├── page.html                         ← Base HTML template with SECTION markers
│   ├── PRODUCT.md.template               ← Template for generated PRODUCT.md
│   └── DESIGN.md.template                ← Template for generated DESIGN.md
│
└── test-project/
    └── specs/001-test/
        ├── plan.md                       ← Example Spec Kit plan
        └── tasks.md                      ← Example Spec Kit task list
```

---

## Impeccable Integration

[Impeccable](https://impeccable.style) is the optional design-quality validation layer.
ui-generate-from-plan reads `PRODUCT.md` and `DESIGN.md` and applies all 44 detector
rules internally — even without Impeccable installed.

When Impeccable **is** installed, it adds structured CLI validation:

```bash
npx impeccable html validate ui-prototypes/courses.html
npx impeccable antipattern check ui-prototypes/courses.html
npx impeccable palette validate
```

To install Impeccable:

```bash
npx impeccable install --providers=claude
```

### What Impeccable validates (44 rules across 8 categories)

| Category | Rules | Examples |
|---|---|---|
| Color | 7 | No purple-to-blue gradient; no gradient text on headings |
| Typography | 6 | No display font for body; min 14px body; max 3 weights per component |
| Layout | 9 | No nested cards; hero overlay contrast ≥ 4.5:1; footer max 4 columns |
| Animation | 3 | No bounce keyframes; transitions ≤ 400ms |
| Interactive | 7 | Button padding min 12×24px; every input has `<label>`; min 44px tap targets |
| Hierarchy | 4 | Max 1 `.btn-primary` per viewport section; measurable elevation system |
| Accessibility | 4 | WCAG AA contrast (4.5:1 normal, 3:1 large text); all images have `alt` |
| Component | 4 | Modals ≤ 90vw mobile; empty states have CTA; border-radius ≤ 12px on cards |

See [references/impeccable-integration.md](references/impeccable-integration.md) for the
complete rule table with rule IDs and anti-pattern mappings.

### Standalone mode (no Node.js)

If Node.js is not available, the skill runs in standalone mode:
- `/ui-plan` still runs all 14 inference layers and writes `design-system.json`
- `/ui-implement` still generates full production-quality HTML
- All 52 anti-slop rules still apply (enforced by the generating AI)
- The only difference: no `impeccable html validate` CLI step at the end

Standalone mode produces identical output quality. Impeccable CLI adds repeatable
machine-checkable validation — useful in CI, not required for one-off generation.

---

## The Design Reference Database

`visual_research.py` contains curated design references for 11 project categories:

| Category | Inspiration sources | Real products |
|---|---|---|
| EdTech | Dribbble, Mobbin, Refero (Coursera/Duolingo), Land-book | Coursera, Kajabi, Maven, Teachable |
| SaaS Dashboard | Lapa Ninja, Godly, Refero (Linear/Vercel), UI Sources | Linear, Stripe, Resend, Raycast |
| E-commerce | Shopify Theme Store, Awwwards, Screenlane | Allbirds, Glossier, ASOS |
| Booking Platform | Refero (Calendly), Pageflows, Mobbin | Calendly, Cal.com, Acuity |
| Healthcare | Mobbin, Awwwards, Themeforest | One Medical, Zocdoc, Hims |
| Fintech | Mobbin (Stripe/Wise/Brex), Godly, Lapa | Stripe, Mercury, Wise |
| Travel/Hospitality | Awwwards, Godly, Themeforest | Airbnb, Klook, Inspirato |
| Food & Beverage | Awwwards, Godly, Themeforest | Sweetgreen, Noma, Chipotle |
| Real Estate | Awwwards, Godly, Themeforest | Compass, Zillow, Sotheby's |
| Creative Agency | Awwwards, Godly, SiteInspire | Pentagram, Fantasy, Ragged Edge |
| Marketing/CRM | SaaS Landing Page, Lapa, Mobbin | HubSpot, Mailchimp, Close |

Each category includes:
- Color palettes that work (with hex values + rationale)
- Typography pairs that work (with personality notes)
- Hero patterns from real sites (not AI defaults)
- Section patterns that work (category-specific)
- Visual DNA — feel, NOT feel, whitespace, image mood, interaction feel

---

## Troubleshooting

### "No Spec Kit artifacts found"

The skill searches for `plan.md` and `tasks.md` in:
1. Current directory
2. `specs/*/plan.md` and `specs/*/tasks.md`
3. `.specify/feature.json` → feature directory
4. Any subdirectory up to 4 levels deep

**Fix:** Run `/speckit-plan` and `/speckit-tasks` first, then run `/ui-plan` from the project root.

---

### "Phase 0 already exists in plan.md"

The skill now replaces stale UI Phase 0 content instead of forcing manual cleanup.

**Fix:** Re-run `/ui-plan`. It refreshes Phase 0, writes fresh backups to `plan.md.backup` and `tasks.md.backup`, and also stores archive copies in `.ui-bridge/backups/`.

---

### "0 pages found"

Page detection looks for `pages/*.vue` patterns in `tasks.md`.

**Fix:** Check that `tasks.md` has task lines with paths like:
```
- [ ] T043 [US1] Create courses page at apps/web/pages/courses/index.vue
```
If your framework uses `src/views/`, edit `scripts/parse_speckit.py` → `page_patterns` list.

---

### HTML prototypes look generic / wrong colors

Brand signal extraction found no project-specific colors.

**Fix:** Edit `.ui-bridge/design-system.json` → `colors.palette` with correct hex values,
or edit `DESIGN.md` directly, then re-run `/ui-implement`.

---

### Arabic text renders incorrectly

**Fix:** Ensure every Arabic page has:
1. `<html dir="rtl" lang="ar">` on the root element
2. Cairo or Tajawal `@import` inside `<style>` (not as a `<link>` tag)
3. All directional CSS uses logical properties: `margin-inline-start` not `margin-left`

---

### Two pages got the same hero pattern

**Fix:** The diversity engine enforces unique hero patterns for 5+ page projects.
If you see a warning in the `/ui-plan` output, check `quality.hero_assignments` in
`design-system.json` — the engine should have already assigned distinct patterns.
If not, run `/ui-plan` again to regenerate assignments.

---

## License

MIT — use freely in any project, commercial or otherwise.

---

*Part of the Spec Kit → UI → Implementation workflow.*
*For Spec Kit skills, see [yousefabdallah171/speckit](https://github.com/yousefabdallah171).*
