## Phase 0 - UI Prototypes

**Project**: Implementation Plan: Phase 1 — Foundation (Auth, RBAC, Tenancy, Bilingual Shell)
**Goal**: Build approved HTML prototypes for every planned UI page before engineering implementation begins.
**Execution rule**: complete this UI phase first. Do not mix Phase 0 prototype work with later engineering phases.

**Generated foundations in this phase**:
- Approved brand and direction artifacts in `.ui-bridge/`
- Shared design system in `.ui-bridge/design-system.json`
- Shared token stylesheet in `.ui-bridge/design-system.css` and `ui-prototypes/design-tokens.css`
- Shared partials in `ui-prototypes/_partials/`
- One approved HTML file per page in `ui-prototypes/`

**Design token rule**: colors, typography, spacing, radius, shadow, and motion must resolve through CSS variables.
**Phase ordering rule**: `/ui-implement` must follow the page order defined below, one page sub-phase at a time.

---

### Phase 0.1 - Frontend Register -> `ui-prototypes/frontend-register.html`

**Page type**: Public
**Direction**: RTL
**Shared tokens**: `ui-prototypes/design-tokens.css`
**Reference source**: `.ui-bridge/page-map.json` -> `frontend-register`

Required section order:
1. Navbar
2. Main content
3. Footer

Definition of done:
- Approved HTML exists for this page.
- Styling values are CSS-variable driven rather than hardcoded.
- Shared navigation, footer, or sidebar content comes from project partials.

### Phase 0.2 - Frontend Mfa Setup -> `ui-prototypes/frontend-mfa-setup.html`

**Page type**: Public
**Direction**: RTL
**Shared tokens**: `ui-prototypes/design-tokens.css`
**Reference source**: `.ui-bridge/page-map.json` -> `frontend-mfa-setup`

Required section order:
1. Navbar
2. Main content
3. Footer

Definition of done:
- Approved HTML exists for this page.
- Styling values are CSS-variable driven rather than hardcoded.
- Shared navigation, footer, or sidebar content comes from project partials.

### Phase 0.3 - Role-Scoped -> `ui-prototypes/role-scoped.html`

**Page type**: Public
**Direction**: RTL
**Shared tokens**: `ui-prototypes/design-tokens.css`
**Reference source**: `.ui-bridge/page-map.json` -> `role-scoped`

Required section order:
1. Navbar
2. Main content
3. Footer

Definition of done:
- Approved HTML exists for this page.
- Styling values are CSS-variable driven rather than hardcoded.
- Shared navigation, footer, or sidebar content comes from project partials.
