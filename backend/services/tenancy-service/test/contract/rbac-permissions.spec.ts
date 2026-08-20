import { PermissionsController } from '../../src/rbac/permissions.controller';
import { AuthenticatedRequest } from '@elm/shared';

/** Contract test for `GET /rbac/permissions/me` (contracts/tenancy-api.md). */
describe('Contract: GET /rbac/permissions/me', () => {
  it('returns { role, permissions: string[] } for the authenticated caller', async () => {
    const fakeRbac = {
      resolveEffectivePermissions: jest.fn().mockResolvedValue(new Set(['course.enroll', 'community.participate'])),
    };
    const controller = new PermissionsController(fakeRbac as any);
    const request = { userId: 'u1', tenantId: 't1', userRole: 'learner' } as AuthenticatedRequest;

    const result = await controller.me(request);

    expect(result).toEqual({
      role: 'learner',
      permissions: expect.arrayContaining(['course.enroll', 'community.participate']),
    });
    expect(fakeRbac.resolveEffectivePermissions).toHaveBeenCalledWith('u1', 't1');
  });
});
