# Feature Specification: Phase 1 — Foundation (Auth, RBAC, Tenancy, Bilingual Shell)

**Feature Branch**: `001-phase-1-foundation`

**Created**: 2026-08-11

**Status**: Draft

**Input**: User description: "Phase 1: Foundation of the Elm Platform (منصة علم), per docs/PRD.md Section 10 Phase 1 — Authentication + MFA (P0-F001), RBAC across six roles (P0-F002), Multi-tenant isolation (P0-F003), Bilingual AR/EN + RTL/LTR shell (P0-F011). Validation target: 'A user can register, sign in with MFA, and access a role-scoped, localized dashboard within an isolated tenant.'"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Secure Registration & Sign-In (Priority: P1)

Any platform user (learner, instructor, or staff) registers an account or signs
in with an existing one, and confirms their identity with a second factor (MFA)
before reaching any part of the platform.

**Why this priority**: Nothing else in the platform is safe or meaningful
without a trustworthy identity boundary. This is the single feature every other
Phase 1 story — and every later phase — depends on.

**Independent Test**: Can be fully tested by registering a new account, signing
in with valid credentials, completing an MFA challenge, and confirming a session
is granted; and by confirming that invalid credentials or a failed/expired MFA
code never grant a session. Delivers value on its own as a working front door
to the platform, even before role-based dashboards or tenant scoping exist.

**Acceptance Scenarios**:

1. **Given** a new user provides a valid email and password, **When** they
   submit registration, **Then** an account is created in an inactive-until-
   verified or active state per the chosen verification policy, and the user is
   prompted to set up MFA.
2. **Given** a registered, active user enters correct credentials, **When**
   they submit sign-in, **Then** the system prompts for an MFA code.
3. **Given** a user has been prompted for MFA, **When** they submit a valid,
   unexpired MFA code, **Then** the system issues an access token and a refresh
   token and routes the user onward.
4. **Given** a user enters incorrect credentials, **When** they submit sign-in,
   **Then** the system rejects the attempt with an inline error and issues no
   token.
5. **Given** a user enters an invalid or expired MFA code, **When** they
   submit it, **Then** the system rejects the attempt, offers retry or resend,
   and issues no token.
6. **Given** an authenticated session's refresh token is used to obtain a new
   access token, **When** the refresh succeeds, **Then** the prior refresh
   token is invalidated (rotation) so it cannot be reused.
7. **Given** any sign-in attempt (successful or failed), **When** it completes,
   **Then** the attempt is recorded in an audit log.

---

### User Story 2 - Role-Scoped Access (Priority: P2)

An authenticated user only sees and can perform the actions permitted to their
assigned role — one of Platform Owner, Platform Administrator, Platform
Supervisor, Course Provider/Instructor, Teaching Assistant, or Learner — and is
blocked from everything else.

**Why this priority**: Once identity exists (P1), the platform must immediately
constrain what that identity can do. Every later feature (courses, payments,
content protection) is built on top of this permission boundary, so it must be
proven before those features are built.

**Independent Test**: Can be fully tested by signing in as a user of each of
the six roles and confirming each can perform only their permitted actions,
that unpermitted actions return a clear denial, and that an instructor cannot
reach another instructor's resources. Delivers value on its own as a working
permission boundary, independent of tenancy or localization.

**Acceptance Scenarios**:

1. **Given** an authenticated user with a specific role, **When** they request
   an action their role permits, **Then** the action proceeds.
2. **Given** an authenticated user with a specific role, **When** they request
   an action their role does not permit, **Then** the system denies the action
   with a clear "insufficient permission" response and the denial is logged.
3. **Given** a Course Provider/Instructor, **When** they attempt to access
   another instructor's course or learner data, **Then** access is denied.
4. **Given** a Platform Administrator, **When** they attempt an ownership-level
   action reserved for the Platform Owner (e.g., billing ownership, permission-
   scheme definition, tenant provisioning), **Then** access is denied.
5. **Given** a Platform Supervisor with a customized (reduced or expanded)
   permission set, **When** they act within their configured boundary, **Then**
   the system enforces that specific configured boundary rather than a fixed
   default.

---

### User Story 3 - Tenant-Isolated Access (Priority: P3)

A user belonging to one tenant (organization/instance) never sees, affects, or
can be affected by data belonging to another tenant, regardless of role.

**Why this priority**: This is the platform's core multi-tenant trust
guarantee. It builds on identity (P1) and roles (P2) — a role only means
something once it is also correctly scoped to the right tenant — but is
sequenced after them because it can be independently verified once a user and
a role exist.

