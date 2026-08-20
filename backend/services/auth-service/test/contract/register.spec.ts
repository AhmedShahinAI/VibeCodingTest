import { ConflictException } from '@nestjs/common';
import { RegisterService } from '../../src/auth/register.service';
import { UserRepository } from '../../src/users/user.repository';

/** Contract test for `POST /auth/register` (contracts/auth-api.md). */
class FakeUserRepository {
  private users = new Map<string, any>();
  async create(input: any) {
    const id = `user-${this.users.size + 1}`;
    const user = { id, ...input, status: 'pending_verification' };
    this.users.set(`${input.tenantId}:${input.email}`, user);
    return user;
  }
  async findByEmailInTenant(tenantId: string, email: string) {
    return this.users.get(`${tenantId}:${email}`) ?? null;
  }
}

describe('Contract: POST /auth/register', () => {
  it('returns 201-shape { userId, status, mfaSetupRequired: true } on success', async () => {
    const service = new RegisterService(new FakeUserRepository() as unknown as UserRepository);
    const result = await service.register({
      tenantId: 'tenant-a',
      email: 'new@example.com',
      password: 'a-strong-password',
      role: 'learner',
      locale: 'en',
    });

    expect(result).toEqual({ userId: expect.any(String), status: 'pending_verification', mfaSetupRequired: true });
  });

  it('returns 409 for an email already registered in the same tenant', async () => {
    const repo = new FakeUserRepository();
    const service = new RegisterService(repo as unknown as UserRepository);
    const input = {
      tenantId: 'tenant-a',
      email: 'dupe@example.com',
      password: 'a-strong-password',
      role: 'learner' as const,
      locale: 'en' as const,
    };
    await service.register(input);
    await expect(service.register(input)).rejects.toBeInstanceOf(ConflictException);
  });
});
