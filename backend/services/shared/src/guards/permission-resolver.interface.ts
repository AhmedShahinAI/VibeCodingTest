/**
 * Resolves a user's effective permission set (role defaults merged with any
 * Platform Supervisor overrides, per spec FR-014) so `RbacGuard` can enforce
 * it without owning the RBAC data model itself. Concrete implementation
 * lives in `backend/services/tenancy-service/src/rbac/rbac.service.ts`
 * (tasks.md T040) and is re-exported through `@elm/shared` so both services
 * can bind it to this token — RBAC data has one owner (tenancy-service's
 * schema access), but the enforcement guard is shared infrastructure used by
 * every service, per plan.md's shared-guard design.
 */
export interface PermissionResolver {
  resolveEffectivePermissions(userId: string, tenantId: string): Promise<Set<string>>;
}

export const PERMISSION_RESOLVER = Symbol('PERMISSION_RESOLVER');
