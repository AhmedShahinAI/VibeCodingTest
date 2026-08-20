import { Injectable } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { ExtractJwt, Strategy } from 'passport-jwt';
import { AccessTokenClaims } from './jwt.types';

/**
 * Verifies access tokens issued by auth-service (RS256, per research.md).
 * Both services register this strategy so a request authenticated against
 * either one carries the same, independently-verifiable claims — no
 * service-to-service call is needed to validate a token.
 */
@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor() {
    const publicKey = process.env.JWT_PUBLIC_KEY;
    if (!publicKey) {
      throw new Error('JWT_PUBLIC_KEY environment variable is required');
    }
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: publicKey.replace(/\\n/g, '\n'),
      algorithms: ['RS256'],
    });
  }

  validate(payload: AccessTokenClaims) {
    return { userId: payload.sub, tenantId: payload.tenantId, role: payload.role };
  }
}
