import { Injectable } from '@nestjs/common';
import { PrismaService, SupervisorPermissionOverride } from '@elm/shared';

@Injectable()
export class SupervisorOverrideRepository {
  constructor(private readonly prisma: PrismaService) {}

  async findForUser(tenantId: string, userId: string): Promise<SupervisorPermissionOverride[]> {
    return this.prisma.withTenant(tenantId, (tx) =>
      tx.supervisorPermissionOverride.findMany({ where: { userId } }),
    );
  }

  async upsert(
    tenantId: string,
    userId: string,
    permissionKey: string,
    granted: boolean,
    setByUserId: string,
  ): Promise<SupervisorPermissionOverride> {
    return this.prisma.withTenant(tenantId, (tx) =>
      tx.supervisorPermissionOverride.upsert({
        where: { userId_permissionKey: { userId, permissionKey } },
        create: { tenantId, userId, permissionKey, granted, setByUserId },
        update: { granted, setByUserId },
      }),
    );
  }
}
