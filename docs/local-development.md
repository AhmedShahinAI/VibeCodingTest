# Local Development — Phase 1 (Foundation)

Covers running `auth-service`, `tenancy-service`, and the frontend locally
against Postgres + Redis. See [specs/001-phase-1-foundation/quickstart.md](../specs/001-phase-1-foundation/quickstart.md)
for the validation scenarios this setup is meant to support.

## Prerequisites

- Node.js 20+, npm 10+
- Docker (for Postgres 15 + Redis 7 via `docker-compose.yml`)

## 1. Install dependencies

```sh
npm install
```

This is an npm-workspaces monorepo (`backend/services/shared`,
`backend/services/auth-service`, `backend/services/tenancy-service`,
`frontend`) — one install at the repo root covers all four packages.

## 2. Start Postgres + Redis

```sh
docker compose up -d
```

## 3. Configure environment variables

Copy each service's `.env.example` to `.env` and fill in the blanks:

```sh
cp backend/services/auth-service/.env.example backend/services/auth-service/.env
cp backend/services/tenancy-service/.env.example backend/services/tenancy-service/.env
```

Generate the RS256 key pair used to sign/verify access tokens (`auth-service`
signs, `tenancy-service` only verifies — same public key in both `.env`
files):

```sh
openssl genrsa -out /tmp/jwt-private.pem 2048
openssl rsa -in /tmp/jwt-private.pem -pubout -out /tmp/jwt-public.pem
```

Paste the PEM contents into `JWT_PRIVATE_KEY` (auth-service only) and
`JWT_PUBLIC_KEY` (both services) with literal `\n` for newlines, and set
`MFA_CHALLENGE_SECRET` to `openssl rand -hex 32` (auth-service only).

## 4. Run migrations and seed two test tenants

```sh
npm run --workspace=@elm/shared prisma:generate
npm run --workspace=@elm/shared prisma:migrate
npm run --workspace=@elm/shared prisma:seed
```

The seed creates `tenant-a` and `tenant-b` (see
[backend/services/shared/prisma/seed.ts](../backend/services/shared/prisma/seed.ts)),
used by the tenant-isolation scenarios in quickstart.md.

## 5. Run the services

```sh
npm run --workspace=@elm/auth-service start:dev      # port 3001
npm run --workspace=@elm/tenancy-service start:dev   # port 3002
npm run --workspace=elm-frontend dev                 # port 5173
```

The frontend's Vite dev server proxies `/api/v1/auth` and `/api/v1/me` to
`auth-service`, and `/api/v1/rbac`/`/api/v1/tenants` to `tenancy-service`
(see [frontend/vite.config.ts](../frontend/vite.config.ts)). Requests need a
resolvable tenant subdomain; for local development, send an
`X-Tenant-Domain: tenant-a` header (the pre-auth `SubdomainTenantGuard`
accepts this as an alternative to a real subdomain — see
`backend/services/shared/src/guards/subdomain-tenant.guard.ts`).

## 6. Run tests

```sh
npm run test --workspaces --if-present   # Jest (backend) + Vitest (frontend)
npm run --workspace=elm-frontend test:e2e  # Playwright — needs the dev server running
```

## Known gaps (tracked, not silent)

- Full end-to-end validation against a live Postgres/Redis (RLS enforcement,
  refresh-token rotation via real Redis, the complete quickstart.md flow) has
  not been run in the environment this Phase 1 build was produced in —only
  unit/contract-level tests with in-memory fakes have been executed. Run
  quickstart.md's five scenarios against a real local stack before
  considering Phase 1 done end-to-end.
- Load testing (API p95 < 500ms, constitution Principle VII) requires a
  running deployment and has not been performed yet.
