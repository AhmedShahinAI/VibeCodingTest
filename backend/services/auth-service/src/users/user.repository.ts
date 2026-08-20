import { Injectable } from '@nestjs/common';
import { PrismaService, User, UserRole } from '@elm/shared';

export interface CreateUserInput {
  tenantId: string;
  email: string;
  passwordHash?: string;
  googleSubjectId?: string;
  role: UserRole;
  locale: 'ar' | 'en';
}

/**
 * All lookups run inside `PrismaService.withTenant` so Postgres RLS (see
 * shared/prisma/migrations) is satisfied and cross-tenant rows can never be
 * returned (spec FR-016), except `findByEmailAcrossTenants`, which is used
 * only pre-tenant-resolution during login to give a uniform "invalid
 * credentials" response without leaking which tenant an email belongs to.
 */
@Injectable()
export class UserRepository {
  constructor(private readonly prisma: PrismaService) {}

  async create(input: CreateUserInput): Promise<User> {
    return this.prisma.withTenant(input.tenantId, (tx) =>
      tx.user.create({
        data: {
          tenantId: input.tenantId,
          email: input.email,
          passwordHash: input.passwordHash,
          googleSubjectId: input.googleSubjectId,
          role: input.role,
          locale: input.locale,
        },
      }),
    );
  }

  async findByEmailInTenant(tenantId: string, email: string): Promise<User | null> {
    return this.prisma.withTenant(tenantId, (tx) => tx.user.findUnique({ where: { tenantId_email: { tenantId, email } } }));
  }

  async findById(tenantId: string, userId: string): Promise<User | null> {
    return this.prisma.withTenant(tenantId, (tx) => tx.user.findFirst({ where: { id: userId, tenantId } }));
  }

  async setMfaSecret(tenantId: string, userId: string, secret: string): Promise<void> {
    await this.prisma.withTenant(tenantId, (tx) =>
      tx.user.update({ where: { id: userId }, data: { mfaTotpSecret: secret } }),
    );
  }

  async completeMfaEnrollment(tenantId: string, userId: string): Promise<void> {
    await this.prisma.withTenant(tenantId, (tx) =>
      tx.user.update({ where: { id: userId }, data: { mfaEnrolled: true, status: 'active' } }),
    );
  }

  /** Implements spec FR-019 — persists the user's language preference. */
  async updateLocale(tenantId: string, userId: string, locale: 'ar' | 'en'): Promise<void> {
    await this.prisma.withTenant(tenantId, (tx) => tx.user.update({ where: { id: userId }, data: { locale } }));
  }
}
