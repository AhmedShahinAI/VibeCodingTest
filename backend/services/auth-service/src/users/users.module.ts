import { Module } from '@nestjs/common';
import { ElmSharedModule } from '@elm/shared';
import { UserRepository } from './user.repository';
import { MeController } from './me.controller';

@Module({
  imports: [ElmSharedModule],
  controllers: [MeController],
  providers: [UserRepository],
  exports: [UserRepository],
})
export class UsersModule {}
