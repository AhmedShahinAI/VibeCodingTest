-- Row-Level Security: defense-in-depth for tenant isolation (constitution
-- Principle II). Application code (TenantContextGuard + PrismaService) sets
-- `app.current_tenant` via `SET LOCAL` at the start of every request-scoped
-- transaction; these policies reject any row whose tenant_id disagrees with
-- that setting, even if an application-level query forgets a WHERE clause.
--
-- `current_setting('app.current_tenant', true)` returns NULL (not an error)
-- when unset, so a connection that never set a tenant sees zero rows rather
-- than every tenant's rows.

ALTER TABLE "users" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "users" FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_users ON "users"
  USING ("tenant_id" = current_setting('app.current_tenant', true));

ALTER TABLE "supervisor_permission_overrides" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "supervisor_permission_overrides" FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_supervisor_overrides ON "supervisor_permission_overrides"
  USING ("tenant_id" = current_setting('app.current_tenant', true));

ALTER TABLE "audit_log_entries" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "audit_log_entries" FORCE ROW LEVEL SECURITY;
-- Audit entries allow tenant_id IS NULL (pre-tenant-resolution rejections,
-- e.g. an unresolvable request) to still be written/read by platform-level
-- tooling, in addition to the caller's own tenant's rows.
CREATE POLICY tenant_isolation_audit_log ON "audit_log_entries"
  USING ("tenant_id" = current_setting('app.current_tenant', true) OR "tenant_id" IS NULL);

-- `tenants` itself is intentionally NOT row-level-secured the same way: a
-- request must be able to resolve its own tenant row before app.current_tenant
-- exists. Cross-tenant reads of OTHER tenants' rows are blocked at the
-- application layer in TenancyService (see GET /tenants/:id contract), not by RLS.
