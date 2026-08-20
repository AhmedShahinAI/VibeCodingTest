import { Injectable, NotFoundException } from '@nestjs/common';
import { PermissionResolver, PrismaService } from '@elm/shared';
import { DEFAULT_PERMISSION_MATRIX } from './permission-matrix';
import { SupervisorOverrideRepository } from './supervisor-override.repository';

/**
 * Resolves a user's effective permission set: role defaults, with Platform
 * Supervisor overrides layered on top (spec FR-014). Implements the shared
 * `PermissionResolver` interface so `RbacGuard` (used by every service) can
 * enforce it without owning the RBAC data model itself — see
 * `@elm/shared`'s `permission-resolver.interface.ts` for why this split
 * exists.
 */
@Injectable()
export class RbacService implements PermissionResolver {
  constructor(
    private readonly prisma: PrismaService,
    private readonly overrides: SupervisorOverrideRepository,
  ) {}

  async resolveEffectivePermissions(userId: string, tenantId: string): Promise<Set<string>> {
    const user = await this.prisma.withTenant(tenantId, (tx) => tx.user.findFirst({ where: { id: userId, tenantId } }));
    if (!user) {
      throw new NotFoundException();
    }

    const permissions = new Set<string>(DEFAULT_PERMISSION_MATRIX[user.role]);

    if (user.role === 'platform_supervisor') {
      const overrides = await this.overrides.findForUser(tenantId, userId);
      for (const override of overrides) {
        if (override.granted) {
          permissions.add(override.permissionKey);
        } else {
          permissions.delete(override.permissionKey);
        }
      }
    }

    return permissions;
  }

  /** Used by `PUT /rbac/supervisor-overrides/:userId` to reject a non-Supervisor target (spec FR-014). */
  async requireSupervisor(tenantId: string, userId: string): Promise<void> {
    const user = await this.prisma.withTenant(tenantId, (tx) => tx.user.findFirst({ where: { id: userId, tenantId } }));
    if (!user || user.role !== 'platform_supervisor') {
      throw new NotFoundException();
    }
  }
}
