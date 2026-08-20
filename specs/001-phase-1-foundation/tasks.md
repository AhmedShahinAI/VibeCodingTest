---

description: "Task list for Phase 1 — Foundation implementation"

---

# Tasks: Phase 1 — Foundation (Auth, RBAC, Tenancy, Bilingual Shell)

**Input**: Design documents from `/specs/001-phase-1-foundation/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/auth-api.md, contracts/tenancy-api.md, quickstart.md

**Tests**: Included. The constitution's Development Workflow & Quality Gates
section mandates an explicit cross-tenant-isolation test case for any feature
touching tenant-scoped data, and RBAC/audit correctness for every protected
action — both apply directly to this feature, so contract/integration tests
are not optional here.

**Organization**: Tasks are grouped by user story (US1–US4, matching spec.md
priorities P1–P4) to enable independent implementation and testing of each.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- File paths are exact and match the layout in plan.md's Project Structure

## Path Conventions (from plan.md)

- Backend: `backend/services/auth-service/`, `backend/services/tenancy-service/`, `backend/services/shared/`
- Frontend: `frontend/src/`, `frontend/tests/`

---

## Phase 0 - UI Prototypes

**Execution rule**: finish the UI prototype phase first and in order before moving into later implementation phases.**
**Granularity rule**: one sub-phase equals one page; one task equals one shared requirement or page section.**
**Theming rule**: brand is **SimpleElm** with an approved light identity and an approved dark
identity, switchable via a required user-controlled toggle (`data-theme` on `<html>`,
`localStorage['simpleelm-theme']`). Verify both themes — not just light — when reviewing any
page or section task below.

---

### Phase 0.1 - Frontend Register -> `ui-prototypes/frontend-register.html`

- [ ] T0-0100 [P] [US1] Create or update the shared HTML shell for `frontend-register`
- [ ] T0-0101 [P] [US1] Ensure `frontend-register` links `design-tokens.css` and copies required root tokens inline
- [ ] T0-0102 [P] [US1] Ensure `frontend-register` uses CSS variables for color, type, spacing, radius, and motion
- [x] T0-204 [P] [US1] Build section: Navbar - `ui-prototypes/frontend-register.html` ✅
  > **UI Reference**: `ui-prototypes\frontend-register.html`
  > **Sections to implement**:
  > - إنشاء حساب جديد في علم -> `#main`
  > **Implementation rule**: Match the approved HTML prototype. Visual changes require approval.
- [x] T0-205 [P] [US1] Build section: Main content - `ui-prototypes/frontend-register.html` ✅
  > **UI Reference**: `ui-prototypes\frontend-register.html`
  > **Sections to implement**:
  > - إنشاء حساب جديد في علم -> `#main`
  > **Implementation rule**: Match the approved HTML prototype. Visual changes require approval.
- [x] T0-206 [P] [US1] Build section: Footer - `ui-prototypes/frontend-register.html` ✅
  > **UI Reference**: `ui-prototypes\frontend-register.html`
  > **Sections to implement**:
  > - إنشاء حساب جديد في علم -> `#main`
  > **Implementation rule**: Match the approved HTML prototype. Visual changes require approval.
- [ ] T0-0198 [P] [US1] Stamp shared partials into `frontend-register` and verify active navigation state
- [x] T0-0199 [P] [US1] Publish the approved prototype file `ui-prototypes/frontend-register.html` ✅
  > **UI Reference**: `ui-prototypes\frontend-register.html`
  > **Sections to implement**:
  > - إنشاء حساب جديد في علم -> `#main`
  > **Implementation rule**: Match the approved HTML prototype. Visual changes require approval.

### Phase 0.2 - Frontend Mfa Setup -> `ui-prototypes/frontend-mfa-setup.html`

- [ ] T0-0200 [P] [US1] Create or update the shared HTML shell for `frontend-mfa-setup`
- [ ] T0-0201 [P] [US1] Ensure `frontend-mfa-setup` links `design-tokens.css` and copies required root tokens inline
- [ ] T0-0202 [P] [US1] Ensure `frontend-mfa-setup` uses CSS variables for color, type, spacing, radius, and motion
- [x] T0-212 [P] [US1] Build section: Navbar - `ui-prototypes/frontend-mfa-setup.html` ✅
  > **UI Reference**: `ui-prototypes\frontend-mfa-setup.html`
  > **Sections to implement**:
  > - إعداد التحقق بخطوتين -> `#main`
  > **Implementation rule**: Match the approved HTML prototype. Visual changes require approval.
