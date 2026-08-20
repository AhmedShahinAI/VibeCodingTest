import { Controller, ForbiddenException, Get, Param, Req, UseGuards } from '@nestjs/common';
import { AuthenticatedRequest, AuditLogService, JwtAuthGuard, TenantContextGuard } from '@elm/shared';
import { TenantRepository } from './tenant.repository';

/**
 * `GET /tenants/:id` (spec FR-016/FR-018, contracts/tenancy-api.md).
 * `TenantContextGuard` has already resolved and trusted `request.tenantId`
 * from the caller's own token; this handler additionally enforces that the
 * requested `:id` matches it — the caller's role never overrides this,
 * per spec User Story 3 acceptance scenario 1 ("only Tenant A's data is
 * ever returned").
 */
@Controller('api/v1/tenants')
@UseGuards(JwtAuthGuard, TenantContextGuard)
export class TenantsController {
  constructor(
    private readonly tenants: TenantRepository,
    private readonly auditLog: AuditLogService,
  ) {}

  @Get(':id')
  async findOne(@Param('id') id: string, @Req() request: AuthenticatedRequest) {
    if (id !== request.tenantId) {
      await this.auditLog.record({
        tenantId: request.tenantId!,
        userId: request.userId,
        eventType: 'cross_tenant_attempt',
        detail: { requestedTenantId: id, path: request.path },
      });
      throw new ForbiddenException({
        error: 'forbidden',
        reason: 'tenant_mismatch',
        messageKey: 'errors.forbidden',
      });
    }

    const tenant = await this.tenants.findById(id);
    return tenant;
  }
}
