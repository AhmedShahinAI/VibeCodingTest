import { RefreshTokenReuseError, RefreshTokenStore } from '@elm/shared';

/**
 * Contract test for refresh-token rotation and reuse detection
 * (contracts/auth-api.md `POST /auth/refresh`, spec FR-005/FR-006), against
 * an in-memory fake Redis client implementing just the commands
 * RefreshTokenStore uses.
 */
class FakeRedis {
  private store = new Map<string, string>();
  private sets = new Map<string, Set<string>>();

  async get(key: string) {
    return this.store.get(key) ?? null;
  }

  async set(key: string, value: string) {
    this.store.set(key, value);
    return 'OK';
  }

  async del(...keys: string[]) {
    keys.forEach((k) => this.store.delete(k));
    return keys.length;
  }

  async sadd(key: string, member: string) {
    if (!this.sets.has(key)) this.sets.set(key, new Set());
    this.sets.get(key)!.add(member);
    return 1;
  }

  async smembers(key: string) {
    return [...(this.sets.get(key) ?? [])];
  }

  async expire() {
    return 1;
  }
}

describe('Contract: POST /auth/refresh (rotation + reuse detection)', () => {
  it('rotates a refresh token and invalidates the previous one', async () => {
    const store = new RefreshTokenStore(new FakeRedis() as any);
    const issued = await store.issue('user-1', 'tenant-a');

    const rotated = await store.rotate(issued.token);
    expect(rotated.token).not.toBe(issued.token);
    expect(rotated.userId).toBe('user-1');
    expect(rotated.tenantId).toBe('tenant-a');
  });

  it('detects reuse of an already-rotated token and revokes the whole family', async () => {
    const store = new RefreshTokenStore(new FakeRedis() as any);
    const issued = await store.issue('user-1', 'tenant-a');
    const rotated = await store.rotate(issued.token);

    // Replaying the original (now-rotated) token must be treated as reuse.
    await expect(store.rotate(issued.token)).rejects.toBeInstanceOf(RefreshTokenReuseError);

    // The whole family — including the token issued by the rotation above —
    // must now be revoked as a result of the reuse.
    await expect(store.rotate(rotated.token)).rejects.toThrow();
  });
});
