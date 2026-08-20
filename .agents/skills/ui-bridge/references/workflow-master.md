# UI Bridge — Master Workflow Reference

This file is the single source of truth for how ui-bridge works.
Every subskill SKILL.md defers to this document for sequencing,
decision logic, and quality standards.

---

## The Three Commands — What Each One Does

---

### COMMAND 1 — /ui-plan

**Trigger**: User runs /ui-plan after speckit.tasks is complete
**Duration**: Fast — no HTML generated
**Output**: Updated plan.md, updated tasks.md, .ui-bridge/ folder initialized

#### Full Step Sequence

STEP 1 — PRE-FLIGHT DETECTION
Run: python scripts/run_detection.py --command ui-plan
Read: .ui-bridge/detection-report.json
Must pass before anything else runs.
If layer_1 status is not "ok" → stop and show error message.
Print the detection summary box.

STEP 2 — SPECKIT ARTIFACT PARSING
Run: python scripts/infer_engine.py --infer speckit --root .
Read parsed data from .ui-bridge/infer-results.json
Extract:
  - Exact path to plan.md
  - Exact path to tasks.md
  - Project name (first H1 in plan.md or metadata table)
  - All phase names
  - All user stories
  - All task IDs (T001, T002 etc.)
  - All file paths mentioned in tasks
  - All page names mentioned anywhere

STEP 3 — PROJECT IDENTITY RESOLUTION
Run: python scripts/infer_master.py --root .
This runs all 8 infer scripts in sequence.
Reads detection-report.json + infer-results.json
Resolves final values for everything:
  - project_category (from ProjectTypeInferrer)
  - is_arabic, is_rtl (from LanguageInferrer)
  - type_tier with font pair (from TypeHierarchyEngine)
  - complete color palette (from ColorCombinationEngine)
  - image strategy (from ImageStrategyRecommender)
  - icon set (from IconSystemRecommender)
  - animation profile (from AnimationRecommender)
  - header pattern + footer pattern (from LayoutRecommender)
  - component library (from ComponentLibraryBuilder)
  - hero assignment per page (from HeroVariationEngine)
  - section variants per section type (from SectionVariationEngine)
Saves: .ui-bridge/design-system.json
Saves: .ui-bridge/design-system.css
Saves: .ui-bridge/PRODUCT.md (copy to project root)
Saves: .ui-bridge/DESIGN.md (copy to project root)

STEP 4 — PAGE MAP GENERATION
Run: python scripts/generate_page_map.py --root .
For every unique page found in plan.md and tasks.md:
  Generate:
    name: human readable
    slug: lowercase-hyphenated (used as filename)
    route: the actual URL route (/courses, /admin/dashboard etc.)
    source_tasks: list of task IDs that build this page
    hero_pattern: assigned hero variant from HeroVariationEngine
    section_order: ordered list of sections for this page
    estimated_sections: count
    image_needs: list of image slots with their Unsplash photo IDs
    is_admin: true if route starts with /admin
    page_type: landing | listing | detail | dashboard | auth | profile | other

Page type determines section_order:
  landing:   hero, logos, features, how-it-works, testimonials, pricing, faq, cta, footer
  listing:   page-header, filters, results-grid, empty-state, pagination, footer
  detail:    breadcrumb, detail-hero, tabs, main-content, sidebar, related, footer
  dashboard: stats-bar, main-chart, data-table, secondary-metrics, activity-feed
  auth:      centered-card with logo, form, social-proof below
  profile:   cover, avatar-strip, stats, tabs, content, sidebar

Saves: .ui-bridge/page-map.md (human readable)
Saves: .ui-bridge/page-map.json (machine readable)

STEP 5 — PHASE 0 GENERATION
Read: .ui-bridge/page-map.json
Generate Phase 0 structure:

  Each sub-phase = one page from page-map
  Each task in sub-phase = one section on that page
  Task IDs: T0-001, T0-002 etc. (T0 prefix, never conflicts with real tasks)

  Sub-phase naming: "Phase 0.N — [Page Name] ([slug].html)"
  Task naming: "T0-NNN Create [section-name] section — [one sentence description]"

Phase 0 tasks also carry metadata comments:
  # hero-pattern: split-image-right
  # image: EdTech_hero
  # section-variant: none (hero is always unique)
  # animation: fade-slide-up

