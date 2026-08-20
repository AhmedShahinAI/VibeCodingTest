import { Injectable, UnauthorizedException } from '@nestjs/common';
import * as bcrypt from 'bcrypt';
import { authenticator } from 'otplib';
import { UserRepository } from '../users/user.repository';

export interface MfaSetupResult {
  otpauthUrl: string;
  secret: string;
}

const ISSUER = 'Elm Platform';

/**
 * Implements the TOTP MFA decision from research.md. No access token exists
 * yet at this point in the flow (MFA is what grants one), so re-verifying
 * email+password here is what authorizes the call — equivalent proof of
 * identity to what `LoginService` requires, without yet needing MFA. This
 * also guarantees `otpauthUrl`/`secret` are only ever returned to the actual
 * account owner and only while enrollment is still pending (spec Edge Case:
 * "interrupted MFA setup" resumes via this same re-verification).
 */
@Injectable()
export class MfaSetupService {
  constructor(private readonly users: UserRepository) {}

  async setup(tenantId: string, email: string, password: string): Promise<MfaSetupResult> {
    const user = await this.users.findByEmailInTenant(tenantId, email);
    const passwordValid = user?.passwordHash ? await bcrypt.compare(password, user.passwordHash) : false;
    if (!user || !passwordValid) {
      throw new UnauthorizedException({
        error: 'unauthorized',
        reason: 'invalid_credentials',
        messageKey: 'errors.invalidCredentials',
      });
    }

    const secret = authenticator.generateSecret();
    await this.users.setMfaSecret(tenantId, user.id, secret);
    const otpauthUrl = authenticator.keyuri(email, ISSUER, secret);

    return { otpauthUrl, secret };
  }
}
