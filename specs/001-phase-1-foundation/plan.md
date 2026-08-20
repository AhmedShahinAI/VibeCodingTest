# Implementation Plan: Phase 1 — Foundation (Auth, RBAC, Tenancy, Bilingual Shell)

**Branch**: `001-phase-1-foundation` | **Date**: 2026-08-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-phase-1-foundation/spec.md`

## Summary

Deliver the platform's identity and access foundation: a user can register or
sign in, complete a TOTP-based MFA challenge, and land on a role-scoped,
localized (AR/EN, RTL/LTR) dashboard — with every request scoped to a single
resolved tenant and every protected action checked against a six-role RBAC
permission matrix. Technical approach: two NestJS microservices (`auth-service`,
`tenancy-service`) behind a shared RBAC/tenant-context guard library, a
Postgres system of record with row-level security as defense-in-depth on top
of application-level tenant scoping, Redis for refresh-token/session state, and
a React 18 frontend with `react-i18next` driving both translation and RTL/LTR
layout switching.

## Technical Context

**Language/Version**: TypeScript 5.x on Node.js 20 LTS (backend); TypeScript
5.x + React 18 (frontend)

**Primary Dependencies**: NestJS 10 (backend framework); Passport.js
(`passport-local`, `passport-jwt`, `passport-google-oauth20`); `otplib` (TOTP
MFA); Prisma (typed ORM + migrations); `ioredis` (Redis client);
`react-i18next` (i18n + RTL); Vite; Tailwind CSS with logical-properties/RTL
support

**Storage**: PostgreSQL 15 (tenant-scoped system of record, row-level security
enabled) + Redis 7 (refresh-token state, MFA challenge state, rate-limit
counters)

**Testing**: Jest + Supertest (backend contract/integration tests); Vitest +
React Testing Library (frontend unit tests); Playwright (end-to-end: auth flow,
RTL/LTR rendering, cross-tenant isolation)

**Target Platform**: Linux containers on Kubernetes; browsers Chrome 100+,
Safari 15+, Firefox 100+

**Project Type**: Web application — frontend + backend, microservices

**Performance Goals**: API p95 < 500ms (constitution VII); full
register→MFA→sign-in→dashboard flow completes in < 3 minutes (spec SC-001)

**Constraints**: Zero cross-tenant data exposure under test (spec SC-002);
100% of auth attempts and permission denials logged in the same request cycle
(spec SC-005); no valid session issued on invalid credentials/MFA (spec SC-006)

**Scale/Scope**: Launch target < 5,000 MAU; architecture must scale 10x+
without a rewrite per PRD. Phase 1 scope = `auth-service` + `tenancy-service` +
frontend auth/dashboard shell only — no course, payment, or media services.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|---|---|---|
| I. Security & Zero-Trust First | PASS | MFA mandatory before session grant; RBAC guard on every endpoint; refresh-token rotation + reuse detection; audit log entry written synchronously for every auth attempt and permission denial; TLS termination and at-rest encryption are infra-level (Kubernetes ingress + managed Postgres/Redis encryption), enforced in deployment config, not app code. |
| II. Multi-Tenant Isolation | PASS | Tenant resolved from JWT claim/subdomain in a shared guard that runs before any controller logic; Postgres row-level security policies enforce `tenant_id` filtering as defense-in-depth beyond application-level query scoping. |
| III. Bilingual-by-Default | PASS | `react-i18next` resource bundles for `ar`/`en`; `dir` attribute and Tailwind logical properties drive RTL/LTR; missing-key fallback-to-English + gap logging built into the i18next config. |
| IV. Content Protection | N/A (this feature) | No media is served in Phase 1; this principle gates Phase 2 (Course Authoring & Content Protection), not this feature. |
| V. Architecture & Technology Discipline | PASS | Matches PRD Section 9 stack exactly: NestJS microservices, React 18 + TS + Tailwind, Postgres + Redis, Kubernetes-ready. |
| VI. MoSCoW & Phase Discipline | PASS | Scope is exactly PRD Phase 1 (P0-F001, P0-F002, P0-F003, P0-F011); no P1/P2 feature is included. |
| VII. Non-Functional Bars | PASS | Performance/availability targets carried into Technical Context above; WCAG 2.1 AA and structured JSON logging are implementation requirements captured in tasks, not deferred. |

No violations — Complexity Tracking table is not needed for this feature.

## Project Structure

### Documentation (this feature)

```text
specs/001-phase-1-foundation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/            # Phase 1 output
│   ├── auth-api.md
│   └── tenancy-api.md
└── tasks.md              # Phase 2 output (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
backend/
├── services/
│   ├── auth-service/
│   │   ├── src/
│   │   │   ├── auth/            # register, login, mfa, refresh, logout controllers+services
│   │   │   ├── users/           # user entity, repository, profile
│   │   │   └── audit/           # audit-log writer used by auth flows
│   │   └── test/
│   │       ├── contract/
│   │       └── integration/
│   ├── tenancy-service/
│   │   ├── src/
│   │   │   ├── tenants/         # tenant CRUD, tenant resolution
│   │   │   └── rbac/            # role/permission matrix, supervisor overrides
│   │   └── test/
│   │       ├── contract/
│   │       └── integration/
│   └── shared/
│       ├── src/
│       │   ├── guards/          # TenantContextGuard, RbacGuard (used by both services)
│       │   ├── i18n/            # server-side message keys for notifications
│       │   └── audit/           # shared AuditLogEntry types + client
│       └── test/unit/

