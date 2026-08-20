import { RbacService } from '../../src/rbac/rbac.service';
import { UserRole } from '@elm/shared';

/**
 * Two-tenant isolation test (spec User Story 3, SC-002: "100% of
 * cross-tenant access attempts... denied — zero tenant-boundary
 * breaches"). Exercises the application-level half of the defense-in-depth
 * model (RLS is the database-level half, verified against a live Postgres
 * per quickstart.md) by confirming every lookup is scoped by BOTH userId
 * and tenantId together — a user from Tenant A can never be resolved while
 * a Tenant B context is active, even if the userId happens to be known.
 */
function fakePrismaWithTwoTenants() {
  const users: Record<string, { id: string; tenantId: string; role: UserRole }> = {
    'user-a': { id: 'user-a', tenantId: 'tenant-a', role: 'learner' },
    'user-b': { id: 'user-b', tenantId: 'tenant-b', role: 'learner' },
  };
  return {
    withTenant: async (tenantId: string, fn: (tx: any) => any) =>
      fn({
        user: {
          findFirst: async ({ where }: any) => {
            const user = users[where.id];
            // Mirrors what the Postgres RLS policy also enforces: a row is
            // only visible when its tenant_id matches the active tenant.
            return user && user.tenantId === tenantId && user.tenantId === where.tenantId ? user : null;
          },
        },
      }),
  };
}

const noopOverrides = { findForUser: async () => [], upsert: async () => undefined };

describe('User Story 3: Tenant-Isolated Access', () => {
  it('never resolves a Tenant B user while scoped to Tenant A, even with a valid Tenant B userId', async () => {
    const service = new RbacService(fakePrismaWithTwoTenants() as any, noopOverrides as any);

    await expect(service.resolveEffectivePermissions('user-b', 'tenant-a')).rejects.toThrow();
  });

  it('resolves each tenant\'s own user only within its own tenant context', async () => {
    const service = new RbacService(fakePrismaWithTwoTenants() as any, noopOverrides as any);

    const permsA = await service.resolveEffectivePermissions('user-a', 'tenant-a');
    const permsB = await service.resolveEffectivePermissions('user-b', 'tenant-b');

    expect(permsA).toBeInstanceOf(Set);
    expect(permsB).toBeInstanceOf(Set);
  });
});