STEP 6 — PLAN AND TASKS UPDATE
Run: python scripts/update_plan.py
Creates backups: plan.md.bak, tasks.md.bak
Inserts Phase 0 into plan.md BEFORE ## Phase 1
Inserts Phase 0 tasks into tasks.md BEFORE ## Phase 1 section
Never modifies any existing content — only inserts

STEP 7 — IMPECCABLE SETUP
Check if PRODUCT.md exists in project root.
If not: copy from .ui-bridge/PRODUCT.md to project root.
Check if DESIGN.md exists in project root.
If not: copy from .ui-bridge/DESIGN.md to project root.
Check if impeccable is installed.
If not: run: npx impeccable install --providers=claude

STEP 8 — SUMMARY OUTPUT
Print:
  ✓ Project identified: [name] ([category])
  ✓ Design system generated: [type_tier] fonts + [primary_color] palette
  ✓ [N] pages mapped → [N] Phase 0 sub-phases created
  ✓ [N] Phase 0 tasks added to tasks.md
  ✓ plan.md updated (backup at plan.md.bak)
  ✓ Impeccable configured

  Pages to prototype:
  [table of all pages with slug, type, section count, hero pattern]

  Next: run /ui-implement

---

### COMMAND 2 — /ui-implement

**Trigger**: User runs /ui-implement after /ui-plan completes
**Duration**: Slow — one HTML file per page
**Output**: ui-prototypes/ folder with one .html file per page + index.html

#### Full Step Sequence

STEP 1 — PRE-FLIGHT
Run: python scripts/run_detection.py --command ui-implement
Check .ui-bridge/page-map.json exists → if not: "Run /ui-plan first"
Check .ui-bridge/design-system.json exists → if not: "Run /ui-plan first"
Check ui-prototypes/ exists → create if missing
Check .ui-bridge/used-patterns.json → create empty if missing

STEP 2 — LOAD DESIGN SYSTEM
Read .ui-bridge/design-system.json COMPLETELY before writing any HTML.
Extract and hold in memory for all pages:
  type_tier → { google_fonts_url, font vars, scale vars }
  color_system → { all --color-* vars, tint scales }
  gradient_styles → { name: css_value for each permitted gradient }
  animation_profile → { duration, easing, hover_lift, keyframes }
  icon_set → { cdn_url, size, style }
  header_pattern → { style, height, position, nav_links }
  footer_pattern → { style, columns, newsletter }
  hero_assignments → { slug: pattern_name }
  section_variants → { section_type: variant_name }
  image_strategy → { category specific photo IDs }
  component_library → { component_name: html_string }

STEP 3 — GENERATE BASE CSS BLOCK
Before any page, generate the shared CSS block that goes into every file.
This is generated ONCE and reused — never regenerated per page.

The base CSS block contains IN THIS ORDER:
  1.  Google Fonts @import (from type_tier.google_fonts_url)
  2.  :root { all --color-* variables }
  3.  :root { all --font-* variables }
  4.  :root { all --text-* size variables using clamp() }
  5.  :root { all --weight-* variables }
  6.  :root { all --leading-* variables }
  7.  :root { all --tracking-* variables }
  8.  :root { all --space-* variables }
  9.  :root { all --radius-* variables }
  10. :root { all --duration-* and --ease-* variables }
  11. CSS reset (box-sizing, margin, padding, font inheritance)
  12. Base element styles (body, h1-h6, p, a, img, ul, button)
  13. Layout utilities (.container, .section, .grid-2, .grid-3, .grid-4)
  14. Typography utilities (.text-display, .text-h1 etc.)
  15. Button components (.btn-primary, .btn-secondary, .btn-ghost, .btn-danger)
  16. Card component (.card, .card-hover)
  17. Badge component (.badge, .badge-success etc.)
  18. Form components (.input, .select, .textarea, .checkbox, .radio)
  19. Avatar component (.avatar-sm through .avatar-xl)
  20. Navigation component (.nav, .nav__logo, .nav__links, .nav__cta)
  21. Footer component (.footer, .footer__grid, .footer__bottom)
  22. Prototype navigation pill (.prototype-nav)
  23. All @keyframes needed by animation profile
  24. Animation utility classes (.animate-fade-in etc.)
  25. Skeleton loading (.skeleton)
  26. Image utilities (.img-cover, .img-circle etc.)
  27. Responsive breakpoints (1024px, 768px, 480px)
  28. RTL overrides if is_arabic (all directional overrides)
  29. prefers-reduced-motion override

