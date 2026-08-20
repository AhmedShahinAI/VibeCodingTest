import { ConflictException, Injectable } from '@nestjs/common';
import * as bcrypt from 'bcrypt';
import { UserRepository } from '../users/user.repository';

export interface RegisterInput {
  tenantId: string;
  email: string;
  password: string;
  role: 'learner' | 'course_provider';
  locale: 'ar' | 'en';
}

export interface RegisterResult {
  userId: string;
  status: string;
  mfaSetupRequired: true;
}

const BCRYPT_ROUNDS = 12;

/**
 * Implements FR-001 (email/password registration). Self-registration is
 * limited to Learner and Course Provider roles per spec.md Assumptions —
 * staff roles are provisioned within a tenant, not self-registered.
 */
@Injectable()
export class RegisterService {
  constructor(private readonly users: UserRepository) {}

  async register(input: RegisterInput): Promise<RegisterResult> {
    const existing = await this.users.findByEmailInTenant(input.tenantId, input.email);
    if (existing) {
      throw new ConflictException({
        error: 'conflict',
        reason: 'email_already_registered',
        messageKey: 'errors.emailAlreadyRegistered',
      });
    }

    const passwordHash = await bcrypt.hash(input.password, BCRYPT_ROUNDS);
    const user = await this.users.create({
      tenantId: input.tenantId,
      email: input.email,
      passwordHash,
      role: input.role,
      locale: input.locale,
    });

    return { userId: user.id, status: user.status, mfaSetupRequired: true };
  }
}
