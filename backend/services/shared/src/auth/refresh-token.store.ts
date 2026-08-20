import { Inject, Injectable } from '@nestjs/common';
import { randomUUID, createHash } from 'crypto';
import type Redis from 'ioredis';

export const REDIS_CLIENT = Symbol('REDIS_CLIENT');

const REFRESH_TOKEN_TTL_SECONDS = 30 * 24 * 60 * 60; // 30 days, per research.md
const familyKey = (familyId: string) => `refresh:family:${familyId}`;
const tokenKey = (tokenHash: string) => `refresh:token:${tokenHash}`;

interface TokenRecord {
  familyId: string;
  current: boolean;
  userId: string;
  tenantId: string;
}

export interface IssuedRefreshToken {
  token: string;
  familyId: string;
  userId: string;
  tenantId: string;
}

export class RefreshTokenReuseError extends Error {
  constructor(readonly familyId: string, readonly userId: string, readonly tenantId: string) {
    super('Refresh token reuse detected; token family revoked');
  }
}

/**
 * Redis-backed refresh-token rotation with reuse detection (research.md
 * "Token Lifetimes & Rotation"; spec FR-005/FR-006). Only a hash of the
 * token is ever stored. `userId`/`tenantId` are stored alongside each token
 * record so `rotate()` does not depend on the caller already holding a
 * valid access token — refreshing is exactly the case where the access
 * token has expired, so the identity must come from the refresh token
 * record itself. Rotating a token invalidates the previous one; replaying
 * an already-rotated token revokes the entire family and raises
 * `RefreshTokenReuseError` so the caller can log a `token_reuse_detected`
 * audit event.
 */
@Injectable()
export class RefreshTokenStore {
  constructor(@Inject(REDIS_CLIENT) private readonly redis: Redis) {}

  private hash(token: string): string {
    return createHash('sha256').update(token).digest('hex');
  }

  /** Issues the first refresh token of a new login, starting a new family. */
  async issue(userId: string, tenantId: string): Promise<IssuedRefreshToken> {
    const familyId = randomUUID();
    return this.mint(familyId, userId, tenantId);
  }

  /**
   * Rotates a refresh token. Throws `RefreshTokenReuseError` if `token` has
   * already been rotated (i.e. is no longer the current token of its
   * family) — this is the reuse-detection path.
   */
  async rotate(token: string): Promise<IssuedRefreshToken> {
    const hash = this.hash(token);
    const raw = await this.redis.get(tokenKey(hash));
    if (!raw) {
      throw new Error('Refresh token invalid or expired');
    }
    const record = JSON.parse(raw) as TokenRecord;

    if (!record.current) {
      await this.revokeFamily(record.familyId);
      throw new RefreshTokenReuseError(record.familyId, record.userId, record.tenantId);
    }

    // Mark this token as rotated-out but keep a short trailing record so a
    // near-simultaneous replay is still detected as reuse rather than "not found".
    await this.redis.set(
      tokenKey(hash),
      JSON.stringify({ ...record, current: false } satisfies TokenRecord),
      'EX',
      REFRESH_TOKEN_TTL_SECONDS,
    );

    return this.mint(record.familyId, record.userId, record.tenantId);
  }

  async revokeFamily(familyId: string): Promise<void> {
    const members = await this.redis.smembers(familyKey(familyId));
    if (members.length > 0) {
      await this.redis.del(...members.map((hash) => tokenKey(hash)));
    }
    await this.redis.del(familyKey(familyId));
  }

  private async mint(familyId: string, userId: string, tenantId: string): Promise<IssuedRefreshToken> {
    const token = randomUUID() + randomUUID();
    const hash = this.hash(token);

    await this.redis.set(
      tokenKey(hash),
      JSON.stringify({ familyId, current: true, userId, tenantId } satisfies TokenRecord),
      'EX',
      REFRESH_TOKEN_TTL_SECONDS,
    );
    await this.redis.sadd(familyKey(familyId), hash);
    await this.redis.expire(familyKey(familyId), REFRESH_TOKEN_TTL_SECONDS);

    return { token, familyId, userId, tenantId };
  }
}
