import { Module } from '@nestjs/common';
import { ElmSharedModule } from '@elm/shared';
import { TenantRepository } from './tenant.repository';
import { TenantsController } from './tenants.controller';

@Module({
  imports: [ElmSharedModule],
  controllers: [TenantsController],
  providers: [TenantRepository],
})
export class TenantsModule {}
