import { ExecutionContext, Injectable, UnauthorizedException } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { AuthenticatedRequest } from '../guards/tenant-context.guard';

/**
 * Verifies the access token (via `JwtStrategy`) and attaches the resulting
 * claims to `request.auth`, which `TenantContextGuard` then trusts to
 * resolve tenant/user/role. Runs first in the guard pipeline (T053):
 * `JwtAuthGuard -> TenantContextGuard -> RbacGuard`.
 */
@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
  handleRequest<TUser = { userId: string; tenantId: string; role: string }>(
    err: unknown,
    user: TUser | false,
    _info: unknown,
    context: ExecutionContext,
  ): TUser {
    if (err || !user) {
      throw err instanceof Error ? err : new UnauthorizedException();
    }
    const request = context.switchToHttp().getRequest<AuthenticatedRequest>();
    const typedUser = user as unknown as { userId: string; tenantId: string; role: string };
    request.auth = { userId: typedUser.userId, tenantId: typedUser.tenantId, role: typedUser.role };
    return user;
  }
}
