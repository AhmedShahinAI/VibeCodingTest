import { NotFoundException } from '@nestjs/common';
import { RbacService } from '../../src/rbac/rbac.service';
import { DEFAULT_PERMISSION_MATRIX, PermissionKey } from '../../src/rbac/permission-matrix';
import { UserRole } from '@elm/shared';

/**
 * Exercises RBAC enforcement for all six roles (spec User Story 2,
 * FR-009 through FR-014) against fakes standing in for Prisma/Postgres, so
 * it runs without a live database. Course-ownership enforcement
 * (FR-012, "instructor cannot access another instructor's course") is
 * re-verified with real course data once Phase 2 (Course Authoring) exists —
 * Phase 1 has no course entity yet, so this suite covers general permission
 * resolution and Supervisor customization only.
 */

const ROLES: UserRole[] = [
  'platform_owner',
  'platform_administrator',
  'platform_supervisor',
  'course_provider',
  'teaching_assistant',
  'learner',
];

function fakePrisma(users: Record<string, { id: string; tenantId: string; role: UserRole }>) {
  return {
    withTenant: async (_tenantId: string, fn: (tx: any) => any) =>
      fn({
        user: {
          findFirst: async ({ where }: any) => {
            const user = users[where.id];
            return user && user.tenantId === where.tenantId ? user : null;
          },
        },
      }),
  };
}

function fakeOverrideRepo(overrides: { userId: string; permissionKey: string; granted: boolean }[] = []) {
  return {
    findForUser: async (_tenantId: string, userId: string) => overrides.filter((o) => o.userId === userId),
    upsert: async () => undefined,
  };
}

describe('User Story 2: Role-Scoped Access — RbacService', () => {
  it.each(ROLES)('resolves exactly the default permission set for %s', async (role) => {
    const users = { 'user-1': { id: 'user-1', tenantId: 'tenant-a', role } };
    const service = new RbacService(fakePrisma(users) as any, fakeOverrideRepo() as any);

    const permissions = await service.resolveEffectivePermissions('user-1', 'tenant-a');
    expect(permissions).toEqual(new Set(DEFAULT_PERMISSION_MATRIX[role]));
  });

  it('reserves ownership-level actions to Platform Owner only (spec FR-013)', async () => {
    const ownerOnlyKeys: PermissionKey[] = ['tenant.provision', 'billing.manage_ownership', 'permission_scheme.define'];
    for (const role of ROLES) {
      const permissions = new Set(DEFAULT_PERMISSION_MATRIX[role]);
      if (role === 'platform_owner') {
        ownerOnlyKeys.forEach((key) => expect(permissions.has(key)).toBe(true));
      } else {
        ownerOnlyKeys.forEach((key) => expect(permissions.has(key)).toBe(false));
      }
    }
  });

  it('layers a granted Supervisor override on top of the role default (spec FR-014)', async () => {
    const users = { sup: { id: 'sup', tenantId: 'tenant-a', role: 'platform_supervisor' as UserRole } };
    const overrides = fakeOverrideRepo([{ userId: 'sup', permissionKey: 'user.manage_all', granted: true }]);
    const service = new RbacService(fakePrisma(users) as any, overrides as any);

    const permissions = await service.resolveEffectivePermissions('sup', 'tenant-a');
    expect(permissions.has('user.manage_all')).toBe(true);
  });

  it('layers a revoked Supervisor override, removing a default permission', async () => {
    const users = { sup: { id: 'sup', tenantId: 'tenant-a', role: 'platform_supervisor' as UserRole } };
    const overrides = fakeOverrideRepo([{ userId: 'sup', permissionKey: 'community.moderate_all', granted: false }]);
    const service = new RbacService(fakePrisma(users) as any, overrides as any);

    const permissions = await service.resolveEffectivePermissions('sup', 'tenant-a');
    expect(permissions.has('community.moderate_all')).toBe(false);
  });

  it('rejects requireSupervisor for a non-Supervisor user', async () => {
    const users = { learner1: { id: 'learner1', tenantId: 'tenant-a', role: 'learner' as UserRole } };
    const service = new RbacService(fakePrisma(users) as any, fakeOverrideRepo() as any);

    await expect(service.requireSupervisor('tenant-a', 'learner1')).rejects.toBeInstanceOf(NotFoundException);
  });
});