- [x] T0-213 [P] [US1] Build section: Main content - `ui-prototypes/frontend-mfa-setup.html` ✅
  > **UI Reference**: `ui-prototypes\frontend-mfa-setup.html`
  > **Sections to implement**:
  > - إعداد التحقق بخطوتين -> `#main`
  > **Implementation rule**: Match the approved HTML prototype. Visual changes require approval.
- [x] T0-214 [P] [US1] Build section: Footer - `ui-prototypes/frontend-mfa-setup.html` ✅
  > **UI Reference**: `ui-prototypes\frontend-mfa-setup.html`
  > **Sections to implement**:
  > - إعداد التحقق بخطوتين -> `#main`
  > **Implementation rule**: Match the approved HTML prototype. Visual changes require approval.
- [ ] T0-0298 [P] [US1] Stamp shared partials into `frontend-mfa-setup` and verify active navigation state
- [x] T0-0299 [P] [US1] Publish the approved prototype file `ui-prototypes/frontend-mfa-setup.html` ✅
  > **UI Reference**: `ui-prototypes\frontend-mfa-setup.html`
  > **Sections to implement**:
  > - إعداد التحقق بخطوتين -> `#main`
  > **Implementation rule**: Match the approved HTML prototype. Visual changes require approval.

### Phase 0.3 - Role-Scoped -> `ui-prototypes/role-scoped.html`

- [ ] T0-0300 [P] [US1] Create or update the shared HTML shell for `role-scoped`
- [ ] T0-0301 [P] [US1] Ensure `role-scoped` links `design-tokens.css` and copies required root tokens inline
- [ ] T0-0302 [P] [US1] Ensure `role-scoped` uses CSS variables for color, type, spacing, radius, and motion
- [x] T0-220 [P] [US1] Build section: Navbar - `ui-prototypes/role-scoped.html` ✅
  > **UI Reference**: `ui-prototypes\role-scoped.html`
  > **Sections to implement**:
  > - الإجراءات المتاحة لدورك -> `#main`
  > **Implementation rule**: Match the approved HTML prototype. Visual changes require approval.
- [x] T0-221 [P] [US1] Build section: Main content - `ui-prototypes/role-scoped.html` ✅
  > **UI Reference**: `ui-prototypes\role-scoped.html`
  > **Sections to implement**:
  > - الإجراءات المتاحة لدورك -> `#main`
  > **Implementation rule**: Match the approved HTML prototype. Visual changes require approval.
- [x] T0-222 [P] [US1] Build section: Footer - `ui-prototypes/role-scoped.html` ✅
  > **UI Reference**: `ui-prototypes\role-scoped.html`
  > **Sections to implement**:
  > - الإجراءات المتاحة لدورك -> `#main`
  > **Implementation rule**: Match the approved HTML prototype. Visual changes require approval.
- [ ] T0-0398 [P] [US1] Stamp shared partials into `role-scoped` and verify active navigation state
- [x] T0-0399 [P] [US1] Publish the approved prototype file `ui-prototypes/role-scoped.html` ✅
  > **UI Reference**: `ui-prototypes\role-scoped.html`
  > **Sections to implement**:
  > - الإجراءات المتاحة لدورك -> `#main`
  > **Implementation rule**: Match the approved HTML prototype. Visual changes require approval.

---

## Phase 0.5 - Design System Integration (SimpleElm Design System.zip)

**Status**: New. Approved 2026-08-20. **Supersedes** the Phase 0 `.ui-bridge`
token set and HTML-prototype visuals for all Phase 1 screens — see
`plan.md` → "Design System Source of Truth" for the full conflict/resolution
analysis. Functional requirements, routes, and API contracts are unchanged;
only visual implementation is affected.

**Source of truth**: `SimpleElm Design System.zip` at repository root
(extracted reference: `tokens/`, `components/`, `ui_kits/auth/AuthKit.jsx`,
`guidelines/`, `assets/`). Primary page reference for this feature is
`ui_kits/auth/AuthKit.jsx` (`Shell`, `Auth`, `Mfa`, `Dashboard`).

**Known gaps in `AuthKit.jsx` requiring composition rather than direct copy**:
no MFA-*setup* (QR enrollment) screen exists in the kit (only MFA-*verify*);
the six-role register picker is a demo affordance and must be scoped down to
the two spec-approved self-registrable roles in production.

