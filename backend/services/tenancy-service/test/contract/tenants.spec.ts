import { ForbiddenException } from '@nestjs/common';
import { TenantsController } from '../../src/tenants/tenants.controller';
import { AuthenticatedRequest } from '@elm/shared';

/** Contract test for `GET /tenants/:id` (contracts/tenancy-api.md, spec FR-016/FR-018). */
describe('Contract: GET /tenants/:id', () => {
  it('returns the tenant when :id matches the caller\'s own resolved tenant', async () => {
    const tenants = { findById: jest.fn().mockResolvedValue({ id: 'tenant-a', name: 'Tenant A' }) };
    const auditLog = { record: jest.fn() };
    const controller = new TenantsController(tenants as any, auditLog as any);
    const request = { tenantId: 'tenant-a', userId: 'u1', path: '/api/v1/tenants/tenant-a' } as AuthenticatedRequest;

    const result = await controller.findOne('tenant-a', request);

    expect(result).toEqual({ id: 'tenant-a', name: 'Tenant A' });
    expect(auditLog.record).not.toHaveBeenCalled();
  });

  it('denies and audits a request for a different tenant\'s :id, regardless of the caller\'s role', async () => {
    const tenants = { findById: jest.fn() };
    const auditLog = { record: jest.fn() };
    const controller = new TenantsController(tenants as any, auditLog as any);
    const request = { tenantId: 'tenant-a', userId: 'u1', path: '/api/v1/tenants/tenant-b' } as AuthenticatedRequest;

    await expect(controller.findOne('tenant-b', request)).rejects.toBeInstanceOf(ForbiddenException);
    expect(tenants.findById).not.toHaveBeenCalled();
    expect(auditLog.record).toHaveBeenCalledWith(
      expect.objectContaining({ tenantId: 'tenant-a', eventType: 'cross_tenant_attempt' }),
    );
  });
});
