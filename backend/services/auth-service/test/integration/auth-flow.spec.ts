import * as bcrypt from 'bcrypt';
import { ConflictException, UnauthorizedException } from '@nestjs/common';
import { RegisterService } from '../../src/auth/register.service';
import { LoginService } from '../../src/auth/login.service';
import { MfaSetupService } from '../../src/auth/mfa-setup.service';
import { MfaVerifyService } from '../../src/auth/mfa-verify.service';
import { TokenIssuerService } from '../../src/auth/token-issuer.service';
import { UserRepository } from '../../src/users/user.repository';
import { authenticator } from 'otplib';

/**
 * Exercises the full register -> mfa-setup -> login -> mfa-verify flow
 * (spec User Story 1 / quickstart.md Scenario 1) against an in-memory fake
 * of UserRepository, so it runs without a live Postgres/Redis instance.
 * Full integration coverage against real Postgres (RLS) and Redis (refresh
 * rotation) is the CI-environment follow-up noted in quickstart.md.
 *
 * RS256 keys and the MFA challenge secret are generated fresh per test run
 * by test/jest.setup.ts (see jest.config.js `setupFiles`).
 */

class FakeUserRepository {
  private users = new Map<string, any>();
  private idCounter = 0;

  async create(input: any) {
    const id = `user-${++this.idCounter}`;
    const user = { id, ...input, status: 'pending_verification', mfaEnrolled: false, mfaTotpSecret: null };
    this.users.set(id, user);
    return user;
  }

  async findByEmailInTenant(tenantId: string, email: string) {
    return [...this.users.values()].find((u) => u.tenantId === tenantId && u.email === email) ?? null;
  }

  async findById(tenantId: string, userId: string) {
    const user = this.users.get(userId);
    return user && user.tenantId === tenantId ? user : null;
  }

  async setMfaSecret(_tenantId: string, userId: string, secret: string) {
    this.users.get(userId).mfaTotpSecret = secret;
  }

  async completeMfaEnrollment(_tenantId: string, userId: string) {
    const user = this.users.get(userId);
    user.mfaEnrolled = true;
    user.status = 'active';
  }
}

class FakeAuditLogService {
  events: any[] = [];
  async record(event: any) {
    this.events.push(event);
  }
}

class FakeRefreshTokenStore {
  async issue(userId: string, tenantId: string) {
    return { token: 'refresh-token-1', familyId: 'family-1', userId, tenantId };
  }
}

const TENANT_ID = 'tenant-a';

describe('User Story 1: Secure Registration & Sign-In', () => {
  let users: FakeUserRepository;
  let audit: FakeAuditLogService;
  let tokens: TokenIssuerService;
  let registerService: RegisterService;
  let loginService: LoginService;
  let mfaSetupService: MfaSetupService;
  let mfaVerifyService: MfaVerifyService;

  beforeEach(() => {
    users = new FakeUserRepository();
    audit = new FakeAuditLogService();
    tokens = new TokenIssuerService();
    registerService = new RegisterService(users as unknown as UserRepository);
    loginService = new LoginService(users as unknown as UserRepository, tokens, audit as any);
    mfaSetupService = new MfaSetupService(users as unknown as UserRepository);
    mfaVerifyService = new MfaVerifyService(
      users as unknown as UserRepository,
      tokens,
      new FakeRefreshTokenStore() as any,
      audit as any,
    );
  });

  it('completes register -> mfa-setup -> login -> mfa-verify and issues a session', async () => {
    const registered = await registerService.register({
      tenantId: TENANT_ID,
      email: 'layla@example.com',
      password: 'correct horse battery staple',
      role: 'learner',
      locale: 'en',
    });
    expect(registered.mfaSetupRequired).toBe(true);

    const { secret } = await mfaSetupService.setup(TENANT_ID, 'layla@example.com', 'correct horse battery staple');

    const login = await loginService.login(TENANT_ID, 'layla@example.com', 'correct horse battery staple');
    expect(login.mfaChallengeToken).toBeTruthy();

    const code = authenticator.generate(secret);
    const result = await mfaVerifyService.verify(login.mfaChallengeToken, code);

    expect(result.accessToken).toBeTruthy();
    expect(result.refreshToken).toBe('refresh-token-1');
    expect(audit.events.map((e) => e.eventType)).toContain('login_success');
  });

  it('rejects duplicate registration within the same tenant (FR: no duplicate email)', async () => {
    await registerService.register({
      tenantId: TENANT_ID,
      email: 'dup@example.com',
      password: 'password12345',
      role: 'learner',
      locale: 'en',
    });

    await expect(
      registerService.register({
        tenantId: TENANT_ID,
        email: 'dup@example.com',
        password: 'password12345',
        role: 'learner',
        locale: 'en',
      }),
    ).rejects.toBeInstanceOf(ConflictException);
  });

  it('never issues a token on invalid credentials (FR-006 / SC-006)', async () => {
    await registerService.register({
      tenantId: TENANT_ID,
      email: 'wrongpass@example.com',
      password: 'correctpassword',
      role: 'learner',
      locale: 'en',
    });

    await expect(loginService.login(TENANT_ID, 'wrongpass@example.com', 'nope')).rejects.toBeInstanceOf(
      UnauthorizedException,
    );
    expect(audit.events.some((e) => e.eventType === 'login_failure')).toBe(true);
  });

  it('never issues a token on an invalid MFA code (FR-007 / SC-006)', async () => {
    await registerService.register({
      tenantId: TENANT_ID,
      email: 'badmfa@example.com',
      password: 'correctpassword',
      role: 'learner',
      locale: 'en',
    });
    await mfaSetupService.setup(TENANT_ID, 'badmfa@example.com', 'correctpassword');
    const login = await loginService.login(TENANT_ID, 'badmfa@example.com', 'correctpassword');

    await expect(mfaVerifyService.verify(login.mfaChallengeToken, '000000')).rejects.toBeInstanceOf(
      UnauthorizedException,
    );
    expect(audit.events.some((e) => e.eventType === 'mfa_failure')).toBe(true);
  });
});

it('sanity: bcrypt is available for password hashing', async () => {
  const hash = await bcrypt.hash('x', 4);
  expect(await bcrypt.compare('x', hash)).toBe(true);
});
