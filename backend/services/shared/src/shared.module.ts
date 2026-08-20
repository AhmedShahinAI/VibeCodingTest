import { Module } from '@nestjs/common';
import { PassportModule } from '@nestjs/passport';
import { PrismaService } from './prisma.service';
import { AuditLogService } from './audit/audit-log.service';
import { TenantContextGuard } from './guards/tenant-context.guard';
import { SubdomainTenantGuard } from './guards/subdomain-tenant.guard';
import { RefreshTokenStore } from './auth/refresh-token.store';
import { JwtStrategy } from './auth/jwt.strategy';
import { JwtAuthGuard } from './auth/jwt-auth.guard';
import { RedisModule } from './redis.module';

/**
 * One-stop import for every Elm Platform backend service: Prisma access,
 * audit logging, the tenant guard, refresh-token rotation, and JWT
 * verification. Both auth-service and tenancy-service import this so the
 * security-critical plumbing (constitution Principles I/II) is identical
 * across services rather than reimplemented per-service.
 *
 * `RbacGuard` is deliberately NOT provided here. Its `PERMISSION_RESOLVER`
 * dependency is service-specific (e.g. `RbacService` in tenancy-service), and
 * Nest resolves a provider's constructor deps from the module that provides
 * it, not the module that imports it — a shared singleton instance would
 * permanently resolve `PERMISSION_RESOLVER` to whatever (or nothing) was
 * available in *this* module. Each consuming module instead provides
 * `RbacGuard` itself alongside its own `PERMISSION_RESOLVER` binding (see
 * tenancy-service's `rbac.module.ts`).
 */
@Module({
  imports: [PassportModule, RedisModule.forRoot()],
  providers: [PrismaService, AuditLogService, TenantContextGuard, SubdomainTenantGuard, RefreshTokenStore, JwtStrategy, JwtAuthGuard],
  exports: [PrismaService, AuditLogService, TenantContextGuard, SubdomainTenantGuard, RefreshTokenStore, JwtAuthGuard, PassportModule],
})
export class ElmSharedModule {}
