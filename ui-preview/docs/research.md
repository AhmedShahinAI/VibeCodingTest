# Phase 0 Research: Phase 1 — Foundation

All Technical Context items were resolved during planning (none required
external spikes); this document records the decisions and alternatives
considered, resolving the spec's Assumptions into concrete choices.

## MFA Method

**Decision**: Time-based One-Time Password (TOTP) via authenticator app
(`otplib` server-side, standard `otpauth://` QR provisioning on setup).

**Rationale**: No SMS gateway dependency, cost, or regional carrier-delivery
reliability risk across the Arabic-speaking markets the platform targets;
works without a live network round-trip to a third party; is the de facto
standard for SaaS MFA and satisfies constitution Principle I without
introducing a new vendor dependency (PRD Section 9 does not list an SMS
provider).

**Alternatives considered**:
- SMS OTP — rejected: added telecom vendor dependency, per-message cost, and
  variable regional delivery reliability.
- Email OTP — rejected: weaker security (email account compromise defeats
  it), slower user flow, and email delivery is not guaranteed real-time.

## Social Sign-In Provider

**Decision**: Google OAuth 2.0 (`passport-google-oauth20`) as the sole
provider for Phase 1.

**Rationale**: PRD P0-F001 only specifies "email/social sign-in" without
naming a provider. Google has the widest reach for the target user base and
the lowest integration cost via a mature Passport strategy. Additional
providers (Microsoft, Apple) are additive later and do not change the auth
data model, so deferring them does not create rework.

**Alternatives considered**:
- Microsoft/Apple sign-in — deferred, not rejected: no PRD signal these are
  required for launch; can be added as additional Passport strategies without
  schema changes.

## Token Lifetimes & Rotation

**Decision**: Access token TTL = 15 minutes (JWT, RS256-signed). Refresh
token TTL = 30 days, sliding, single-use with rotation — each refresh issues a
new refresh token and immediately invalidates the prior one in Redis; reuse of
an already-rotated refresh token revokes the entire token family and is logged
as a suspicious event.

**Rationale**: A short access-token window limits the blast radius of a leaked
token without forcing re-authentication on every request; rotation-with-
reuse-detection is the standard mitigation for stolen refresh tokens and
directly satisfies spec FR-005/FR-006 and constitution Principle I
(Zero-Trust).

**Alternatives considered**:
- Long-lived non-rotating refresh tokens — rejected: violates FR-005
  (rotation required) and the constitution's Zero-Trust principle.
- Server-side session cookies only (no JWT) — rejected: conflicts with PRD
  Section 9's explicit "JWT with refresh-token rotation" mandate and with the
  microservices' need for a stateless, verifiable token passed between
  services.

## Data Access Layer

**Decision**: Prisma ORM against PostgreSQL, with Postgres Row-Level Security
(RLS) policies on every tenant-scoped table as a second, database-enforced
layer beneath Prisma's application-level `tenant_id` filtering.

**Rationale**: Prisma gives compile-time-checked queries and a straightforward
migration workflow, reducing the chance of an accidental unscoped query (a
direct risk to constitution Principle II). RLS provides defense-in-depth: even
a bug in application-level scoping cannot return cross-tenant rows, directly
supporting spec SC-002 ("100% of cross-tenant access attempts... denied").

**Alternatives considered**:
- TypeORM — rejected: weaker compile-time query safety than Prisma for this
  team's needs; migration ergonomics are worse for a schema this shape.
- Per-tenant database/schema instead of RLS — rejected for Phase 1: PRD states
  a < 5,000 MAU launch target; per-tenant DB provisioning overhead is not
  justified yet. Revisit if/when the PRD's 10x scale target requires it — RLS
  plus application scoping is the documented interim isolation strategy.

## Tenant Resolution

**Decision**: Tenant is resolved once per request in a shared
`TenantContextGuard` from the JWT's `tenant_id` claim, cross-checked against
the resolved subdomain when present; the resolved tenant is attached to the
request context and is the only source later guards/services trust.

**Rationale**: Centralizing resolution in one guard (used by both
`auth-service` and `tenancy-service` via the shared library) is what makes
FR-015/FR-017/FR-018 enforceable uniformly rather than re-implemented per
endpoint.

## RBAC Enforcement

**Decision**: Declarative NestJS route decorators (e.g.,
`@RequirePermission('course.publish')`) checked by a shared `RbacGuard`
against a permission matrix. Default per-role grants are seeded/config-driven;
Platform Supervisor may additionally have per-tenant override rows
(`SupervisorPermissionOverride`) layered on top of the role default.

**Rationale**: A declarative, centrally-enforced check (rather than ad hoc
in-controller `if` checks) is required so FR-010/FR-011 hold for every
endpoint by construction, and so `/speckit-analyze` can later verify coverage
mechanically (every protected route must carry the decorator).

## Localization & RTL/LTR

**Decision**: `react-i18next` with per-namespace JSON resource files
(`ar.json`, `en.json`); layout direction driven by a single `dir` attribute on
the document root, computed from the selected language; Tailwind configured
with logical properties (`ms-*`/`me-*`/`ps-*`/`pe-*` etc.) instead of
physical `left`/`right` utilities so RTL/LTR do not require duplicated
styles.

**Rationale**: i18next's built-in fallback-language behavior directly
satisfies FR-023 (fallback to English + log the gap) with a documented,
low-code hook rather than a custom implementation. Logical-properties CSS
avoids a second, RTL-specific stylesheet to maintain.

## Audit Logging

**Decision**: Audit log entries (auth attempts, permission denials,
cross-tenant attempts) are written synchronously, in the same database
transaction as the action they record, to an append-only, tenant-scoped
`audit_log` table.

**Rationale**: Spec SC-005 requires logging "within the same request cycle" —
an async/queued write could be lost on crash between the action and the log
write, which is unacceptable for a security audit trail per constitution
Principle I.

**Alternatives considered**:
- Async logging via a queue (e.g., for lower request latency) — rejected for
  auth/permission events specifically: the durability requirement (SC-005)
  outweighs the latency cost, and MFA/login are not high-frequency-enough
  endpoints for synchronous writes to threaten the p95 < 500ms budget.
