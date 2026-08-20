# Contract: Tenancy & RBAC API (`tenancy-service`)

Base path: `/api/v1`. Every endpoint runs behind the shared
`TenantContextGuard` (tenant resolved before any handler executes, FR-015) and
the shared `RbacGuard` (permission-checked per FR-010).

## `GET /tenants/:id`

Returns tenant metadata. Only resolvable for the caller's own resolved tenant
(FR-016); requesting any other `:id` returns `403` and logs a
`cross_tenant_attempt` (FR-018), regardless of the caller's role.

**Response 200**:
```json
{ "id": "uuid", "name": "string", "domain": "string", "status": "active | suspended" }
```

## `GET /rbac/permissions/me`

Returns the resolved effective permission set for the authenticated user —
their role's defaults merged with any `SupervisorPermissionOverride` rows
(FR-014). Used by the frontend to render only the actions a user is permitted
to see (defense-in-depth alongside server-side enforcement; the UI check is
not itself a security boundary).

**Response 200**:
```json
{ "role": "string", "permissions": ["course.view", "community.moderate", "..."] }
```

## `PUT /rbac/supervisor-overrides/:userId`

Platform Owner/Administrator only (FR-014). Sets or clears a permission
override for a Platform Supervisor.

**Request**:
```json
{ "permissionKey": "string", "granted": true }
```

**Response 200**: the updated effective permission set for `:userId` (same
shape as `GET /rbac/permissions/me`).

**Errors**: `403` — caller is not Owner/Administrator, or `:userId` does not
resolve to a `platform_supervisor` user in the caller's tenant.

## Cross-Cutting Contract: Denial Response Shape

Every `403` from `RbacGuard` (FR-011) and every tenant-mismatch `403` from
`TenantContextGuard` (FR-018) share one envelope so the frontend can render a
single localized "You don't have access" pattern (PRD edge case):

```json
{ "error": "forbidden", "reason": "insufficient_permission | tenant_mismatch", "messageKey": "errors.forbidden" }
```

`messageKey` is resolved client-side through the i18n resource bundle
(FR-020/FR-022), never a hardcoded string from the API.