**Execution rule**: complete this phase before restyling any individual
page in Phases 3, 4, and 6 below — the token/Tailwind bridge and shared `ui/`
primitives are prerequisites for every restyle task that follows.

- [ ] T070 [P] Vendor brand assets (`assets/logo-en*.png`, `assets/logo-ar*.png`, `assets/mark*.png`) from `SimpleElm Design System.zip` into `frontend/src/assets/brand/`
- [ ] T071 [P] Port `tokens/{colors,typography,spacing,fonts,base}.css` verbatim into `frontend/src/styles/tokens/` and import from `frontend/src/index.css` ahead of the Tailwind layers; retire `ui-prototypes/design-tokens.css` as a production dependency
- [ ] T072 [P] Wire Google Fonts (Inter, IBM Plex Sans Arabic, IBM Plex Mono) loading per `tokens/fonts.css` in `frontend/index.html`
- [ ] T073 Extend `frontend/tailwind.config.js` `theme.extend` to map `--brand`, `--bg-*`, `--text-*`, `--border*`, `--r-*` (incl. `pill`), `--shadow-*` (incl. `brand`, `glow`), `--sp-*`, `--fs-*`, and font-family tokens from `frontend/src/styles/tokens/` into Tailwind `colors`/`borderRadius`/`boxShadow`/`spacing`/`fontFamily` (depends on T071)
- [ ] T074 Install `lucide-react`; build typed `Icon` wrapper in `frontend/src/shared/ui/Icon.tsx` using the brand→Lucide glyph map from the design system's `readme.md` ICONOGRAPHY section (depends on T073)
- [ ] T075 Implement theme toggle (`data-theme` on `<html>`, `localStorage['simpleelm-theme']`, defaults to OS preference until explicit choice) in `frontend/src/shared/theme/useTheme.ts` + `frontend/src/shared/theme/ThemeToggle.tsx` (depends on T073)
- [ ] T076 [P] Build typed, Tailwind-driven primitives in `frontend/src/shared/ui/`: `Button.tsx` (primary/gradient/secondary/ghost × sm/md/lg, hover/press/disabled), `Input.tsx` (icon slot, focus ring, clearable, error state), `Card.tsx` (elevation sm/md/lg, interactive hover-lift), `Badge.tsx` (tone × solid × sm/md), `IconButton.tsx`, `Switch.tsx`, `Progress.tsx`, `StatItem.tsx` — API parity with `components/**/*.d.ts` in the design system, reimplemented (not copy-pasted) for React+TS+Tailwind (depends on T073, T074)
- [ ] T077 [P] Build `Logo.tsx` (EN/AR wordmark + standalone S-mark, light/dark aware) in `frontend/src/shared/ui/Logo.tsx` (depends on T070)

**Checkpoint**: Design system foundation ready — per-page restyle tasks in US1/US2/US4 below can now begin

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create repository layout per plan.md Project Structure (`backend/services/{auth-service,tenancy-service,shared}`, `frontend/`)
- [X] T002 Initialize `auth-service` NestJS project with Prisma, Passport (local/jwt/google-oauth20), `otplib` dependencies in `backend/services/auth-service/`
- [X] T003 [P] Initialize `tenancy-service` NestJS project in `backend/services/tenancy-service/`
- [X] T004 [P] Initialize `shared` library package (guards, audit, i18n message resolver) in `backend/services/shared/`
- [X] T005 [P] Initialize frontend Vite + React 18 + TypeScript project with Tailwind CSS (logical-properties config) and `react-i18next` in `frontend/`
- [X] T006 [P] Configure ESLint + Prettier for backend and frontend workspaces
- [X] T007 Configure `docker-compose.yml` with PostgreSQL 15 and Redis 7 for local development at repository root

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Define Prisma schema for `Tenant`, `User`, `SupervisorPermissionOverride`, `AuditLogEntry` per data-model.md in `backend/services/shared/prisma/schema.prisma`
- [X] T009 Write initial Prisma migration and enable Postgres Row-Level Security on all tenant-scoped tables in `backend/services/shared/prisma/migrations/`
- [X] T010 [P] Implement `TenantContextGuard` (resolves tenant from JWT claim + subdomain cross-check) in `backend/services/shared/src/guards/tenant-context.guard.ts`
- [X] T011 [P] Implement `RbacGuard` and `@RequirePermission` decorator in `backend/services/shared/src/guards/rbac.guard.ts`
- [X] T012 [P] Implement shared `AuditLogService` (synchronous, same-transaction writer) in `backend/services/shared/src/audit/audit-log.service.ts`
- [X] T013 [P] Implement Redis-backed refresh-token store with family tracking, rotation, and reuse detection in `backend/services/shared/src/auth/refresh-token.store.ts`
- [X] T014 Configure structured JSON logging with >1% error-rate alerting hook in `backend/services/shared/src/logging/`
- [X] T015 [P] Scaffold frontend i18n config (`ar.json`, `en.json`, `fallbackLng: 'en'`, missing-key gap logging) in `frontend/src/i18n/`
- [X] T016 [P] Build RTL/LTR-aware root layout (document `dir` binding driven by locale) in `frontend/src/shared/layout/`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Secure Registration & Sign-In (Priority: P1) 🎯 MVP