STEP 4 — PROCESS EACH PAGE (one at a time, in order)

For each page in .ui-bridge/page-map.json:

  4a. ANNOUNCE: print "Building [page_name] → ui-prototypes/[slug].html"

  4b. LOAD PAGE DATA
    Read from page-map.json:
      hero_pattern assigned to this slug
      section_order for this page_type
      image_needs for this page
      source_tasks that describe what goes on this page
    Read matching task descriptions from tasks.md for content guidance

  4c. GENERATE REALISTIC CONTENT
    NEVER use Lorem ipsum
    NEVER use "Title Here" or "Description goes here"
    Use content appropriate to project category and page purpose:

    For EdTech course listing:
      Use real course names: "Advanced Project Management", "Data Analysis with Python"
      Use real instructor names: "Dr. Ahmed Hassan", "Sarah Mitchell"
      Use real prices: "$299", "$149"
      Use real durations: "8 weeks", "32 hours"
      Use real levels: "Intermediate", "Beginner"

    For booking platform:
      Use real service names, real expert names, real time slots
      Use real prices and session durations

    For e-commerce:
      Use real product names, real prices with sale prices
      Use real product descriptions, real specifications

    Content must read like it came from the actual business,
    not from a template or AI placeholder.

  4d. GENERATE HTML STRUCTURE
    Start with this exact doctype and html tag:
      <!DOCTYPE html>
      <html dir="[rtl if arabic else ltr]" lang="[ar if arabic else en]">

    Head section contains:
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <meta name="description" content="[page-specific description]">
      <title>[Page Name] — [Project Name]</title>
      <style>
        [FULL BASE CSS BLOCK from Step 3]
        [PAGE-SPECIFIC CSS for this page only]
      </style>

    Body structure:
      <!-- SECTION: navigation -->
      [header HTML using header_pattern from design-system]

      <!-- SECTION: hero -->
      [hero HTML using hero_assignments[slug] pattern]
      [with Unsplash images from ImageIntegrationHelper]

      <!-- SECTION: [section-name] -->
      [each section in section_order with assigned variant]

      <!-- SECTION: footer -->
      [footer HTML using footer_pattern from design-system]

      <!-- SECTION: prototype-nav -->
      <a href="index.html" class="prototype-nav">← All Prototypes</a>

      <script>
        [hamburger menu JS]
        [scroll reveal JS if animation profile has scroll_reveal: true]
        [number counting JS if profile has number_counting: true]
        [any other minimal vanilla JS needed for this page]
      </script>

  4e. GENERATE HEADER HTML
    Use header_pattern from design-system.json
    Logo: project name as text logo (styled with --font-heading, --color-primary)
    Nav links: from header_pattern.nav_links (in Arabic if is_arabic)
    CTA: from header_pattern.cta_text
    Mobile: hamburger icon that toggles .nav--open class

  4f. GENERATE HERO HTML
    Pattern: from hero_assignments[slug]
    Get pattern definition from HeroVariationEngine.HERO_PATTERNS
    Generate the HTML structure for that specific pattern
    Inject Unsplash image URL using ImageIntegrationHelper.get_url()
      using the correct photo_id for this page category
    Apply hero-specific CSS using design system variables only
    Apply hero entrance animation from animation_profile

  4g. GENERATE EACH SECTION
    For each section in section_order:
      Get variant from section_variants[section_type]
      Check .ui-bridge/used-patterns.json — if variant used before on this project:
        pick next available variant for this section type
        update used-patterns.json
      Generate HTML for this section variant
      Use realistic content (not placeholders)
      Use images where needed: generate img tags with Unsplash URLs
      Apply section-specific CSS using design system variables only
      Add scroll reveal class if animation profile enables it

    Section content guidelines per type:

    FEATURES SECTION:
      3-6 features (not more)
      Each feature: icon (inline SVG from icon set) + heading + 2-line description
      Heading: describes the benefit not the feature name
      Description: one specific outcome not a vague claim

    TESTIMONIALS SECTION:
      3-6 testimonials
      Each: real-sounding name + real job title + real company name
      Quote: specific outcome not generic praise
      "Reduced our onboarding time by 40%" not "Great product!"
      Stars: 4 or 5 (never all 5 if it looks fake)
      Avatar: Unsplash person photo via ImageIntegrationHelper.get_avatar_url()

    STATS SECTION:
      4 stats maximum
      Use realistic numbers appropriate to project scale
      EdTech: "12,000+ Students", "94% Completion Rate", "4.8/5 Rating", "120 Courses"
      E-commerce: "50K+ Products", "99.9% Uptime", "4.9 Star Rating", "2M+ Orders"
      Numbers must tell a coherent story

    PRICING SECTION:
      2-3 tiers maximum
      Use realistic prices for the market
      Middle tier: mark as "Most Popular" with visual highlight
      Feature list: 5-8 items, some crossed out on lower tier

    FAQ SECTION:
      6-8 questions
      Questions must be real questions the target audience asks
      Answers: 2-4 sentences, specific and helpful

    CTA SECTION:
      One clear primary action
      One supporting line of context
      Optional: email input for newsletter/waitlist

  4h. GENERATE FOOTER HTML
    Use footer_pattern from design-system.json
    Columns: as defined in footer_pattern.columns
    Bottom bar: copyright + privacy + terms links
    Logo: same as header
    Newsletter: if footer_pattern.newsletter is true, include email form
    Social icons: inline SVGs for Twitter/X, LinkedIn, Instagram, YouTube
      (use whichever 3-4 are most relevant for the project type)

  4i. ANTI-SLOP CHECK
    Run AntiSlopEnforcer.check(html_content)
    If violations: fix each one before saving
    If missing required elements: add them
    Print: "✓ Anti-slop check passed" or list of fixed issues

  4j. WRITE FILE
    Write to ui-prototypes/[slug].html
    Print: "✓ [slug].html — [section_count] sections — [file_size]KB"