frontend/
├── src/
│   ├── features/
│   │   ├── auth/                # register, login, mfa-setup, mfa-verify pages
│   │   └── dashboard/           # role-scoped dashboard shell
│   ├── i18n/
│   │   ├── ar.json
│   │   └── en.json
│   └── shared/
│       ├── rbac/                # permission-aware route/UI guards
│       └── layout/               # RTL/LTR-aware shell layout
└── tests/
    ├── unit/
    └── e2e/                      # Playwright: auth flow, RTL/LTR, tenant isolation
```

**Structure Decision**: Web application with two Phase 1 microservices
(`auth-service`, `tenancy-service`) sharing a `backend/services/shared`
library for the tenant-context and RBAC guards mandated by constitution
principles I/II/V, plus a React frontend consuming both services through a
single `/api/v1` gateway path. Later phases add sibling services (`courses`,
`media`, `payments`, …) under `backend/services/` without restructuring this
layout.

---

## Phase 0 - UI Prototypes

**Project**: Implementation Plan: Phase 1 — Foundation (Auth, RBAC, Tenancy, Bilingual Shell)
**Goal**: Build approved HTML prototypes for every planned UI page before engineering implementation begins.
**Execution rule**: complete this UI phase first. Do not mix Phase 0 prototype work with later engineering phases.

**Generated foundations in this phase**:
- Approved brand and direction artifacts in `.ui-bridge/` — brand: **SimpleElm** (`brand-intake.v3.json`)
- Shared design system in `.ui-bridge/design-system.json`
- Shared token stylesheet in `.ui-bridge/design-system.css` and `ui-prototypes/design-tokens.css`
- Shared partials in `ui-prototypes/_partials/`
- One approved HTML file per page in `ui-prototypes/`

**Design token rule**: colors, typography, spacing, radius, shadow, and motion must resolve through CSS variables.
**Theming rule**: SimpleElm ships approved **light and dark** identities, not one default plus an
auto-derived dark mode. Every page must expose a user-controlled toggle
(`data-theme="light"|"dark"` on `<html>`, persisted in `localStorage['simpleelm-theme']`,
defaulting to the visitor's OS preference until they choose explicitly) — see the toggle button
and bootstrap script already wired into `ui-prototypes/_partials/nav-public.html` and each page's
`<head>`. No component may hardcode a color that isn't a `var(--color-*)` token.
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

---

## UI Prototype Index

Generated: 2026-08-18
Total: 4 page(s)

| Page | File | Sections |
|------|------|----------|
| إعداد التحقق بخطوتين — علم | `ui-prototypes\frontend-mfa-setup.html` | 1 |
| إنشاء حساب — علم | `ui-prototypes\frontend-register.html` | 1 |
| فهرس النماذج — علم | `ui-prototypes\prototype-hub.html` | 1 |
| لوحة التحكم — علم | `ui-prototypes\role-scoped.html` | 1 |

### Design System Reference (superseded — see below)

The `.ui-bridge` artifacts and the three approved HTML prototypes above were
the Phase 0 starting point. They are now superseded for **visual** purposes
by the approved design system in the section immediately below. They remain
useful as historical record of page structure/section order and are not to
be deleted.

---

## Design System Source of Truth — `SimpleElm Design System.zip` (2026-08-20)

**Status**: Approved. **Supersedes** the Phase 0 `.ui-bridge` token set and
HTML-prototype visuals for all Phase 1 screens. Does **not** change any
functional requirement, route, API contract, or business rule in spec.md —
per that document, "the existing specifications are the source of truth for
functionality and business requirements," and this design system is the
source of truth for visual design only.

A full copy of the approved package (tokens, components, UI kits,
guidelines, brand assets) lives at repository root as
`SimpleElm Design System.zip`. It was generated from uploaded brand identity
boards (`assets/brand-board-light.png`, `assets/brand-board-dark.png`) and
logos, and — per its own `readme.md` — explicitly reads
`specs/001-phase-1-foundation/` as its product-spec source, so its
`ui_kits/auth/` package is a direct visual reference for this feature.

### What's in scope for Phase 1

| Design system asset | Phase 1 relevance |
|---|---|
| `tokens/{colors,typography,spacing,fonts,base}.css` | Canonical CSS variables — colors, type scale, spacing/radii/shadows/motion, font loading. **Replaces** `ui-prototypes/design-tokens.css` as the token source for production code. |
| `components/{forms,feedback,content,media}/*.jsx` + `.d.ts` | Reference API/behavior for `Button`, `Input`, `IconButton`, `Switch`, `Progress`, `Badge`, `Card`, `FeatureCard`, `CourseCard`, `StatItem`, `Icon`. Reimplemented (not copy-pasted) as typed, Tailwind-driven components — see Technical Approach below. |
| `ui_kits/auth/AuthKit.jsx` + `README.md` | **Primary visual reference for this feature.** Models `Shell` (header/logo/language+theme toggles), `Auth` (tabbed Sign in/Register card, role picker, social sign-in), `Mfa` (6-digit TOTP verify), `Dashboard` (role icon, tenant badge, stat cards, quick actions, activity feed) — bilingual + light/dark. |
| `guidelines/*.card.html` | Foundation specimens (color, type, spacing, radii, shadows, brand/logo) — reference for any state/spacing question not answered by AuthKit directly. |
| `assets/*.png` | Logo (EN/AR wordmark + transparent variants), standalone S-mark, 3D hero mark, brand boards. |
| `ui_kits/website/`, `ui_kits/mobile/` | **Out of Phase 1 scope.** These are marketing-site and learner-mobile-app recreations for a later phase/feature. Do not build marketing or mobile-app pages under this feature; do not let their scope bleed into `tasks.md`. |

### Conflicts, gaps, and resolutions identified before implementation

1. **Token-system conflict.** The old `.ui-bridge`/`ui-prototypes/design-tokens.css`
   tokens (`--color-primary`, fixed `--radius-sm/md/lg` at 8/16/24px, no
   gradients, JetBrains Mono) and the new `tokens/*.css` (`--se-*` raw ramp +
   semantic `--brand`/`--bg-*`/`--text-*` aliases, pill radius `999px` on all
   interactive elements, brand gradients, glow shadows, IBM Plex Mono) share
   the same brand blue/cyan/violet hues but are **not** drop-in compatible.
   **Resolution**: the new token set is canonical going forward; the old file
   is left in place for the historical prototypes but is not referenced by
   any new or restyled production code.
2. **No prior approved prototype for Login or MFA-verify.** `tasks.md` T032
   already notes this gap explicitly. **Resolution**: `AuthKit.jsx`'s `Auth`
   (tabbed sign-in/register card) and `Mfa` (6-digit verify) components fill
   this gap and become the reference for those two routes.
3. **No visual reference for MFA *setup* (QR enrollment).** `AuthKit.jsx`
   only models MFA *verify*, not the TOTP-secret/QR enrollment step.
   **Resolution**: compose the MFA-setup screen from the same card shell,
   icon-avatar, and type/spacing tokens used elsewhere in `AuthKit`, since no
   direct specimen exists — this is new composition within the approved
   system, not an invented style.
4. **Production frontend currently has no visual design applied.**
   `RegisterPage.tsx`, `LoginPage.tsx`, `MfaSetupPage.tsx`,
   `MfaVerifyPage.tsx`, `DashboardPage.tsx`, and `AppShell.tsx` are built with
   generic, unbranded Tailwind defaults (`bg-white`, `text-gray-900`, plain
   `border`/`rounded`) — no logo, no brand color, no pill shapes, no card
   elevation, no dark mode, no icon system, no font loading for Inter/IBM
   Plex Sans Arabic. The `tasks.md` entries for these pages are marked
   complete for **function** (the auth/RBAC/i18n logic works and is tested)
   but not for the visual fidelity this design system now requires.
   **Resolution**: new restyle tasks are added in `tasks.md` (Design System
   Foundation phase + per-story restyle tasks) that keep every existing
   component's props, state, routes, and API calls unchanged and only change
   markup/styling.
5. **Register role picker scope.** `AuthKit.jsx`'s register screen lets a
   demo user pick any of the six roles. spec.md's own Assumptions state that
   only Learner and Course Provider/Instructor self-register; the other four
   roles are invited/provisioned within a tenant. **Resolution**: adopt
   AuthKit's pill/card role-selector *visual* style, but keep the production
   `RegisterPage` scoped to exactly the two self-registrable roles — the
   spec is the source of truth for what's functionally selectable, the
   design system only supplies how the selector looks.
6. **MFA demo code is not real validation.** `AuthKit.jsx`'s `Mfa` component
   accepts the literal code `000000` client-side, for demo purposes only.
   **Resolution**: adopt only the 6-box input layout, focus/error states,
   and copy — the actual TOTP verification stays server-side via the
   existing `POST /auth/mfa/verify` call in `authClient.ts`.
7. **No social sign-in entry point exists in the frontend today**, though
   FR-002 requires it and the backend already depends on
   `passport-google-oauth20`. **Resolution**: add the "Continue with Google"
   button (AuthKit visual) to the restyled auth card and wire it to the
   backend's Google OAuth route as part of the US1 restyle work — flagged as
   a functional gap-fill, not just a visual one.
8. **No dark/light theme toggle exists in the frontend today.** `AppShell`
   hardcodes light colors. The design system requires an explicit,
   user-controlled `data-theme` toggle persisted in
   `localStorage['simpleelm-theme']`, defaulting to OS preference — the same
   pattern already used by the (superseded) HTML prototypes.
   **Resolution**: build this as part of Design System Foundation work; every
   restyled screen must be verified in both themes.
9. **No Tailwind↔token bridge exists.** `frontend/tailwind.config.js` has an
   empty theme (no color/radius/shadow/font extension), so there is
   currently no mechanical way for Tailwind utility classes to consume the
   new CSS variables. **Resolution**: extend the Tailwind theme to map every
   token (see Technical Approach) so components use Tailwind utilities
   (`bg-brand`, `rounded-pill`, `shadow-brand`, `font-arabic`, etc.) rather
   than inline styles, keeping the codebase idiomatic for a Vite+Tailwind
   React app instead of copy-pasting the design system's prototype-grade
   inline-style JSX verbatim.

### Technical approach for production integration

- **Tokens**: port `tokens/{colors,typography,spacing,fonts,base}.css`
  verbatim into `frontend/src/styles/tokens/` (unchanged CSS custom
  properties — these are the contract) and import them from
  `frontend/src/index.css` ahead of the Tailwind layers.
- **Tailwind bridge**: extend `frontend/tailwind.config.js` `theme.extend`
  so `colors`, `borderRadius`, `boxShadow`, `spacing`, and `fontFamily` read
  from the CSS variables (e.g. `colors: { brand: 'var(--brand)', ... }`,
  `borderRadius: { pill: 'var(--r-pill)', xl: 'var(--r-xl)', ... }`). This
  keeps the existing Tailwind-utility authoring style used across the
  codebase and gets automatic light/dark + RTL/LTR switching for free
  wherever a token is referenced.
- **Components**: reimplement the design system's `components/**/*.jsx`
  primitives as typed React components under `frontend/src/shared/ui/`
  (`Button.tsx`, `Input.tsx`, `Card.tsx`, `Badge.tsx`, `IconButton.tsx`,
  `Switch.tsx`, `Progress.tsx`, `StatItem.tsx`, `Icon.tsx`), matching the
  `.d.ts` prop contracts and visual states (hover/press/focus/disabled/error)
  via Tailwind classes and `:focus-visible`/`:hover` rather than the
  source's inline `onMouseEnter`/`onMouseDown` handlers. Existing pages are
  refactored to compose these primitives instead of raw `<input>`/`<button>`
  elements; no page's data flow, validation, or API calls change.
- **Icons**: install `lucide-react` (the design system's stated substitution
  for the brand's line-icon style — see `readme.md` ICONOGRAPHY) and use the
  brand→Lucide glyph map already documented there.
- **Fonts**: load Inter, IBM Plex Sans Arabic, and IBM Plex Mono per
  `tokens/fonts.css`; the `[dir="rtl"],[lang="ar"] { --font-sans: var(--font-arabic) }`
  rule already handles automatic switching.
- **Theme toggle**: add a `frontend/src/shared/theme/` module (`useTheme`
  hook + `ThemeToggle` component) mirroring the existing
  `frontend/src/i18n` locale-persistence pattern — `data-theme` on
  `<html>`, `localStorage['simpleelm-theme']`, OS-preference default.
- **Routing/architecture unchanged**: Login and Register stay on separate
  routes (existing architecture) but both render the same shared tabbed
  auth-card shell with the corresponding tab pre-selected, matching
  `AuthKit.jsx`'s `Auth` component visually while preserving the existing
  route split.

### Updated frontend project structure

```text
frontend/
├── src/
│   ├── styles/
│   │   └── tokens/            # ported verbatim from SimpleElm Design System.zip: colors.css, typography.css, spacing.css, fonts.css, base.css
│   ├── shared/
│   │   ├── ui/                 # Button, Input, Card, Badge, IconButton, Switch, Progress, StatItem, Icon, Logo — typed, Tailwind-driven primitives
│   │   ├── theme/               # useTheme hook + ThemeToggle (data-theme, localStorage['simpleelm-theme'])
│   │   ├── rbac/                # unchanged
│   │   └── layout/               # AppShell (restyled), LanguageToggle (restyled)
│   ├── features/
│   │   ├── auth/                # RegisterPage, LoginPage, MfaSetupPage, MfaVerifyPage — restyled, same routes/logic
│   │   └── dashboard/            # DashboardPage — restyled, same permission-gated sections
│   └── i18n/                     # unchanged
```

**Design token rule (unchanged)**: colors, typography, spacing, radius,
shadow, and motion must resolve through CSS variables — now sourced from
`frontend/src/styles/tokens/`, not `ui-prototypes/design-tokens.css`.

**Theming rule (unchanged in spirit, now formally required in production)**:
SimpleElm ships approved light and dark identities. Every Phase 1 screen
must expose the user-controlled theme toggle described above — not just the
former HTML prototypes.

**Fidelity rule**: match `ui_kits/auth/AuthKit.jsx` and the `guidelines/`
specimens with pixel-perfect fidelity wherever technically feasible within
the existing React/Tailwind architecture. Visual deviations require the same
approval as any other prototype change.

### Design System Reference

Use only the approved `SimpleElm Design System.zip` package (tokens,
components, `ui_kits/auth/`, `guidelines/`) as the visual reference for
Phase 1 screens, and `specs/001-phase-1-foundation/spec.md` as the
functional reference. Do not restyle from Tailwind/category defaults, and do
not reintroduce the superseded `.ui-bridge` token values into new code.