**Goal**: A user can register or sign in, complete an MFA challenge, and receive a valid session — with no session ever granted on invalid credentials or an invalid/expired MFA code.

**Independent Test**: Register a new account, complete MFA setup, sign in with correct credentials + valid MFA code and confirm tokens are issued; repeat with wrong password and wrong/expired MFA code and confirm no token is issued in either case. Runs standalone against `auth-service` with no RBAC/tenancy/i18n dependencies beyond the Foundational guards.

### Tests for User Story 1 ⚠️

- [X] T017 [P] [US1] Contract test `POST /auth/register` (incl. duplicate-email 409) in `backend/services/auth-service/test/contract/register.spec.ts`
- [X] T018 [P] [US1] Contract test `POST /auth/login` + `POST /auth/mfa/verify` (success and failure paths) in `backend/services/auth-service/test/contract/login-mfa.spec.ts`
- [X] T019 [P] [US1] Contract test `POST /auth/refresh` rotation and reuse-detection (403 + family revocation) in `backend/services/auth-service/test/contract/refresh.spec.ts`
- [X] T020 [P] [US1] Integration test: full register → mfa-setup → login → mfa-verify flow issues a session, and every attempt (success/failure) produces an audit entry, in `backend/services/auth-service/test/integration/auth-flow.spec.ts`

### Implementation for User Story 1

- [X] T021 [P] [US1] Create `User` Prisma repository/model access layer in `backend/services/auth-service/src/users/user.repository.ts`
- [X] T022 [US1] Implement `RegisterService` (email/password + Google OAuth registration) in `backend/services/auth-service/src/auth/register.service.ts` (depends on T021)
- [X] T023 [US1] Implement MFA setup (TOTP secret generation + `otpauth://` QR payload) in `backend/services/auth-service/src/auth/mfa-setup.service.ts`
- [X] T024 [US1] Implement `LoginService` (credential check → MFA challenge token issuance, no session token yet) in `backend/services/auth-service/src/auth/login.service.ts`
- [X] T025 [US1] Implement `MfaVerifyService` (TOTP code validation → access + refresh token issuance) in `backend/services/auth-service/src/auth/mfa-verify.service.ts` (depends on T013, T023)
- [X] T026 [US1] Implement `POST /auth/refresh` handler (rotation, reuse detection, family revocation) in `backend/services/auth-service/src/auth/refresh.controller.ts` (depends on T013)
- [X] T027 [US1] Implement `POST /auth/logout` handler (revoke current token family) in `backend/services/auth-service/src/auth/logout.controller.ts` (depends on T013)
- [X] T028 [US1] Wire `AuditLogService` writes into register/login/mfa-verify/refresh flows (`login_success`, `login_failure`, `mfa_failure`, `token_reuse_detected`) across `backend/services/auth-service/src/auth/*.ts` (depends on T012)
- [X] T029 [US1] Implement `GET /me` endpoint in `backend/services/auth-service/src/users/me.controller.ts`
- [X] T030 [P] [US1] Build frontend Register page in `frontend/src/features/auth/RegisterPage.tsx`
  > **UI Reference**: `ui-prototypes/frontend-register.html`
  > **Sections to implement**:
  > - إنشاء حساب جديد في علم -> `#main`
  > **Implementation rule**: Match the approved HTML prototype. Visual changes require approval.
- [X] T031 [P] [US1] Build frontend MFA setup page (QR display) in `frontend/src/features/auth/MfaSetupPage.tsx`
  > **UI Reference**: `ui-prototypes/frontend-mfa-setup.html`
  > **Sections to implement**:
  > - إعداد التحقق بخطوتين -> `#main`
  > **Implementation rule**: Match the approved HTML prototype. Visual changes require approval.
