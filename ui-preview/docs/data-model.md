# Phase 1 Data Model: Foundation

All tables below are tenant-scoped (`tenant_id` foreign key + Postgres RLS
policy `tenant_id = current_setting('app.current_tenant')`) except `Tenant`
itself. This directly implements spec Key Entities and constitution Principle
II.

## Tenant

| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| name | text | |
| domain | text, unique | subdomain used for tenant resolution |
| status | enum(`active`, `suspended`) | non-`active` tenants reject all requests |
| created_at | timestamptz | |

## User

| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | UUID (FK → Tenant) | RLS-enforced |
| email | text | unique per `tenant_id` (FR: duplicate registration within a tenant is rejected) |
| password_hash | text, nullable | null if account is social-sign-in-only |
| google_subject_id | text, nullable, unique | set when registered/linked via Google OAuth |
| role | enum(`platform_owner`, `platform_administrator`, `platform_supervisor`, `course_provider`, `teaching_assistant`, `learner`) | exactly one role per user (FR-009) |
| mfa_enrolled | boolean, default `false` | |
| mfa_totp_secret | text, encrypted at rest, nullable | set once MFA setup completes |
| locale | enum(`ar`, `en`), default `en` | persisted language preference (FR-019) |
| status | enum(`pending_verification`, `active`, `disabled`) | |
| created_at | timestamptz | |

**Validation rules**:
- `email` required, valid format, unique within `tenant_id`.
- `role` required at creation for staff-provisioned accounts; learner/
  instructor self-registration defaults to `learner`/`course_provider`
  respectively per spec Assumptions.
- A user with `status != active` cannot complete sign-in past MFA.

**State transitions** (`status`): `pending_verification → active` on
email/account verification; `active → disabled` on administrative action
(out of scope to trigger in Phase 1, but the field exists so RBAC/session
checks can honor it).

## SupervisorPermissionOverride

| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | UUID (FK → Tenant) | |
| user_id | UUID (FK → User) | must reference a `platform_supervisor` user |
| permission_key | text | e.g. `community.moderate` |
| granted | boolean | `true` adds a permission beyond the Supervisor default; `false` revokes a default permission |
| set_by_user_id | UUID (FK → User) | must be `platform_owner` or `platform_administrator` |
| updated_at | timestamptz | |

Implements FR-014. The `RbacGuard` merges the role's default permission set
with any override rows for that user before evaluating a request.

## RefreshToken

| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | also serves as the token family id root, or `family_id` below tracks it |
| family_id | UUID | shared across all tokens produced by rotating the same original login |
| user_id | UUID (FK → User) | |
| tenant_id | UUID (FK → Tenant) | |
| token_hash | text | store only a hash, never the raw token |
| issued_at | timestamptz | |
| expires_at | timestamptz | issued_at + 30 days |
| rotated_at | timestamptz, nullable | set the moment it is exchanged for a new token |
| revoked | boolean, default `false` | set `true` for the whole family on reuse-after-rotation detection |

Stored in Redis (not Postgres) keyed by `family_id`/token hash for low-latency
validation on every refresh; TTL matches `expires_at`. Implements FR-005/FR-006
and the reuse-detection decision in research.md.

## AuditLogEntry

| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | UUID (FK → Tenant), nullable | null only for pre-tenant-resolution rejected requests |
| user_id | UUID (FK → User), nullable | null for failed sign-in attempts with an unrecognized email |
| event_type | enum(`login_success`, `login_failure`, `mfa_failure`, `permission_denied`, `cross_tenant_attempt`, `token_reuse_detected`) | |
| detail | jsonb | event-specific context (e.g., requested permission key, denied route) |
| occurred_at | timestamptz | |

Append-only table (`INSERT`-only application role; no `UPDATE`/`DELETE`
grants), directly implementing FR-008/FR-011/FR-018 and spec SC-005.

## LocalizationPreference

Modeled as the `User.locale` field above rather than a separate table — it is
a single-valued attribute of the user with no independent lifecycle,
so a dedicated entity would add indirection without benefit.

## Relationships Summary

```text
Tenant 1───* User
Tenant 1───* AuditLogEntry
User   1───* SupervisorPermissionOverride  (as the overridden user)
User   1───* SupervisorPermissionOverride  (as set_by_user_id, self-referential)
User   1───* RefreshToken (in Redis, logically FK'd to User.id)
User   1───* AuditLogEntry
```
