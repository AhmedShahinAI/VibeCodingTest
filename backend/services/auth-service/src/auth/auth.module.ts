import { Module } from '@nestjs/common';
import { ElmSharedModule } from '@elm/shared';
import { UsersModule } from '../users/users.module';
import { AuthController } from './auth.controller';
import { RefreshController } from './refresh.controller';
import { LogoutController } from './logout.controller';
import { RegisterService } from './register.service';
import { MfaSetupService } from './mfa-setup.service';
import { LoginService } from './login.service';
import { MfaVerifyService } from './mfa-verify.service';
import { TokenIssuerService } from './token-issuer.service';

@Module({
  imports: [ElmSharedModule, UsersModule],
  controllers: [AuthController, RefreshController, LogoutController],
  providers: [RegisterService, MfaSetupService, LoginService, MfaVerifyService, TokenIssuerService],
})
export class AuthModule {}
