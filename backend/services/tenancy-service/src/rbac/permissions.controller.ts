import { Controller, Get, Req, UseGuards } from '@nestjs/common';
import { AuthenticatedRequest, JwtAuthGuard, TenantContextGuard } from '@elm/shared';
import { RbacService } from './rbac.service';

/** `GET /rbac/permissions/me` — spec FR-010, used by the frontend to render only permitted UI (defense-in-depth, not itself a security boundary). */
@Controller('api/v1/rbac')
@UseGuards(JwtAuthGuard, TenantContextGuard)
export class PermissionsController {
  constructor(private readonly rbac: RbacService) {}

  @Get('permissions/me')
  async me(@Req() request: AuthenticatedRequest) {
    const permissions = await this.rbac.resolveEffectivePermissions(request.userId!, request.tenantId!);
    return { role: request.userRole, permissions: [...permissions] };
  }
}