- [X] T032 [P] [US1] Build frontend Login and MFA-verify pages in `frontend/src/features/auth/LoginPage.tsx` and `frontend/src/features/auth/MfaVerifyPage.tsx`
  > **UI Reference**: none — no dedicated Login/MFA-verify prototype exists in `ui-prototypes/`. Only Register, MFA-setup, and the role-scoped dashboard were generated in Phase 0.
- [X] T033 [US1] Implement frontend auth API client with token storage and silent-refresh interceptor in `frontend/src/features/auth/authClient.ts` (depends on T030, T031, T032)
- [X] T034 [US1] Add inline, localized validation and error handling to all auth screens in `frontend/src/features/auth/` (depends on T033)

### Design System Restyle for User Story 1 (SimpleElm Design System.zip)

**UI Reference**: `ui_kits/auth/AuthKit.jsx` (`Shell`, `Auth`, `Mfa` components) — see plan.md conflicts #2, #3, #5, #6, #7. T030–T034 above are functionally complete but currently render generic unbranded Tailwind, not the approved design; these tasks bring them to visual parity without changing any route, prop, or API call.

- [ ] T078 [P] [US1] Restyle `RegisterPage.tsx` and `LoginPage.tsx` to share one tabbed auth-card shell (Sign in / Register tabs, logo, welcome text) per `AuthKit.jsx` `Auth()` — keep the two existing routes and existing 2-role (Learner, Course Provider/Instructor) self-registration scope, adopting only the pill/card role-selector *visual* style from the kit's 6-way demo picker (depends on T076, T077)
  > **States to cover**: default, focus (input ring), inline validation error, submitting/disabled, both tabs' hover/active state, both themes, both languages.
- [ ] T079 [US1] Add "Continue with Google" social sign-in button (visual per `AuthKit.jsx` `Auth()`) to the shared auth card and wire it to the backend's existing `passport-google-oauth20` route — closes the FR-002 gap where no social sign-in entry point currently exists in the frontend (depends on T078)
- [ ] T080 [US1] Restyle `MfaSetupPage.tsx` (TOTP QR enrollment) using the SimpleElm card shell, shield-check icon avatar, and type/spacing tokens — no direct `AuthKit.jsx` specimen exists for this step (verify-only kit), so compose from the same primitives used elsewhere; render an actual QR image from the existing `otpauthUrl` instead of raw secret text only (depends on T076)
- [ ] T081 [US1] Restyle `MfaVerifyPage.tsx` as 6 individual boxed digit inputs with auto-advance, per-box focus/error border, resend/back actions, per `AuthKit.jsx` `Mfa()` — replace the current single free-text code input; server-side TOTP verification via `authClient.ts` is unchanged (depends on T076)
- [ ] T082 [P] [US1] Verify inline/localized error states on all restyled US1 screens use the `--se-danger` token consistently (Input error border + Badge/error text), in both AR and EN (depends on T078, T079, T080, T081)

**Checkpoint**: User Story 1 fully functional, independently testable, and visually matches the approved SimpleElm Design System in both themes and both languages

---

## Phase 4: User Story 2 - Role-Scoped Access (Priority: P2)

**Goal**: An authenticated user can perform only the actions their role (of six) permits; unpermitted actions are denied and logged; instructors cannot reach each other's resources.

**Independent Test**: Sign in as each of the six roles and confirm each performs only its permitted actions; confirm an instructor cannot access another instructor's course; confirm a customized Supervisor override changes the enforced boundary.

### Tests for User Story 2 ⚠️

- [X] T035 [P] [US2] Contract test `GET /rbac/permissions/me` in `backend/services/tenancy-service/test/contract/rbac-permissions.spec.ts`
- [X] T036 [P] [US2] Contract test `PUT /rbac/supervisor-overrides/:userId` (Owner/Admin-only) in `backend/services/tenancy-service/test/contract/supervisor-overrides.spec.ts`
- [X] T037 [P] [US2] Integration test: each of six roles performs only permitted actions; instructor cannot access another instructor's course/learners in `backend/services/tenancy-service/test/integration/rbac-enforcement.spec.ts`

### Implementation for User Story 2

