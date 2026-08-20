import { CanActivate, ExecutionContext, ForbiddenException, Inject, Injectable, Optional } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { AuditLogService } from '../audit/audit-log.service';
import { PERMISSION_KEY } from './require-permission.decorator';
import { PERMISSION_RESOLVER, PermissionResolver } from './permission-resolver.interface';
import { AuthenticatedRequest } from './tenant-context.guard';

/**
 * Enforces the permission a route declares via `@RequirePermission` (spec
 * FR-010/FR-011). Routes without the decorator are allowed through — those
 * are intentionally public-once-authenticated endpoints (e.g. `/me`,
 * `/auth/refresh`); every route that gates a role-scoped action MUST carry
 * the decorator for this guard to do anything.
 *
 * MUST run after `TenantContextGuard` in the guard pipeline: it reads
 * `request.userId`/`request.tenantId`, which `TenantContextGuard` sets.
 */
@Injectable()
export class RbacGuard implements CanActivate {
  constructor(
    private readonly reflector: Reflector,
    private readonly auditLog: AuditLogService,
    @Optional() @Inject(PERMISSION_RESOLVER) private readonly resolver?: PermissionResolver,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const requiredPermission = this.reflector.get<string | undefined>(PERMISSION_KEY, context.getHandler());
    if (!requiredPermission) {
      return true;
    }

    const request = context.switchToHttp().getRequest<AuthenticatedRequest>();
    const { userId, tenantId } = request;

    if (!userId || !tenantId) {
      // TenantContextGuard should have already rejected this; fail closed.
      return false;
    }

    if (!this.resolver) {
      throw new Error(
        'RbacGuard: no PermissionResolver bound. Provide PERMISSION_RESOLVER in this service\'s module.',
      );
    }

    const permissions = await this.resolver.resolveEffectivePermissions(userId, tenantId);
    if (permissions.has(requiredPermission)) {
      return true;
    }

    await this.auditLog.record({
      tenantId,
      userId,
      eventType: 'permission_denied',
      detail: { requiredPermission, path: request.path },
    });

    throw new ForbiddenException({
      error: 'forbidden',
      reason: 'insufficient_permission',
      messageKey: 'errors.forbidden',
    });
  }
}
