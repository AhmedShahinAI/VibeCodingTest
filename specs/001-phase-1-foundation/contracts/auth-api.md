# Contract: Auth API (`auth-service`)

Base path: `/api/v1/auth`. All endpoints require a resolvable tenant context
(subdomain or, where noted, no token yet) per constitution Principle II. All
responses are localized per the caller's `Accept-Language` header or the
authenticated user's `locale`, per FR-022.

## `POST /auth/register`

Registers a new Learner or Course Provider account (FR-001; Assumptions:
staff roles are provisioned, not self-registered).

**Request**:
```json
{ "email": "string", "password": "string", "role": "learner | course_provider", "locale": "ar | en" }
```

**Response 201**:
```json
{ "userId": "uuid", "status": "pending_verification", "mfaSetupRequired": true }
```

**Errors**: `409` — email already registered in this tenant. `422` — invalid
email/password format.

## `POST /auth/register/google`

Registers or signs in via Google OAuth (FR-002). Standard OAuth 2.0
authorization-code exchange; request/response follow the
`passport-google-oauth20` redirect flow and are not repeated here.

## `POST /auth/mfa/setup`

Issues a TOTP secret + provisioning QR payload for a not-yet-MFA-enrolled
user. No access token exists at this point in the flow (MFA is what grants
one), so email+password are re-submitted as proof of identity — equivalent
to the credential check `/auth/login` performs, just without an MFA step
gating it yet.

**Request**:
```json
{ "email": "string", "password": "string" }
```

**Response 200**:
```json
{ "otpauthUrl": "string", "secret": "string" }
```

**Errors**: `401` — invalid credentials.

## `POST /auth/login`

Primary-credential step (FR-003/FR-006).

**Request**:
```json
{ "email": "string", "password": "string" }
```

**Response 200** (credentials valid → MFA required):
```json
{ "mfaChallengeToken": "string" }
```

**Errors**: `401` — invalid credentials. No token of any kind is issued on
this path (FR-006).

## `POST /auth/mfa/verify`

Completes sign-in (FR-003/FR-004/FR-007).

**Request**:
```json
{ "mfaChallengeToken": "string", "code": "string" }
```

**Response 200**:
```json
{ "accessToken": "string", "refreshToken": "string", "expiresIn": 900 }
```

**Errors**: `401` — invalid or expired code; response includes
`retryAllowed: true`. No token issued (FR-007).

## `POST /auth/refresh`

Rotates a refresh token (FR-005).

**Request**:
```json
{ "refreshToken": "string" }
```

**Response 200**:
```json
{ "accessToken": "string", "refreshToken": "string", "expiresIn": 900 }
```

**Errors**: `401` — token invalid/expired. `403` — reuse of an already-rotated
token detected; the entire token family is revoked server-side and the event
is audit-logged (`token_reuse_detected`).

## `POST /auth/logout`

Revokes the current refresh-token family. Idempotent — an already-invalid
token still returns `204` rather than an error, since the end state (no
valid session) is the same either way.

**Request**:
```json
{ "refreshToken": "string" }
```

**Response**: `204`.

## `GET /me`

Returns the authenticated user's profile, role, tenant, and locale — used by
the frontend to render the role-scoped, localized dashboard shell.

**Response 200**:
```json
{ "userId": "uuid", "tenantId": "uuid", "role": "string", "locale": "ar | en" }
```

**Errors**: `401` — missing/invalid access token. `403` — resolved tenant
does not match token's tenant claim (cross-tenant attempt; logged per
FR-018).

## `PUT /me/locale`

Persists the caller's language preference (FR-019).

**Request**:
```json
{ "locale": "ar | en" }
```

**Response 200**:
```json
{ "locale": "ar | en" }
```
