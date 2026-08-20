import { CanActivate, ExecutionContext, Injectable, UnauthorizedException } from '@nestjs/common';
import { PrismaService } from '../prisma.service';
import { AuditLogService } from '../audit/audit-log.service';
import { AuthenticatedRequest } from './tenant-context.guard';

const SUBDOMAIN_PATTERN = /^([a-z0-9-]+)\./i;

/**
 * Resolves tenant context for PRE-AUTHENTICATION endpoints (register, login,
 * mfa/verify, refresh) where no access token exists yet to carry a
 * `tenantId` claim (spec FR-015 still applies — registration/login are
 * tenant-scoped, per data-model.md `User.tenantId`). Resolves purely from
 * the request's host/subdomain (or `X-Tenant-Domain` header, used in local
 * development where `Host` is `localhost`) against the `tenants` table,
 * which is not itself row-level-secured (see prisma RLS migration notes).
 *
 * Once a session exists, `TenantContextGuard` (trusting the JWT claim) is
 * used instead — this guard is only for the handful of pre-auth routes.
 */
@Injectable()
export class SubdomainTenantGuard implements CanActivate {
  constructor(
    private readonly prisma: PrismaService,
    private readonly auditLog: AuditLogService,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest<AuthenticatedRequest>();
    const explicitDomain = request.headers['x-tenant-domain'] as string | undefined;
    const hostHeader = request.headers.host ?? '';
    const domain = explicitDomain ?? SUBDOMAIN_PATTERN.exec(hostHeader)?.[1];

    if (!domain) {
      await this.auditLog.record({
        tenantId: null,
        eventType: 'cross_tenant_attempt',
        detail: { reason: 'unresolvable_tenant_domain', path: request.path },
      });
      throw new UnauthorizedException();
    }

    const tenant = await this.prisma.tenant.findUnique({ where: { domain } });
    if (!tenant || tenant.status !== 'active') {
      await this.auditLog.record({
        tenantId: null,
        eventType: 'cross_tenant_attempt',
        detail: { reason: 'unknown_or_inactive_tenant', domain, path: request.path },
      });
      throw new UnauthorizedException();
    }

    request.tenantId = tenant.id;
    return true;
  }
}
