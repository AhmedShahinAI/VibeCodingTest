import { Injectable, OnModuleDestroy, OnModuleInit } from '@nestjs/common';
import { PrismaClient } from '../prisma/generated/client';

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/**
 * Wraps PrismaClient and provides `withTenant`, which runs a callback inside
 * a transaction with Postgres session variable `app.current_tenant` set via
 * `SET LOCAL`. Row-Level Security policies (see prisma/migrations) key off
 * that variable, so every tenant-scoped query MUST go through `withTenant` —
 * a raw `prisma.user.findMany()` outside of it will see zero rows once RLS
 * is enabled (`current_setting(..., true)` is NULL for an unset variable).
 */
@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit, OnModuleDestroy {
  async onModuleInit() {
    await this.$connect();
  }

  async onModuleDestroy() {
    await this.$disconnect();
  }

  async withTenant<T>(
    tenantId: string,
    fn: (tx: Omit<PrismaClient, '$connect' | '$disconnect' | '$on' | '$transaction' | '$use' | '$extends'>) => Promise<T>,
  ): Promise<T> {
    // Postgres SET LOCAL does not accept a bind parameter for its value, so
    // the tenant id must be interpolated. It is validated as a UUID first to
    // close off SQL injection via this path (OWASP Top 10 / constitution I).
    if (!UUID_PATTERN.test(tenantId)) {
      throw new Error(`Invalid tenantId passed to withTenant: ${tenantId}`);
    }
    return this.$transaction(async (tx) => {
      await tx.$executeRawUnsafe(`SET LOCAL app.current_tenant = '${tenantId}'`);
      return fn(tx);
    });
  }
}
