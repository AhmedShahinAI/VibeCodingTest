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

### Design System Reference

Use only approved `.ui-bridge` artifacts and approved HTML prototypes. Do not restyle from category defaults.

