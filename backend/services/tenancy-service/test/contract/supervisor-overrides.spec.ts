import { SupervisorOverridesController } from '../../src/rbac/supervisor-overrides.controller';
import { AuthenticatedRequest } from '@elm/shared';

/**
 * Contract test for `PUT /rbac/supervisor-overrides/:userId`
 * (contracts/tenancy-api.md). Authorization to Owner/Administrator-only
 * is enforced by `@RequirePermission('user.manage_all')` + `RbacGuard`
 * ahead of this handler (see rbac-enforcement.spec.ts for the permission
 * resolution this depends on) — this test covers the handler's own
 * behavior: rejecting a non-Supervisor target and returning the updated
 * effective permission set.
 */
describe('Contract: PUT /rbac/supervisor-overrides/:userId', () => {
  it('rejects a target user who is not a Platform Supervisor', async () => {
    const rbac = {
      requireSupervisor: jest.fn().mockRejectedValue(new Error('not found')),
      resolveEffectivePermissions: jest.fn(),
    };
    const overrides = { upsert: jest.fn() };
    const controller = new SupervisorOverridesController(rbac as any, overrides as any);
    const request = { userId: 'admin1', tenantId: 't1' } as AuthenticatedRequest;

    await expect(
      controller.setOverride('not-a-supervisor', { permissionKey: 'user.manage_all', granted: true }, request),
    ).rejects.toThrow();
    expect(overrides.upsert).not.toHaveBeenCalled();
  });

  it('applies the override and returns the updated effective permission set', async () => {
    const rbac = {
      requireSupervisor: jest.fn().mockResolvedValue(undefined),
      resolveEffectivePermissions: jest.fn().mockResolvedValue(new Set(['course.review_flagged', 'user.manage_all'])),
    };
    const overrides = { upsert: jest.fn().mockResolvedValue(undefined) };
    const controller = new SupervisorOverridesController(rbac as any, overrides as any);
    const request = { userId: 'admin1', tenantId: 't1' } as AuthenticatedRequest;

    const result = await controller.setOverride('sup1', { permissionKey: 'user.manage_all', granted: true }, request);

    expect(overrides.upsert).toHaveBeenCalledWith('t1', 'sup1', 'user.manage_all', true, 'admin1');
    expect(result.permissions).toContain('user.manage_all');
  });
});
