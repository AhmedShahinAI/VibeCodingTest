import { Injectable, UnauthorizedException } from '@nestjs/common';
import * as bcrypt from 'bcrypt';
import { AuditLogService } from '@elm/shared';
import { UserRepository } from '../users/user.repository';
import { TokenIssuerService } from './token-issuer.service';

export interface LoginResult {
  mfaChallengeToken: string;
}

/**
 * Primary-credential step of sign-in (spec FR-003/FR-006). Never issues an
 * access/refresh token itself — success only advances the user to the MFA
 * challenge, per acceptance scenario US1-2/3 in spec.md.
 */
@Injectable()
export class LoginService {
  constructor(
    private readonly users: UserRepository,
    private readonly tokens: TokenIssuerService,
    private readonly auditLog: AuditLogService,
  ) {}

  async login(tenantId: string, email: string, password: string): Promise<LoginResult> {
    const user = await this.users.findByEmailInTenant(tenantId, email);
    const passwordValid = user?.passwordHash ? await bcrypt.compare(password, user.passwordHash) : false;

    // 'pending_verification' is allowed through deliberately: a brand-new
    // user is still pending until their FIRST successful MFA verification
    // completes enrollment (see MfaVerifyService), and that verification can
    // only happen after this login step. Only 'disabled' blocks sign-in.
    if (!user || !passwordValid || user.status === 'disabled') {
      await this.auditLog.record({
        tenantId,
        userId: user?.id ?? null,
        eventType: 'login_failure',
        detail: { email },
      });
      throw new UnauthorizedException({
        error: 'unauthorized',
        reason: 'invalid_credentials',
        messageKey: 'errors.invalidCredentials',
      });
    }

    const mfaChallengeToken = this.tokens.issueMfaChallengeToken(user.id, tenantId);
    return { mfaChallengeToken };
  }
}
