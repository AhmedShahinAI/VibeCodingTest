import { ForbiddenException } from '@nestjs/common';
import { TenantContextGuard, AuthenticatedRequest } from '../../src/guards/tenant-context.guard';

/**
 * Spec User Story 3 acceptance scenario 2: "a request that cannot resolve a
 * tenant context... is rejected" — before any data access, i.e. this guard
 * must throw, not merely proceed with an empty tenant.
 */
function fakeContext(request: Partial<AuthenticatedRequest>) {
  return {
    switchToHttp: () => ({ getRequest: () => request }),
  } as any;
}

describe('User Story 3: TenantContextGuard', () => {
  it('rejects a request with no auth/tenant claim at all', async () => {
    const auditLog = { record: jest.fn() };
    const guard = new TenantContextGuard(auditLog as any);
    const request = { path: '/api/v1/me', headers: {} } as AuthenticatedRequest;

    await expect(guard.canActivate(fakeContext(request))).rejects.toBeInstanceOf(ForbiddenException);
    expect(auditLog.record).toHaveBeenCalledWith(
      expect.objectContaining({ tenantId: null, eventType: 'cross_tenant_attempt' }),
    );
  });

  it('rejects when the X-Tenant-Domain header disagrees with the host subdomain', async () => {
    const auditLog = { record: jest.fn() };
    const guard = new TenantContextGuard(auditLog as any);
    const request = {
      path: '/api/v1/me',
      auth: { tenantId: 'tenant-a', userId: 'u1', role: 'learner' },
      headers: { host: 'tenant-a.elm.example', 'x-tenant-domain': 'tenant-b' },
    } as unknown as AuthenticatedRequest;

    await expect(guard.canActivate(fakeContext(request))).rejects.toBeInstanceOf(ForbiddenException);
  });

  it('resolves tenantId/userId/userRole onto the request when the claim is present and consistent', async () => {
    const auditLog = { record: jest.fn() };
    const guard = new TenantContextGuard(auditLog as any);
    const request = {
      path: '/api/v1/me',
      auth: { tenantId: 'tenant-a', userId: 'u1', role: 'learner' },
      headers: { host: 'tenant-a.elm.example' },
    } as unknown as AuthenticatedRequest;

    const allowed = await guard.canActivate(fakeContext(request));

    expect(allowed).toBe(true);
    expect(request.tenantId).toBe('tenant-a');
    expect(request.userId).toBe('u1');
  });
});
