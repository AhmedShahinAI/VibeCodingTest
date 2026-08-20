import { Body, Controller, Param, Put, Req, UseGuards } from '@nestjs/common';
import { AuthenticatedRequest, JwtAuthGuard, RbacGuard, RequirePermission, TenantContextGuard } from '@elm/shared';
import { SupervisorOverrideDto } from './dto/supervisor-override.dto';
import { RbacService } from './rbac.service';
import { SupervisorOverrideRepository } from './supervisor-override.repository';

/**
 * `PUT /rbac/supervisor-overrides/:userId` — spec FR-014. Restricted to
 * Platform Owner/Administrator via `user.manage_all`, the permission only
 * those two roles hold by default (see permission-matrix.ts) — reuses the
 * same RBAC mechanism rather than a bespoke role check.
 */
@Controller('api/v1/rbac')
@UseGuards(JwtAuthGuard, TenantContextGuard, RbacGuard)
export class SupervisorOverridesController {
  constructor(
    private readonly rbac: RbacService,
    private readonly overrides: SupervisorOverrideRepository,
  ) {}

  @Put('supervisor-overrides/:userId')
  @RequirePermission('user.manage_all')
  async setOverride(
    @Param('userId') targetUserId: string,
    @Body() dto: SupervisorOverrideDto,
    @Req() request: AuthenticatedRequest,
  ) {
    await this.rbac.requireSupervisor(request.tenantId!, targetUserId);
    await this.overrides.upsert(request.tenantId!, targetUserId, dto.permissionKey, dto.granted, request.userId!);
    const permissions = await this.rbac.resolveEffectivePermissions(targetUserId, request.tenantId!);
    return { role: 'platform_supervisor', permissions: [...permissions] };
  }
}