- [X] T038 [P] [US2] Define default per-role permission matrix (config/seed) in `backend/services/tenancy-service/src/rbac/permission-matrix.ts`
- [X] T039 [P] [US2] Create `SupervisorPermissionOverride` Prisma repository in `backend/services/tenancy-service/src/rbac/supervisor-override.repository.ts`
- [X] T040 [US2] Implement `RbacService` (merges role defaults with Supervisor overrides) in `backend/services/tenancy-service/src/rbac/rbac.service.ts` (depends on T038, T039)
- [X] T041 [US2] Implement `GET /rbac/permissions/me` endpoint in `backend/services/tenancy-service/src/rbac/permissions.controller.ts` (depends on T040)
- [X] T042 [US2] Implement `PUT /rbac/supervisor-overrides/:userId` endpoint restricted to Owner/Administrator in `backend/services/tenancy-service/src/rbac/supervisor-overrides.controller.ts` (depends on T040)
- [X] T043 [US2] Apply `@RequirePermission` decorators + `RbacGuard` to all protected US1 routes in `backend/services/auth-service/src/**/*.controller.ts` and `backend/services/tenancy-service/src/**/*.controller.ts` (depends on T011, T040)
- [X] T044 [US2] Wire `permission_denied` audit writes into `RbacGuard` in `backend/services/shared/src/guards/rbac.guard.ts` (depends on T012, T011)
- [X] T045 [P] [US2] Build frontend `usePermissions` hook consuming `GET /rbac/permissions/me` in `frontend/src/shared/rbac/usePermissions.ts`
- [X] T046 [P] [US2] Build role-scoped dashboard shell (renders only permitted sections per role) in `frontend/src/features/dashboard/DashboardPage.tsx` (depends on T045)
  > **UI Reference**: `ui-prototypes/role-scoped.html`
  > **Sections to implement**:
  > - الإجراءات المتاحة لدورك -> `#main`
  > **Implementation rule**: Match the approved HTML prototype. Visual changes require approval.
- [X] T047 [US2] Build localized "You don't have access" denial view in `frontend/src/shared/rbac/ForbiddenView.tsx` (depends on T045)

### Design System Restyle for User Story 2 (SimpleElm Design System.zip)

**UI Reference**: `ui_kits/auth/AuthKit.jsx` `Dashboard()` component.

- [ ] T083 [US2] Restyle `DashboardPage.tsx` per `AuthKit.jsx` `Dashboard()`: role icon avatar + role name, tenant badge, `StatItem` stat cards, quick-actions list, activity feed layout — keep the existing permission-gated `SECTIONS` array as the functional source of truth (which sections render), mapping each *permitted* section onto the quick-actions/stat-card visual pattern rather than AuthKit's static per-role demo buckets (depends on T076, T045, T070–T077)
  > **States to cover**: 0/1/many visible sections (role with few permissions vs. many), loading state, both themes, both languages, RTL icon mirroring (chevron direction) per `AuthKit.jsx`.
- [ ] T084 [US2] Restyle `ForbiddenView.tsx` "you don't have access" state using SimpleElm `Card`/`Badge`(danger tone) tokens instead of default Tailwind (depends on T076)

**Checkpoint**: User Stories 1 AND 2 both work independently and match the approved design system

---

## Phase 5: User Story 3 - Tenant-Isolated Access (Priority: P3)

**Goal**: A user in one tenant never sees, affects, or is affected by another tenant's data; requests without resolvable tenant context are rejected; cross-tenant attempts are denied and logged.

**Independent Test**: Provision two tenants; confirm every read/write a user performs stays within their own tenant; confirm a request with mismatched/missing tenant context is rejected before any data access; confirm cross-tenant attempts are logged as suspicious.

### Tests for User Story 3 ⚠️

- [X] T048 [P] [US3] Integration test: two-tenant isolation — no cross-tenant row is ever returned across auth/RBAC endpoints in `backend/services/tenancy-service/test/integration/tenant-isolation.spec.ts`
- [X] T049 [P] [US3] Contract test `GET /tenants/:id` cross-tenant denial (403 + audit entry) in `backend/services/tenancy-service/test/contract/tenants.spec.ts`
- [X] T050 [P] [US3] Integration test: request with missing/mismatched tenant context is rejected before data access in `backend/services/shared/test/integration/tenant-context-guard.spec.ts`

### Implementation for User Story 3

