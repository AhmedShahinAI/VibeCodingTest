# UI Bridge — Detection Layers

These 7 layers run in order at the start of every ui-bridge command.
Results are saved to `.ui-bridge/detection-report.json` and printed as
a summary before any work begins. If Layer 1 or Layer 2 fail,
the command stops immediately with a clear error message.

---

## Layer 1 — Spec Kit Artifact Detection (BLOCKING)

What to detect:
- Search for `plan.md` in: root, `specs/`, `.specify/`, `specs/*/`
- Search for `tasks.md` in: root, `specs/`, `.specify/`, `specs/*/`
- Check that `plan.md` contains at least one `## Phase` heading
- Check that `tasks.md` contains at least one `- [ ] T` task line
- Check for `constitution.md` in `.specify/memory/`

Output:
```json
{
  "plan_path": "string | null",
  "tasks_path": "string | null",
  "phases_found": "number",
  "tasks_found": "number",
  "has_constitution": "boolean",
  "status": "ok | missing_plan | missing_tasks | empty"
}
```

On failure: print exactly this and stop:
```
✗ Layer 1 Failed — No Spec Kit artifacts found.
  Run /speckit-plan and /speckit-tasks first, then retry.
```

---

## Layer 2 — Project Type Detection (BLOCKING with fallback)

What to detect:
- Read `package.json` if exists → extract framework, dependencies
- Read `plan.md` tech stack section → extract frontend/backend choices
- Detect language: search for Arabic text `[؀-ۿ]` or `dir="rtl"` in plan.md/tasks.md/README
- Detect project category from keywords in plan.md:
  - `"course"` | `"training"` | `"learn"` → EdTech
  - `"shop"` | `"product"` | `"cart"` → E-commerce
  - `"dashboard"` | `"analytics"` | `"metrics"` → SaaS/Dashboard
  - `"booking"` | `"appointment"` → Booking Platform
  - `"clinic"` | `"doctor"` | `"health"` → Healthcare
  - `"invest"` | `"finance"` | `"payment"` → Fintech
  - `"hotel"` | `"travel"` | `"tour"` → Travel/Hospitality
  - `"restaurant"` | `"menu"` | `"food"` → Food & Beverage
  - `"real estate"` | `"property"` | `"rent"` → Real Estate
  - `"agency"` | `"portfolio"` | `"creative"` → Creative Agency
  - default → unknown type; brand decisions still require approval

Output:
```json
{
  "framework": "string",
  "project_category": "string",
  "is_arabic": "boolean",
  "is_rtl": "boolean",
  "has_admin_panel": "boolean",
  "has_auth": "boolean",
  "status": "ok | unknown_type"
}
```

On failure (`unknown_type`): continue only for page discovery and content
analysis. Do not select colors, fonts, imagery, radii, or visual presets from
this layer.

---

## Layer 3 — Brand Signal Detection (NON-BLOCKING)

What to detect:
- Scan all `.css`, `.scss`, `.vue`, `.jsx`, `.tsx`, `.html` files for hex colors
- Scan for CSS custom properties (`--color-*`, `--primary`, `--brand`)
- Scan `tailwind.config.ts/js` for `theme.colors`
- Scan for Google Fonts `@import` or `<link>` with `fonts.googleapis.com`
- Scan for `font-family` declarations
- Look for logo files: `*.svg`, `*logo*`, `*brand*`, `*icon*` in `public/`, `assets/`, `src/`
- Read `README.md` for any brand/color/font mentions

Score signals by confidence:
- `explicit_code` = high confidence (found in actual code)
- `config_file` = medium confidence (found in tailwind/config)
- `readme_mention` = low confidence (found in documentation)
- `inferred` = inferred from project type

Output:
```json
{
  "primary_color": { "value": "string", "confidence": "high|medium|low|inferred" },
  "secondary_color": { "value": "string", "confidence": "string" },
  "accent_color": { "value": "string", "confidence": "string" },
  "heading_font": { "value": "string", "confidence": "string" },
  "body_font": { "value": "string", "confidence": "string" },
  "logo_path": "string | null",
  "brand_signals_count": "number"
}
```

---

## Layer 4 — Page Inventory Detection (NON-BLOCKING)

