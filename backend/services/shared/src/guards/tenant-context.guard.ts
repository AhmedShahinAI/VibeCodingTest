import { CanActivate, ExecutionContext, ForbiddenException, Injectable } from '@nestjs/common';
import { Request } from 'express';
import { AuditLogService } from '../audit/audit-log.service';

export interface AuthenticatedRequest extends Request {
  tenantId?: string;
  userId?: string;
  userRole?: string;
  /** Present once `passport-jwt` (wired per-service) validates the access token. */
  auth?: { tenantId: string; userId: string; role: string };
}

const SUBDOMAIN_PATTERN = /^([a-z0-9-]+)\./i;

/**
 * Resolves the tenant for every request BEFORE any handler runs (spec
 * FR-015). Trusts only the authenticated token's `tenantId` claim; the
 * subdomain is cross-checked as a second signal and any disagreement is
 * treated as a tenant-mismatch, not silently resolved in the token's favor.
 *
 * Must run globally (APP_GUARD) ahead of RbacGuard in both services' guard
 * pipeline (tasks.md T053) so a request can never reach controller logic
 * without a trusted, resolved tenant on `request.tenantId`.
 */
@Injectable()
export class TenantContextGuard implements CanActivate {
  constructor(private readonly auditLog: AuditLogService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest<AuthenticatedRequest>();

    if (!request.auth?.tenantId) {
      await this.auditLog.record({
        tenantId: null,
        eventType: 'cross_tenant_attempt',
        detail: { reason: 'missing_tenant_context', path: request.path },
      });
      throw new ForbiddenException({
        error: 'forbidden',
        reason: 'tenant_mismatch',
        messageKey: 'errors.forbidden',
      });
    }

    const hostHeader = request.headers.host ?? '';
    const subdomainMatch = SUBDOMAIN_PATTERN.exec(hostHeader);
    const claimedSubdomain = subdomainMatch?.[1];

    if (claimedSubdomain && request.headers['x-tenant-domain'] && request.headers['x-tenant-domain'] !== claimedSubdomain) {
      await this.auditLog.record({
        tenantId: request.auth.tenantId,
        userId: request.auth.userId,
        eventType: 'cross_tenant_attempt',
        detail: { reason: 'subdomain_token_mismatch', path: request.path },
      });
      throw new ForbiddenException({
        error: 'forbidden',
        reason: 'tenant_mismatch',
        messageKey: 'errors.forbidden',
      });
    }

    request.tenantId = request.auth.tenantId;
    request.userId = request.auth.userId;
    request.userRole = request.auth.role;
    return true;
  }
}
