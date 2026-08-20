import { Injectable } from '@nestjs/common';
import { PrismaService, Tenant } from '@elm/shared';

@Injectable()
export class TenantRepository {
  constructor(private readonly prisma: PrismaService) {}

  /**
   * Deliberately NOT wrapped in `withTenant` — `tenants` is the root entity
   * a request's tenant context is resolved *from*, so it is not itself
   * row-level-secured (see prisma RLS migration notes). Same-tenant-only
   * access is enforced in `TenantsController`, not by RLS, for this table.
   */
  async findById(id: string): Promise<Tenant | null> {
    return this.prisma.tenant.findUnique({ where: { id } });
  }
}