What to detect:
- Scan tasks.md for all UI page mentions using TWO methods:

  **Method A — Framework path patterns** (any of these extensions):
  ```
  pages/*.vue    pages/*.tsx    pages/*.jsx    pages/*.astro
  src/views/*.vue    src/views/*.tsx    src/pages/*.tsx
  app/**/page.tsx    screens/*.tsx    screens/*.jsx
  ```

  **Method B — Semantic patterns** (framework-agnostic):
  ```
  Build the X Page       Design the X Screen    Create the X View
  Implement the X Page   Develop the X Screen   Add the X Page
  ```
  Exclude lines containing backend indicators:
  `service, controller, middleware, route, endpoint, migration, model,`
  `repository, handler, database, schema, redis, email, smtp, cron,`
  `webhook, job, queue, seed, fixture, jwt, token, resolver, dto`

- Deduplicate by slug — if Method A and Method B both find "courses", count once
- Normalize to HTML slug: `pages/courses/index.vue` → `courses`, `"Courses Listing Page"` → `courses`
- Detect admin pages: slug starts with `admin-` or path contains `/admin/`

Output:
```json
{
  "pages": [
    {
      "name": "string",
      "slug": "string",
      "route": "string",
      "is_admin": "boolean",
      "source_tasks": ["string"],
      "detection_method": "path | semantic",
      "estimated_sections": "number"
    }
  ],
  "total_pages": "number",
  "public_count": "number",
  "admin_count": "number"
}
```

---

## Layer 5 — Impeccable Installation Detection (NON-BLOCKING)

What to detect:
- Check for `.claude/skills/impeccable/` directory in project root
- Check for `~/.claude/skills/impeccable/` directory (global installation)
- Check for `PRODUCT.md` in project root or `.ui-bridge/`
- Check for `DESIGN.md` in project root or `.ui-bridge/`
- Check if `npx` is available on PATH

Output:
```json
{
  "impeccable_installed": "boolean",
  "product_md_exists": "boolean",
  "design_md_exists": "boolean",
  "npx_available": "boolean",
  "install_needed": "boolean"
}
```

---

## Layer 6 — Existing UI Bridge State Detection (NON-BLOCKING)

What to detect:
- Check if `.ui-bridge/` directory exists
- Check if `.ui-bridge/detection-report.json` exists (previous run)
- Check if `.ui-bridge/page-map.json` exists
- Check if `ui-prototypes/` directory exists
- Count existing `.html` files in `ui-prototypes/` (excluding `index.html`)
- Detect if `plan.md` already has `## Phase 0` (already ran `/ui-plan`)

Output:
```json
{
  "previous_run_exists": "boolean",
  "page_map_exists": "boolean",
  "prototypes_exist": "boolean",
  "prototypes_count": "number",
  "phase_0_already_added": "boolean",
  "resuming": "boolean"
}
```

If `resuming` is true, print:
```
↻ Resuming from previous ui-bridge session
  Found X existing prototypes — will skip completed pages
```

---

## Layer 7 — Output Consistency Check (NON-BLOCKING)

This layer runs ONLY when `ui-prototypes/` already has HTML files.
It checks that existing files follow the consistency rules
so new files match the existing ones.

What to check:
- Extract `--color-primary` value from first HTML file found
- Extract `--font-heading` / `font-family` from first HTML file found
- Extract `--radius` / `border-radius` scale from first HTML file found
- Extract nav structure signature from first HTML file found

These become the **LOCKED values** for all subsequent files in this project.

Output:
```json
{
  "locked_primary_color": "string | null",
  "locked_font_family": "string | null",
  "locked_border_radius": "string | null",
  "locked_nav_html": "string | null",
  "consistency_baseline_set": "boolean"
}
```

---

## Detection Report Format

After all 7 layers complete, save to `.ui-bridge/detection-report.json`:

```json
{
  "timestamp": "ISO timestamp",
  "command": "ui-plan | ui-implement | ui-link",
  "layer_1": {},
  "layer_2": {},
  "layer_3": {},
  "layer_4": {},
  "layer_5": {},
  "layer_6": {},
  "layer_7": {},
  "summary": {
    "can_proceed": "boolean",
    "warnings": ["string"],
    "decisions_made": ["string"]
  }
}
```

And print this summary to the user before any work begins:

```
┌─ UI Bridge — Detection Complete ──────────────────────┐
│ Project:    [name] ([category])                        │
│ Pages:      [count] pages found                        │
│ Brand:      [primary color] / [font] ([confidence])    │
│ Arabic:     [Yes / No]                                 │
│ Resuming:   [Yes (X files exist) / No (fresh start)]  │
│ Impeccable: [Installed / Will install]                 │
└────────────────────────────────────────────────────────┘
[warnings if any]
Proceeding with [command name]...
```
