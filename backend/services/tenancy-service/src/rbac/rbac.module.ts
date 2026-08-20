import { Module } from '@nestjs/common';
import { ElmSharedModule, PERMISSION_RESOLVER, RbacGuard } from '@elm/shared';
import { RbacService } from './rbac.service';
import { SupervisorOverrideRepository } from './supervisor-override.repository';
import { PermissionsController } from './permissions.controller';
import { SupervisorOverridesController } from './supervisor-overrides.controller';

/**
 * Provides `RbacGuard` locally (not via ElmSharedModule — see that module's
 * comment) so its `PERMISSION_RESOLVER` dependency resolves to this
 * service's own `RbacService` from this module's own injector.
 */
@Module({
  imports: [ElmSharedModule],
  controllers: [PermissionsController, SupervisorOverridesController],
  providers: [
    RbacService,
    SupervisorOverrideRepository,
    { provide: PERMISSION_RESOLVER, useExisting: RbacService },
    RbacGuard,
  ],
  exports: [RbacService, RbacGuard],
})
export class RbacModule {}