- [X] T051 [US3] Create `Tenant` Prisma repository in `backend/services/tenancy-service/src/tenants/tenant.repository.ts`
- [X] T052 [US3] Implement `GET /tenants/:id` endpoint enforcing same-tenant-only access in `backend/services/tenancy-service/src/tenants/tenants.controller.ts` (depends on T051)
- [X] T053 [US3] Wire `TenantContextGuard` into both services' global guard pipeline in `backend/services/auth-service/src/main.ts` and `backend/services/tenancy-service/src/main.ts` (depends on T010)
- [X] T054 [US3] Author and apply Postgres RLS policies for all tenant-scoped tables in `backend/services/shared/prisma/migrations/` (depends on T008, T009)
- [X] T055 [US3] Wire `cross_tenant_attempt` audit writes into `TenantContextGuard` in `backend/services/shared/src/guards/tenant-context.guard.ts` (depends on T012, T010)
- [X] T056 [P] [US3] Seed two isolated test tenants for local/dev/test environments in `backend/services/shared/prisma/seed.ts`

**Checkpoint**: All user stories 1–3 independently functional; isolation verified

---

## Phase 6: User Story 4 - Bilingual, Direction-Aware Experience (Priority: P4)

**Goal**: Registration, sign-in, MFA, and the role-scoped dashboard render fully in Arabic (RTL) or English (LTR), including notifications, with graceful fallback on missing translations.

**Independent Test**: Switch language between Arabic and English and confirm every US1–US3 screen re-renders with correct localized text and layout direction; remove a translation key and confirm English fallback + gap logging instead of a broken screen.

### Tests for User Story 4 ⚠️

- [X] T057 [P] [US4] Playwright e2e test: AR/EN + RTL/LTR rendering across register/login/MFA/dashboard in `frontend/tests/e2e/bilingual.spec.ts`
- [X] T058 [P] [US4] Unit test: missing translation key falls back to English and logs the gap in `frontend/tests/unit/i18n-fallback.spec.ts`

### Implementation for User Story 4

- [X] T059 [P] [US4] Populate full `ar.json`/`en.json` resource bundles for all US1–US3 screens in `frontend/src/i18n/ar.json` and `frontend/src/i18n/en.json` (depends on T030, T031, T032, T046, T047)
- [X] T060 [US4] Implement language switcher with persisted `User.locale` update in `frontend/src/features/dashboard/LanguageSwitcher.tsx` (depends on T059)
- [X] T061 [US4] Implement backend locale-aware message resolver for notifications in `backend/services/shared/src/i18n/message-resolver.ts` (depends on T012)
- [X] T062 [US4] Audit and apply Tailwind logical-properties (RTL-safe) styling across all US1–US3 components in `frontend/src/features/` and `frontend/src/shared/` (depends on T059)
- [X] T063 [US4] Wire missing-translation-key fallback + gap logging in `frontend/src/i18n/i18next-config.ts` (depends on T059)

### Design System Restyle for User Story 4 (SimpleElm Design System.zip)

**UI Reference**: `ui_kits/auth/AuthKit.jsx` `Shell()` component (header: logo, language toggle, theme toggle).

- [ ] T085 [US4] Restyle `LanguageToggle.tsx`/`LanguageSwitcher.tsx` as the SimpleElm pill toggle (languages icon + current-language label) per `AuthKit.jsx` `Shell()`, replacing default Tailwind button styling (depends on T076)
- [ ] T086 [US4] Extend `AppShell.tsx` into the full SimpleElm shell — sticky `72px` header (`--header-h`), `Logo`, language toggle, and theme toggle (T075) in the header row — replacing the hardcoded `bg-white text-gray-900` — and confirm Tailwind logical-properties usage (T062) still holds across the new header markup (depends on T075, T077, T085)

