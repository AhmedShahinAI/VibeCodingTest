# Quickstart: Validating Phase 1 — Foundation

Validates the spec's Phase 1 target: *"A user can register, sign in with MFA,
and access a role-scoped, localized dashboard within an isolated tenant."*
References [contracts/auth-api.md](./contracts/auth-api.md),
[contracts/tenancy-api.md](./contracts/tenancy-api.md), and
[data-model.md](./data-model.md) for exact payloads/schemas.

## Prerequisites

- `backend/services/auth-service` and `backend/services/tenancy-service`
  running (e.g., via local `docker-compose` with Postgres 15 + Redis 7).
- Database migrated and seeded with two tenants (`tenant-a`, `tenant-b`) to
  exercise isolation scenarios.
- `frontend` dev server running against the two services.

## Scenario 1 — Secure Registration & Sign-In (User Story 1, SC-001, SC-006)

1. `POST /api/v1/auth/register` on `tenant-a` with a new email/password/role.
   Expect `201` with `mfaSetupRequired: true`.
2. `POST /api/v1/auth/mfa/setup`. Expect an `otpauthUrl`; generate a TOTP code
   from it (e.g., via a test TOTP library, not a real authenticator app).
3. `POST /api/v1/auth/login` with correct credentials. Expect `200` with a
   `mfaChallengeToken`, no access/refresh token yet.
4. `POST /api/v1/auth/mfa/verify` with the TOTP code. Expect `200` with
   `accessToken` + `refreshToken`.
5. Repeat step 3 with a wrong password. Expect `401`, no token issued
   (SC-006).
6. Repeat step 4 with a wrong/expired code. Expect `401`, `retryAllowed:
   true`, no token issued (SC-006).
7. Confirm steps 3–6 each produced an `AuditLogEntry` row (SC-005).
8. Time steps 1–4 end-to-end; expect < 3 minutes (SC-001).

## Scenario 2 — Refresh Rotation (FR-005/FR-006)

1. `POST /api/v1/auth/refresh` with the refresh token from Scenario 1 step 4.
   Expect `200` with a new `refreshToken`; old one is now invalid.
2. Replay the original (already-rotated) refresh token. Expect `403` and an
   audit entry of type `token_reuse_detected`; confirm the entire token
   family (including the token from step 1) is now rejected.

## Scenario 3 — Role-Scoped Access (User Story 2, SC-003)

1. Using the Scenario 1 access token (role: `learner`), call an endpoint
   reserved for `course_provider`. Expect `403`,
   `reason: "insufficient_permission"`.
2. Provision a `platform_supervisor` user and, as `platform_owner`, call
   `PUT /api/v1/rbac/supervisor-overrides/:userId` to grant an extra
   permission. Call `GET /api/v1/rbac/permissions/me` as that supervisor and
   confirm the granted permission is present.
3. As `platform_administrator`, attempt an Owner-only action (e.g., tenant
   provisioning). Expect `403`.

## Scenario 4 — Tenant Isolation (User Story 3, SC-002)

1. Sign in as a `tenant-a` user; call `GET /api/v1/tenants/:tenant-b-id`.
   Expect `403`, `reason: "tenant_mismatch"`, and a `cross_tenant_attempt`
   audit entry.
2. Send any authenticated request with a token whose `tenant_id` claim does
   not match the request's subdomain. Expect `403` before any data access
   (FR-018).
3. Confirm no endpoint used in Scenarios 1–3 ever returned a row belonging to
   `tenant-b` while authenticated as a `tenant-a` user.

## Scenario 5 — Bilingual, Direction-Aware UI (User Story 4, SC-004)

1. In the frontend, set language to Arabic. Load the registration, login,
   MFA, and dashboard screens. Confirm all visible text is Arabic and
   `document.dir === "rtl"`.
2. Switch to English. Confirm all visible text is English and
   `document.dir === "ltr"`.
3. Trigger a permission-denied response (Scenario 3 step 1) in both
   languages; confirm the "You don't have access" message renders localized,
   not a raw `messageKey`.
4. Temporarily remove one key from `ar.json` and reload an affected screen.
   Confirm the English fallback string renders (not a raw key, not a crash)
   and a missing-translation gap is logged server- or client-side (FR-023).

## Expected Outcome

All five scenarios pass without manual intervention beyond seeding the two
test tenants, confirming the Phase 1 validation target from PRD Section 10 is
met.