STEP 5 — GENERATE INDEX.HTML
After all page files are written:

Generate ui-prototypes/index.html:
  This is the prototype navigation hub
  Uses full design system (same CSS block as all pages)
  Hero: simple centered — "UI Prototypes — [Project Name]"
  Main content: card grid showing all prototypes

  Each prototype card shows:
    Page name (styled heading)
    Route (/courses, /admin/dashboard etc.)
    Page type badge (landing, listing, detail etc.)
    Section count
    Hero pattern used
    "View Prototype →" link

  Cards grouped in sections:
    "Public Pages" — all non-admin pages
    "Admin Pages" — all /admin/* pages
    "Auth Pages" — login, register, reset

  Progress indicator:
    "X of Y pages prototyped"

  Quick stats strip:
    Total pages | Total sections | Design tier | Primary color swatch

  Prototype nav pill: NOT on index (it IS the index)

STEP 6 — FINAL SUMMARY
Print:
  ════════════════════════════════════════
  UI Prototypes Complete
  ════════════════════════════════════════
  Pages generated: [N]
  Total sections:  [N]
  Design tier:     [type_tier name]
  Hero patterns used: [list]
  Section variants used: [list]

  Files:
  [list every file with size]

  Next: run /ui-link-html-to-plan
  ════════════════════════════════════════

---

### COMMAND 3 — /ui-link-html-to-plan

**Trigger**: User runs /ui-link-html-to-plan after /ui-implement
**Duration**: Fast — modifies text files only
**Output**: Updated tasks.md with UI references, link report

#### Full Step Sequence

STEP 1 — PRE-FLIGHT
Run: python scripts/run_detection.py --command ui-link
Check ui-prototypes/ has .html files → if empty: "Run /ui-implement first"
Check plan.md and tasks.md paths from detection-report.json

STEP 2 — SCAN ALL HTML FILES
Run: python scripts/link_html.py
For each .html file in ui-prototypes/ (skip index.html):
  Extract:
    Page title (from <title> tag)
    All section IDs (all id="" attributes)
    All <!-- SECTION: name --> comments
    Component class names that indicate major sections
    Approximate section count
  Build section map saved to .ui-bridge/task-html-map.json

STEP 3 — MATCH TASKS TO PAGES
For each task in tasks.md:
  Extract file path from task description
  Match to HTML file by:
    Route matching: pages/courses/index.vue → courses.html
    Name matching: "admin dashboard" → admin-dashboard.html
    Fuzzy matching: any significant word overlap
  Find the specific section that matches this task:
    "Create CourseCard component" → courses.html #course-grid section
    "Create registration form" → register.html #registration-form section

STEP 4 — UPDATE TASKS.MD
For each matched task, add UI Reference block immediately after the task line:
  Format:
    - [ ] T043 [US1] Create courses list page at apps/web/pages/courses/index.vue
      ↳ **UI Reference**: `ui-prototypes/courses.html`
      ↳ **Match section**: `#course-grid` (course listing grid, 3-col responsive)
      ↳ **Design tokens to use**:
        - Primary color: `var(--color-primary)` = [value from design-system]
        - Heading font: `var(--font-heading)` = [value]
        - Card radius: `var(--radius-lg)` = [value]
      ↳ **Implementation rule**: Match this HTML exactly.
        Copy the CSS patterns. Do not restyle. Do not change spacing.
        Every design decision is already made in this file.

STEP 5 — UPDATE PLAN.MD ARCHITECTURE SECTION
Find the "Technical Architecture" or "Project Structure" section in plan.md
Add after it:

  ## UI Prototype Reference

  All frontend pages MUST match ui-prototypes/ exactly.
  Visual changes require explicit client approval before implementation.

  | Page | Prototype | Type | Sections | Hero Pattern |
  |------|-----------|------|----------|--------------|
  [one row per page]

  Design system source: `.ui-bridge/design-system.json`
  CSS source: `.ui-bridge/design-system.css`
  Fonts: [google fonts URL]
  Colors: primary=[value] secondary=[value] accent=[value]

STEP 6 — GENERATE LINK REPORT
Write .ui-bridge/link-report.md:
  Total tasks updated: N
  Total pages linked: N
  Tasks with strong match (route match): N
  Tasks with fuzzy match: N
  Tasks with no match (need manual review): list them
  HTML pages with no matching tasks: list them (may be extra pages)

STEP 7 — FINAL SUMMARY
Print:
  ✓ [N] tasks updated with UI references
  ✓ [N] pages linked
  ✓ Link report: .ui-bridge/link-report.md
  Tasks needing manual review: [N] (see link-report.md)

  The developer now has:
  - Complete HTML prototypes in ui-prototypes/
  - Every task linked to its exact HTML section
  - Design tokens documented inline per task
  - A design-system.css to import in the real app

  Next: run /speckit.implement

---

## Quality Standards — What "Good Output" Means

### Typography Quality Checklist
Every generated page must pass these checks:

- [ ] Uses exactly the assigned type_tier font pair — no other fonts
- [ ] Display text uses --font-display and --weight-display
- [ ] H1 uses size between clamp(2rem,4vw,3.5rem) and clamp(3rem,6vw,5rem)
- [ ] Body text is never smaller than --text-sm (0.875rem)
- [ ] Line height on body text is never below 1.55
- [ ] Letter spacing on body text is 0em or at most 0.01em
- [ ] Heading hierarchy is sequential (h1 → h2 → h3 never skips)
- [ ] No heading uses letter-spacing above 0.05em
- [ ] Labels use uppercase only when --text-xs size or smaller
- [ ] Maximum 3 font weights used on any single page
- [ ] Font sizes change by at least 1.25x ratio between adjacent levels

### Color Quality Checklist
- [ ] All colors use var(--color-*) never hardcoded hex values
- [ ] Primary color covers max 15% of page visible area
- [ ] No text uses gray below #555 on white background
- [ ] No text uses any color on a background with less than 4.5:1 contrast
- [ ] Gradient is used in maximum 2 places per page
- [ ] No full-page or section background uses primary-to-secondary gradient
- [ ] Cards use --color-surface and --color-border only
- [ ] Error states always use --color-error never orange or yellow
- [ ] Success states always use --color-success
- [ ] Focus states always visible (outline or box-shadow using primary color)

### Layout Quality Checklist
- [ ] .container has max-width 1200px and horizontal padding
- [ ] No element uses a fixed pixel width above 800px
- [ ] All grids collapse correctly at 768px
- [ ] Navigation collapses to hamburger at 768px
- [ ] No card is nested inside another card
- [ ] Sections have consistent vertical padding (--space-20 default)
- [ ] Page has clear visual hierarchy: hero > main sections > supporting > footer
- [ ] No section uses the same layout pattern as the immediately adjacent section
- [ ] At least 3 visual rhythm breaks per page (background color changes or patterns)

### Image Quality Checklist
- [ ] Every img tag has a meaningful alt attribute
- [ ] Every img tag has loading="lazy" except above-fold images (loading="eager")
- [ ] Every img tag has explicit width and height attributes
- [ ] Hero images use Unsplash URLs with w=1200 minimum
- [ ] Card images use Unsplash URLs with w=600
- [ ] Avatars use pravatar.cc with specific seed numbers
- [ ] No page uses more than 2 images from the same Unsplash photo ID
- [ ] No placeholder text appears in alt attributes

### Animation Quality Checklist
- [ ] All transitions use var(--duration-base) and var(--ease-primary)
- [ ] No animation uses bounce, elastic, or spring easing
- [ ] Hover effects only use transform and opacity (never width/height/margin)
- [ ] Hover lift uses exactly var(--hover-lift) value from animation profile
- [ ] Scroll reveal uses IntersectionObserver with threshold 0.15
- [ ] Skeleton loading used on all listing pages
- [ ] prefers-reduced-motion override present and functional
- [ ] No animation loops infinitely except loading spinners and skeletons
- [ ] All interactive elements have :focus-visible styles

### Content Quality Checklist
- [ ] Zero Lorem ipsum instances anywhere
- [ ] Zero "Title Here" or "Description goes here" instances
- [ ] Zero emoji used as UI elements (🚀 ⚡ 💡 etc.)
- [ ] All numbers are realistic for the project scale
- [ ] All names sound like real people (not "John Doe" or "User Name")
- [ ] All company names are plausible (not "Acme Corp" or "Example Inc")
- [ ] All prices are realistic for the market
- [ ] All dates are in the future (for upcoming events/courses)
- [ ] CTA button text is specific ("Start Learning" not "Click Here")
- [ ] Error messages are helpful ("Email already registered" not "Error 422")

### Diversity Quality Checklist
- [ ] No two pages use the same hero pattern
- [ ] No two adjacent sections use the same background color
- [ ] Feature sections use at least 2 different layouts across pages
- [ ] Testimonials use at least 2 different layout variants across pages
- [ ] Images are different on every page (no duplicate Unsplash IDs)
- [ ] Avatar photos are different for every person shown
- [ ] Section ordering is not identical on any two pages

---

## Decision Log — What Gets Decided Automatically

These decisions are made by infer_master.py with no human input:

| Decision | How decided | Where stored |
|----------|-------------|--------------|
| Project category | Keyword scoring in ProjectTypeInferrer | detection-report.json |
| Language/RTL | Unicode range check in LanguageInferrer | detection-report.json |
| Font tier | Category + existing fonts in TypeHierarchyEngine | design-system.json |
| Primary color | Existing code → preset by category | design-system.json |
| Tint scales | HSL calculation from primary | design-system.json |
| Hero per page | Category + page index in HeroVariationEngine | design-system.json |
| Section variants | Type + used-set in SectionVariationEngine | used-patterns.json |
| Image photo IDs | Category + page type in ImageIntegrationHelper | design-system.json |
| Animation profile | Category in AnimationRecommender | design-system.json |
| Header pattern | Category in LayoutRecommender | design-system.json |
| Footer pattern | Category in LayoutRecommender | design-system.json |
| Page type | Page name + sections in LayoutRecommender | page-map.json |
| Section order | Page type in PAGE_STRUCTURE_STANDARDS | page-map.json |

---

## Error Recovery Guide

### "No speckit artifacts found"
Cause: plan.md and tasks.md don't exist yet
Fix: run /speckit.plan then /speckit.tasks first

### "Page map is empty"
Cause: No page paths found in plan.md and tasks.md
Fix: Check plan.md has actual page descriptions
Check tasks.md has file paths like pages/*.vue

### "Design system missing font"
Cause: type_tier selection failed
Fix: python scripts/infer_engine.py --infer project_type --root .
Check .ui-bridge/infer-results.json for project_type.category

### "Anti-slop check failed"
Cause: Generated HTML contains forbidden patterns
Fix: The engine auto-fixes these — check console for what was fixed
If persists: check infer_quality.py AntiSlopEnforcer patterns

### "All hero patterns are the same"
Cause: HeroVariationEngine not finding category matches
Fix: Check design-system.json hero_assignments section
Manual fix: edit .ui-bridge/design-system.json hero_assignments

### "Images not loading"
Cause: Unsplash URLs changed or rate limited
Fix: Open image URL directly in browser
Alternative: images.unsplash.com is reliable but may need ?auto=format appended

### "Arabic text not rendering"
Cause: Cairo font not loaded or dir attribute missing
Fix: Check <html dir="rtl" lang="ar"> on html tag
Check Google Fonts URL includes Cairo font family

---

## File State After Each Command

### After /ui-plan
```
.ui-bridge/
  detection-report.json   ← layer results
  infer-results.json      ← all inference data
  design-system.json      ← complete design decisions
  design-system.css       ← complete CSS ready to embed
  page-map.md             ← human readable page list
  page-map.json           ← machine readable page list
  brand-decisions.md      ← documented rationale
  PRODUCT.md              ← for Impeccable
  DESIGN.md               ← for Impeccable
PRODUCT.md                ← copied to root for Impeccable
DESIGN.md                 ← copied to root for Impeccable
plan.md                   ← Phase 0 prepended (backup: plan.md.bak)
tasks.md                  ← Phase 0 tasks prepended (backup: tasks.md.bak)
```

### After /ui-implement
```
ui-prototypes/
  index.html              ← navigation hub
  [slug].html             ← one per page
  ...
.ui-bridge/
  used-patterns.json      ← tracks which variants were used
```

### After /ui-link-html-to-plan
```
.ui-bridge/
  task-html-map.json      ← task to HTML section mapping
  link-report.md          ← coverage report
tasks.md                  ← UI Reference blocks added to each task
plan.md                   ← UI Prototype Reference section added
```

---

## Section Order Standards

### For Landing Pages (home, about, services):
1. Navigation (sticky, 64-72px)
2. Hero (full-impact, uses assigned hero pattern)
3. Social proof logos strip (client/partner logos, light background)
4. Primary value proposition (features, 3-4 items max)
5. How it works (3 steps, only if product needs explanation)
6. Showcase (product screenshots, or portfolio grid, or course examples)
7. Testimonials (social proof with real quotes)
8. Pricing or Plans (if applicable)
9. FAQ accordion (6-8 items)
10. Final CTA (email signup or primary action)
11. Footer (full footer)

### For Listing Pages (courses, products, experts, properties):
1. Navigation
2. Page header (h1 + breadcrumb + result count + sort)
3. Filter bar (horizontal) or filter sidebar
4. Results grid (with skeleton loading states shown)
5. Pagination
6. Empty state design (no results found)
7. Footer (simplified)

### For Detail Pages (course detail, product detail, expert profile):
1. Navigation
2. Breadcrumb
3. Detail hero (image + title + key metadata + primary CTA)
4. Tab navigation (Overview, Curriculum, Instructor, Reviews)
5. Tab content — Overview: full description + objectives + audience
6. Tab content — Curriculum: collapsible sections
7. Tab content — Instructor: mini profile
8. Tab content — Reviews: review list with summary
9. Related items (3-4 cards)
10. Sticky bottom bar on mobile (price + CTA)
11. Footer

### For Dashboard Pages (admin, analytics):
1. Sidebar navigation (fixed, collapsible on mobile)
2. Top bar (search + notifications + user menu)
3. Page header (h1 + breadcrumb + action buttons)
4. Stats row (4 KPI cards)
5. Primary content (table or main chart)
6. Secondary content (smaller charts or lists)
7. No footer (dashboard fills viewport)

### For Auth Pages (login, register, reset):
1. Minimal header (logo only, no nav)
2. Centered card (max-width 480px)
   - Logo at top of card
   - Heading ("Welcome back" not "Login")
   - Form fields with labels above inputs
   - Primary button (full width)
   - Alternative action (Register / Forgot password)
3. Social proof strip below card (trusted by X users / logos)
4. Minimal footer (privacy + terms only)

---

## The Non-Negotiable Rules

These rules are never overridden for any reason:

**RULE 1**: Every HTML file is 100% self-contained.
All CSS in one `<style>` block. All JS in one `<script>` block.
No external CSS files. No external JS files except Google Fonts @import.

**RULE 2**: No Lorem ipsum anywhere.
Any file containing "Lorem ipsum" is automatically rejected by AntiSlopEnforcer.

**RULE 3**: All colors via CSS variables.
Any hardcoded hex value outside `:root {}` block is a violation.
Exception: the values inside `:root { }` themselves.

**RULE 4**: No hero pattern repeats on same project.
HeroVariationEngine tracks used patterns per project.
If all patterns are used (12+ page project): cycle with different content.

**RULE 5**: No card inside a card.
Any `.card` element that contains another `.card` element is rejected.

**RULE 6**: Prototype nav pill on every page.
Every page except index.html must have:
`<a href="index.html" class="prototype-nav">← All Prototypes</a>`

**RULE 7**: Mobile hamburger menu on every page.
Every page with a navigation must have a working hamburger
with vanilla JS toggle. Test at 375px width.

**RULE 8**: Unsplash images for all photography.
No placeholder.com, no lorempixel, no picsum.
Use ImageIntegrationHelper.get_url() with specific photo IDs.

**RULE 9**: Contrast ratio 4.5:1 minimum on all body text.
ColorCombinationEngine.check_all_contrast() enforced before output.

**RULE 10**: prefers-reduced-motion in every file.
The override must appear in every generated CSS block.

---

## Anti-Slop Rules — What Is NEVER Allowed

Source: `scripts/anti_slop_database.py` — enforced automatically by `AntiSlopEnforcer`

### CRITICAL violations (file rejected until fixed)

**COLORS**
- Indigo `#6366f1` (or any variant: `#818cf8`, `#7c3aed`, `#8b5cf6`, `#4f46e5`) as primary color
- Any purple-to-blue gradient as hero or section background
- Gradient text (`background-clip: text`) on any heading or element
- Neon glow `box-shadow` (radial, no x/y offset, large blur radius)

**TYPOGRAPHY**
- Emoji in any heading (`h1`–`h6`)
- Lorem ipsum anywhere in the document
- `"Title Here"` / `"Description Here"` / `"Heading Here"` placeholder text
- `"John Doe"` / `"Company Name"` / `"example@email.com"` placeholder names

**LAYOUT**
- Card nested inside card (`.card` containing `.card`)
- Thick colored side border on card (`border-left: 4px solid primary`)
- Icon-in-rounded-tile above every feature heading (3+ repeated)
- Sparkle/lightning/fire emoji (`✨ ⚡ 🔥 💡`) as feature icons

**CONTENT**
- "Streamline your workflow"
- "Boost your productivity"
- "Next-generation platform"
- "Transform your business"
- Any of the 22 generic marketing phrases in `FORBIDDEN_CONTENT`

---

### HIGH violations (must fix before delivery)

**COLORS**
- Cream/beige (`#fefce8`, `#fffbeb`, `#fdf6e3`) as page background default
- Cool gray (`#f9fafb`, `#f3f4f6`) as alternating section backgrounds
- Glassmorphism (`backdrop-filter: blur`) on cards
- Cyan/teal (`#06b6d4`, `#0ea5e9`) as primary color

**TYPOGRAPHY**
- Inter as the only font with no display/heading font contrast
- Geist font unless deliberate SaaS/dev-tool choice
- `01` / `02` / `03` display numbers above section headings

**LAYOUT**
- Stack of 3–5 overlapping avatars + "trusted by X users" text
- Exactly 6 identical feature cards in a grid
- Small pill/chip immediately above H1 hero headline
- Header taller than 80px

**ANIMATIONS**
- Bounce or elastic CSS easing on any UI element
- Continuously spinning or floating decorative element
- Pulsing glow on CTA button

**CONTENT**
- Generic CTA text: "Get Started Today" / "Sign Up Now" / "Click Here"
- All testimonials showing 5 stars (mix in one 4-star)
- Testimonial quotes: "Game changer" / "Best decision ever" / "Amazing product"
- Em dash used three or more times in a single paragraph

---

### What is ALWAYS required in every HTML file

Every generated file must contain all 17 of these strings:

| Required element | Why |
|-----------------|-----|
| `<!DOCTYPE html>` | Standards mode |
| `charset="UTF-8"` | Encoding declaration |
| `name="viewport"` | Mobile scaling |
| `:root {` | CSS variable block opens |
| `--color-primary:` | Primary color token defined |
| `--color-bg:` | Background token defined |
| `--font-heading:` | Heading font token defined |
| `--font-body:` | Body font token defined |
| `--text-h1:` | H1 size token defined |
| `--space-4:` | Base spacing token defined |
| `--radius-md:` | Radius token defined |
| `--duration-base:` | Animation duration token |
| `--ease-primary:` | Easing token |
| `class="container"` | Layout wrapper present |
| `class="prototype-nav"` | Back-to-index pill present |
| `@media (max-width: 768px)` | Mobile breakpoint present |
| `prefers-reduced-motion` | Accessibility override present |

Files missing any of these are flagged as `missing_required` and will not pass the check.
