import { UnauthorizedException } from '@nestjs/common';
import { authenticator } from 'otplib';
import { LoginService } from '../../src/auth/login.service';
import { MfaVerifyService } from '../../src/auth/mfa-verify.service';
import { TokenIssuerService } from '../../src/auth/token-issuer.service';
import { RegisterService } from '../../src/auth/register.service';
import { MfaSetupService } from '../../src/auth/mfa-setup.service';
import { UserRepository } from '../../src/users/user.repository';

/**
 * Contract tests for `POST /auth/login` and `POST /auth/mfa/verify`
 * (contracts/auth-api.md). RS256/MFA-secret env vars are provided by
 * test/jest.setup.ts.
 */
class FakeUserRepository {
  private users = new Map<string, any>();
  async create(input: any) {
    const id = `user-${this.users.size + 1}`;
    const user = { id, ...input, status: 'pending_verification', mfaEnrolled: false, mfaTotpSecret: null };
    this.users.set(id, user);
    return user;
  }
  async findByEmailInTenant(tenantId: string, email: string) {
    return [...this.users.values()].find((u) => u.tenantId === tenantId && u.email === email) ?? null;
  }
  async findById(_tenantId: string, userId: string) {
    return this.users.get(userId) ?? null;
  }
  async setMfaSecret(_tenantId: string, userId: string, secret: string) {
    this.users.get(userId).mfaTotpSecret = secret;
  }
  async completeMfaEnrollment(_tenantId: string, userId: string) {
    const u = this.users.get(userId);
    u.mfaEnrolled = true;
    u.status = 'active';
  }
}
const noopAudit = { record: jest.fn() };
const fakeRefreshStore = { issue: jest.fn().mockResolvedValue({ token: 'rt', familyId: 'f1' }) };

describe('Contract: POST /auth/login + POST /auth/mfa/verify', () => {
  const users = new FakeUserRepository();
  const tokens = new TokenIssuerService();
  const registerService = new RegisterService(users as unknown as UserRepository);
  const mfaSetupService = new MfaSetupService(users as unknown as UserRepository);
  const loginService = new LoginService(users as unknown as UserRepository, tokens, noopAudit as any);
  const mfaVerifyService = new MfaVerifyService(
    users as unknown as UserRepository,
    tokens,
    fakeRefreshStore as any,
    noopAudit as any,
  );

  it('login returns only { mfaChallengeToken } — no session token before MFA', async () => {
    await registerService.register({
      tenantId: 't1',
      email: 'a@example.com',
      password: 'password123',
      role: 'learner',
      locale: 'en',
    });
    const result = await loginService.login('t1', 'a@example.com', 'password123');
    expect(Object.keys(result)).toEqual(['mfaChallengeToken']);
  });

  it('login rejects invalid credentials with 401 and no token', async () => {
    await expect(loginService.login('t1', 'a@example.com', 'wrong')).rejects.toBeInstanceOf(UnauthorizedException);
  });

  it('mfa/verify returns { accessToken, refreshToken, expiresIn } on a valid code', async () => {
    const { secret } = await mfaSetupService.setup('t1', 'a@example.com', 'password123');
    const login = await loginService.login('t1', 'a@example.com', 'password123');
    const code = authenticator.generate(secret);

    const result = await mfaVerifyService.verify(login.mfaChallengeToken, code);
    expect(result).toEqual({ accessToken: expect.any(String), refreshToken: 'rt', expiresIn: 900 });
  });

  it('mfa/verify rejects an invalid code with retryAllowed: true', async () => {
    const login = await loginService.login('t1', 'a@example.com', 'password123');
    await expect(mfaVerifyService.verify(login.mfaChallengeToken, '000000')).rejects.toMatchObject({
      response: { retryAllowed: true },
    });
  });
});
