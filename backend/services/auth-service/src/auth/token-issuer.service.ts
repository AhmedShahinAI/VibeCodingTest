import { Injectable, UnauthorizedException } from '@nestjs/common';
import jwt from 'jsonwebtoken';

const ACCESS_TOKEN_TTL_SECONDS = 15 * 60; // research.md: 15-minute access token
const MFA_CHALLENGE_TTL_SECONDS = 5 * 60;

export interface MfaChallengeClaims {
  sub: string; // userId
  tenantId: string;
  purpose: 'mfa_challenge';
}

/**
 * Signs access tokens (RS256, verified by `@elm/shared`'s JwtStrategy in
 * both services) and short-lived MFA challenge tokens (HS256, verified only
 * by this service between `/auth/login` and `/auth/mfa/verify`).
 */
@Injectable()
export class TokenIssuerService {
  private readonly privateKey: string;
  private readonly mfaChallengeSecret: string;

  constructor() {
    const privateKey = process.env.JWT_PRIVATE_KEY;
    const mfaChallengeSecret = process.env.MFA_CHALLENGE_SECRET;
    if (!privateKey || !mfaChallengeSecret) {
      throw new Error('JWT_PRIVATE_KEY and MFA_CHALLENGE_SECRET environment variables are required');
    }
    this.privateKey = privateKey.replace(/\\n/g, '\n');
    this.mfaChallengeSecret = mfaChallengeSecret;
  }

  issueAccessToken(userId: string, tenantId: string, role: string): { token: string; expiresIn: number } {
    const token = jwt.sign({ tenantId, role }, this.privateKey, {
      subject: userId,
      algorithm: 'RS256',
      expiresIn: ACCESS_TOKEN_TTL_SECONDS,
    });
    return { token, expiresIn: ACCESS_TOKEN_TTL_SECONDS };
  }

  issueMfaChallengeToken(userId: string, tenantId: string): string {
    return jwt.sign({ tenantId, purpose: 'mfa_challenge' } satisfies Omit<MfaChallengeClaims, 'sub'>, this.mfaChallengeSecret, {
      subject: userId,
      algorithm: 'HS256',
      expiresIn: MFA_CHALLENGE_TTL_SECONDS,
    });
  }

  verifyMfaChallengeToken(token: string): { userId: string; tenantId: string } {
    try {
      const payload = jwt.verify(token, this.mfaChallengeSecret) as jwt.JwtPayload & MfaChallengeClaims;
      if (payload.purpose !== 'mfa_challenge' || !payload.sub) {
        throw new Error('invalid purpose');
      }
      return { userId: payload.sub, tenantId: payload.tenantId };
    } catch {
      throw new UnauthorizedException({
        error: 'unauthorized',
        reason: 'invalid_mfa_challenge_token',
        messageKey: 'errors.mfaChallengeExpired',
      });
    }
  }
}
