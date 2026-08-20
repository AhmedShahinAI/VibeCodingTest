import { Injectable, UnauthorizedException } from '@nestjs/common';
import { authenticator } from 'otplib';
import { AuditLogService, RefreshTokenStore } from '@elm/shared';
import { UserRepository } from '../users/user.repository';
import { TokenIssuerService } from './token-issuer.service';

export interface MfaVerifyResult {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

/**
 * Completes sign-in (spec FR-003/FR-004/FR-007). Also completes MFA
 * enrollment the first time a user proves possession of their TOTP secret
 * (see MfaSetupService), transitioning them from `pending_verification` to
 * `active`.
 */
@Injectable()
export class MfaVerifyService {
  constructor(
    private readonly users: UserRepository,
    private readonly tokens: TokenIssuerService,
    private readonly refreshTokens: RefreshTokenStore,
    private readonly auditLog: AuditLogService,
  ) {}

  async verify(mfaChallengeToken: string, code: string): Promise<MfaVerifyResult> {
    const { userId, tenantId } = this.tokens.verifyMfaChallengeToken(mfaChallengeToken);
    const user = await this.users.findById(tenantId, userId);

    const codeValid = user?.mfaTotpSecret ? authenticator.check(code, user.mfaTotpSecret) : false;

    if (!user || !codeValid) {
      await this.auditLog.record({
        tenantId,
        userId: user?.id ?? null,
        eventType: 'mfa_failure',
      });
      throw new UnauthorizedException({
        error: 'unauthorized',
        reason: 'invalid_mfa_code',
        retryAllowed: true,
        messageKey: 'errors.invalidMfaCode',
      });
    }

    if (!user.mfaEnrolled) {
      await this.users.completeMfaEnrollment(tenantId, user.id);
    }

    const { token: accessToken, expiresIn } = this.tokens.issueAccessToken(user.id, tenantId, user.role);
    const { token: refreshToken } = await this.refreshTokens.issue(user.id, tenantId);

    await this.auditLog.record({ tenantId, userId: user.id, eventType: 'login_success' });

    return { accessToken, refreshToken, expiresIn };
  }
}
