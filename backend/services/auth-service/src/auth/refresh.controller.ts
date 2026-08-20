import { Body, Controller, HttpCode, Post } from '@nestjs/common';
import { AuditLogService, RefreshTokenReuseError, RefreshTokenStore } from '@elm/shared';
import { UnauthorizedException, ForbiddenException } from '@nestjs/common';
import { RefreshDto } from './dto/auth.dto';
import { UserRepository } from '../users/user.repository';
import { TokenIssuerService } from './token-issuer.service';

/**
 * `POST /auth/refresh` (spec FR-005/FR-006). Deliberately outside
 * `SubdomainTenantGuard`/`JwtAuthGuard` — the access token that would carry
 * tenant/user claims may well be expired (that is exactly why the client is
 * refreshing), so identity comes from the refresh token record itself.
 */
@Controller('api/v1/auth')
export class RefreshController {
  constructor(
    private readonly refreshTokens: RefreshTokenStore,
    private readonly users: UserRepository,
    private readonly tokens: TokenIssuerService,
    private readonly auditLog: AuditLogService,
  ) {}

  @Post('refresh')
  @HttpCode(200)
  async refresh(@Body() dto: RefreshDto) {
    try {
      const rotated = await this.refreshTokens.rotate(dto.refreshToken);
      const user = await this.users.findById(rotated.tenantId, rotated.userId);
      if (!user) {
        throw new UnauthorizedException();
      }
      const { token: accessToken, expiresIn } = this.tokens.issueAccessToken(user.id, user.tenantId, user.role);
      return { accessToken, refreshToken: rotated.token, expiresIn };
    } catch (err) {
      if (err instanceof RefreshTokenReuseError) {
        await this.auditLog.record({
          tenantId: err.tenantId,
          userId: err.userId,
          eventType: 'token_reuse_detected',
          detail: { familyId: err.familyId },
        });
        throw new ForbiddenException({
          error: 'forbidden',
          reason: 'refresh_token_reused',
          messageKey: 'errors.sessionRevoked',
        });
      }
      throw new UnauthorizedException({
        error: 'unauthorized',
        reason: 'invalid_refresh_token',
        messageKey: 'errors.sessionExpired',
      });
    }
  }
}