**Checkpoint**: All four user stories independently functional, visually matching the approved SimpleElm Design System — Phase 1 validation target ("register, sign in with MFA, and access a role-scoped, localized dashboard within an isolated tenant") is met

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T064 [P] Run all quickstart.md validation scenarios end-to-end
- [X] T065 [P] WCAG 2.1 AA accessibility pass (focus states, ARIA labels, contrast) across `frontend/src/features/auth/` and `frontend/src/features/dashboard/`
- [ ] T066 [P] Load-test auth and RBAC endpoints; confirm API p95 < 500ms per constitution Principle VII
- [X] T067 Security hardening pass: rate-limit `/auth/login` and `/auth/mfa/verify`, confirm AES-256-at-rest and TLS 1.3 config in deployment manifests
- [X] T068 [P] Update local-dev setup documentation in `docs/`
- [ ] T069 Remove any remaining scaffold/placeholder code and finalize commit history
- [ ] T087 [P] Pixel-fidelity sign-off: compare every restyled US1/US2/US4 screen against `ui_kits/auth/AuthKit.jsx` and `guidelines/*.card.html` specimens in both light/dark themes and both AR/EN languages (depends on T078–T086)
- [ ] T088 [P] Mark `ui-prototypes/*.html` and `.ui-bridge/design-system.*` as superseded historical artifacts (note in `ui-prototypes/prototype-hub.html`) now that `SimpleElm Design System.zip` is canonical (depends on T087)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **Design System Foundation (Phase 0.5)**: No hard dependency on Phase 1/2 (pure frontend tokens/primitives) but in practice runs alongside/after Setup, since it lives entirely in `frontend/`; BLOCKS every restyle task (T078–T086) in Phases 3, 4, and 6
- **User Story 1 (Phase 3)**: Functional tasks (T017–T034) depend on Foundational only; restyle tasks (T078–T082) additionally depend on Design System Foundation (T070–T077)
- **User Story 2 (Phase 4)**: Functional tasks depend on Foundational; T043 also depends on US1's routes existing (T022–T029) to decorate; restyle tasks (T083–T084) additionally depend on Design System Foundation and T045
- **User Story 3 (Phase 5)**: Depends on Foundational; independently testable once T053 wires the shared guard, but T054's RLS policies apply to tables introduced across Foundational + US1 + US2. No design-system restyle work applies to this story (backend-only).
- **User Story 4 (Phase 6)**: Functional tasks depend on Foundational; its implementation tasks (T059, T062) apply localization on top of the screens built in US1–US3, so it is sequenced last even though the i18n scaffold itself (T015, T016) is Foundational; restyle tasks (T085–T086) additionally depend on Design System Foundation, particularly the theme toggle (T075)
- **Polish (Phase 7)**: Depends on all four user stories being complete; T087/T088 additionally depend on all restyle tasks (T078–T086)

### Parallel Opportunities

- All `[P]` Setup tasks (T003–T006) run in parallel
- All `[P]` Foundational tasks (T010–T013, T015, T016) run in parallel after T008/T009
- Tests within a story phase (all `[P]`) run in parallel before that story's implementation tasks
- T021, and the frontend pages T030–T032, run in parallel within US1
- T038/T039 run in parallel within US2; T045/T046 run in parallel on the frontend side
- T048/T049/T050 run in parallel within US3
- T057/T058 run in parallel within US4

---

## Parallel Example: User Story 1

```bash
# Tests together:
Task: "Contract test POST /auth/register in backend/services/auth-service/test/contract/register.spec.ts"
Task: "Contract test POST /auth/login + /auth/mfa/verify in backend/services/auth-service/test/contract/login-mfa.spec.ts"
Task: "Contract test POST /auth/refresh in backend/services/auth-service/test/contract/refresh.spec.ts"

# Frontend pages together:
Task: "Build Register page in frontend/src/features/auth/RegisterPage.tsx"
Task: "Build MFA setup page in frontend/src/features/auth/MfaSetupPage.tsx"
Task: "Build Login and MFA-verify pages in frontend/src/features/auth/LoginPage.tsx and MfaVerifyPage.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (blocks everything else)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: run quickstart.md Scenario 1 + 2 independently
5. Demo: a user can register, set up MFA, sign in, and hold a rotating session — before any RBAC, tenancy, or localization work exists

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. Add US1 → validate (quickstart Scenario 1–2) → demo (MVP)
3. Add US2 → validate (quickstart Scenario 3) → demo
4. Add US3 → validate (quickstart Scenario 4) → demo
5. Add US4 → validate (quickstart Scenario 5) → demo — Phase 1 validation target fully met
6. Polish

### Parallel Team Strategy

With multiple developers, after Foundational is done: one developer on US1
(auth-service core), one on US2 (RBAC, can stub against US1's contract until
it lands), one on US3 (tenancy-service + RLS), and frontend work in US1/US2/US4
can proceed in parallel against the contracts in `contracts/`.

---

## Notes

- `[P]` tasks touch different files with no unfinished dependency
- `[Story]` labels give per-task traceability back to spec.md's prioritized user stories
- Tests are included per the constitution's mandatory tenant-isolation and RBAC test-coverage gates — write and confirm they fail before implementing the corresponding task
- Commit after each task or logical group
- Stop at any Checkpoint to validate a story independently before continuing