**Independent Test**: Can be fully tested by provisioning two tenants with
their own users, and confirming that every read/write a user performs is
confined to their own tenant, that requests without resolvable tenant context
are rejected, and that any cross-tenant attempt is denied and logged. Delivers
value on its own as a verifiable isolation guarantee.

**Acceptance Scenarios**:

1. **Given** an authenticated user in Tenant A, **When** they request any data
   or action, **Then** only Tenant A's data is ever returned or affected.
2. **Given** a request that cannot resolve a tenant context (e.g., malformed
   token/subdomain), **When** it reaches the system, **Then** the request is
   rejected.
3. **Given** a user attempts to access a resource belonging to a different
   tenant than their own, **When** the attempt is made, **Then** the system
   denies it and logs it as a suspicious event.

---

### User Story 4 - Bilingual, Direction-Aware Experience (Priority: P4)

Any user can use the entire Phase 1 experience (registration, sign-in, MFA,
and their role-scoped dashboard) fully in Arabic with right-to-left layout, or
fully in English with left-to-right layout, including notifications.

**Why this priority**: Bilingual, RTL-first support is a stated market
differentiator, not a cosmetic layer, so it is validated as its own story. It
is sequenced last only because it wraps the experiences built in P1–P3 rather
than gating them — but it is still required for Phase 1 to be considered done,
per the PRD's own Phase 1 validation target.

**Independent Test**: Can be fully tested by switching the platform language
between Arabic and English and confirming every screen in the registration,
sign-in, MFA, and dashboard flows re-renders with correct localized text and
correct layout direction, and that a missing translation falls back to English
visibly and is logged rather than breaking the screen.

**Acceptance Scenarios**:

1. **Given** a user selects Arabic, **When** any Phase 1 screen renders,
   **Then** all UI text is in Arabic and the layout is right-to-left.
2. **Given** a user selects English, **When** any Phase 1 screen renders,
   **Then** all UI text is in English and the layout is left-to-right.
3. **Given** a notification is generated for a user (e.g., MFA prompt, denial
   message), **When** it is delivered, **Then** it is in the user's selected
   language.
4. **Given** a UI string has no translation for the selected language, **When**
   the screen renders, **Then** the system falls back to English for that
   string and logs the missing-translation gap instead of showing a raw key or
   failing.

---

### Edge Cases

- What happens when a user tries to register with an email already in use in
  the same tenant? System MUST reject with a clear, localized error.
- What happens when a user's refresh token has already been rotated/invalidated
  and is replayed (e.g., stolen token reuse)? System MUST deny the refresh and
  MAY treat this as a suspicious-activity signal.
- How does the system handle a user with no role assigned yet (e.g., mid-
  onboarding)? System MUST NOT grant access to any role-scoped area until a
  role is assigned within a tenant.
- What happens when a Platform Supervisor's customized permission set is
  changed while they have an active session? System MUST apply the updated
  boundary no later than the next permission check (does not require immediate
  forced logout).
- How does the system handle a request whose tenant subdomain/token disagree
  with each other? System MUST reject the request as a tenant-mismatch and log
  it as suspicious, per Multi-Tenant Isolation acceptance criteria.
- What happens when MFA setup is interrupted before completion? System MUST
  leave the account without a granted session and allow the user to resume MFA
  setup on next sign-in attempt.

## Requirements *(mandatory)*

### Functional Requirements

**Authentication + MFA**
- **FR-001**: System MUST allow a user to register an account with email and
  password within a tenant.
- **FR-002**: System MUST support social sign-in as an alternative registration
  and sign-in path.
- **FR-003**: System MUST require a second-factor (MFA) code after correct
  primary credentials before granting a session.
- **FR-004**: System MUST issue an access token and a refresh token upon
  successful authentication (credentials + MFA).
- **FR-005**: System MUST rotate refresh tokens on use and invalidate the prior
  token so it cannot be reused.
- **FR-006**: System MUST reject sign-in on invalid credentials without issuing
  any token.
- **FR-007**: System MUST reject an invalid or expired MFA code and allow the
  user to retry or request a new code.
- **FR-008**: System MUST record every authentication attempt (success and
  failure) in an audit log.

**RBAC (Six Roles)**
- **FR-009**: System MUST support exactly six roles: Platform Owner, Platform
  Administrator, Platform Supervisor, Course Provider/Instructor, Teaching
  Assistant, and Learner.
- **FR-010**: System MUST check every request to a protected action against a
  permission matrix resolved from the user's role (and, for Supervisor, any
  configured customization) before allowing it to proceed.
- **FR-011**: System MUST deny and log any action a user's role does not
  permit, returning a clear denial rather than a silent failure or generic
  error.
- **FR-012**: System MUST prevent a Course Provider/Instructor from accessing
  another instructor's courses, learners, or analytics.
- **FR-013**: System MUST reserve ownership-level actions (billing ownership,
  permission-scheme definition, tenant provisioning) to the Platform Owner role
  only.
- **FR-014**: System MUST allow a Platform Owner or Administrator to customize
  the Platform Supervisor role's permission grants within defined bounds, and
  MUST enforce that customized boundary once configured.

**Multi-Tenant Isolation**
- **FR-015**: System MUST resolve a tenant context for every request from the
  authenticated token or subdomain before any data access occurs.
- **FR-016**: System MUST scope every data read and write to the resolved
  tenant context; no query may span tenants implicitly.
- **FR-017**: System MUST reject any request that lacks a resolvable tenant
  context.
- **FR-018**: System MUST deny and log as suspicious any request whose
  resolved tenant does not match the tenant that owns the requested resource.

**Bilingual AR/EN (RTL/LTR)**
- **FR-019**: System MUST allow a user to select Arabic or English at any
  point, and MUST persist that preference for the user going forward.
- **FR-020**: System MUST render all UI text for registration, sign-in, MFA,
  and the role-scoped dashboard from localized resources — no hardcoded
  user-facing strings.
- **FR-021**: System MUST render right-to-left layout when Arabic is selected
  and left-to-right layout when English is selected, across all Phase 1
  screens.
- **FR-022**: System MUST deliver notifications and system messages (e.g., MFA
  prompts, denial messages, registration confirmations) in the user's selected
  language.
- **FR-023**: System MUST fall back to English and log the gap when a
  translation key is missing for the selected language, rather than displaying
  a raw key or failing the screen.

### Key Entities *(include if feature involves data)*

- **Tenant**: A single isolated organization/instance of the platform. Key
  attributes: identifier, name, domain, status. All other entities in this
  feature belong to exactly one tenant.
- **User**: An individual account within a tenant. Key attributes: identifier,
  tenant reference, email, assigned role, MFA enrollment state, language
  preference. Relationships: belongs to one Tenant; has one Role.
- **Role / Permission Grant**: The named role (one of six) assigned to a User,
  plus — for Platform Supervisor only — an optional customized set of
  permission grants layered on the role's default boundary.
- **Session / Token**: The result of a successful authentication — an access
  token and a rotating refresh token tied to a User and their resolved Tenant.
- **Audit Log Entry**: A record of an authentication attempt, permission
  denial, or cross-tenant access attempt, including outcome and timestamp.
- **Localization Preference**: The selected language (Arabic or English) and
  resulting layout direction (RTL/LTR) associated with a User.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new user can complete registration, MFA setup, sign-in, and
  reach their role-scoped dashboard in under 3 minutes on first attempt.
- **SC-002**: 100% of cross-tenant access attempts made during isolation
  testing are denied and logged — zero tenant-boundary breaches.
- **SC-003**: 100% of role/permission acceptance tests across all six roles
  confirm each role can perform only its permitted actions.
- **SC-004**: 100% of Phase 1 screens (registration, sign-in, MFA, dashboard)
  render correctly in both Arabic (RTL) and English (LTR) with no untranslated
  raw keys visible to the user.
- **SC-005**: 100% of authentication attempts (success and failure) and 100%
  of permission denials appear in the audit log within the same request cycle.
- **SC-006**: No valid session is ever granted on invalid credentials or an
  invalid/expired MFA code, across all tested failure scenarios.

## Assumptions

- MFA is implemented as a time-based one-time code (authenticator-app style);
  SMS/email-OTP as additional MFA channels are not required for Phase 1 but are
  not precluded by this spec.
- Social sign-in covers at least one major identity provider (e.g., Google);
  the specific provider set is a planning-time decision, not a scoping
  decision, since the PRD only specifies "social sign-in" generally.
- "Register" in Phase 1 covers Learner and Instructor self-registration; staff
  roles (Owner, Administrator, Supervisor, Teaching Assistant) are assumed to
  be provisioned/invited within a tenant rather than self-registering, since
  the PRD does not describe open self-registration for governance roles.
- Email verification before first sign-in is assumed as a standard practice
  but is not itself a P0 acceptance criterion in the PRD; if omitted, account
  activation is assumed immediate upon registration.
- The specific access-token lifetime and refresh-token TTL are planning-time
  decisions; this spec only requires that rotation and invalidation behavior
  hold, per PRD acceptance criteria for P0-F001.
- Existing cloud-native infrastructure (Kubernetes-ready) is available, per the
  PRD's stated assumptions, so this spec does not re-litigate infrastructure
  availability.
