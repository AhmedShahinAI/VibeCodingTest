import { Body, Controller, HttpCode, Post, Req, UseGuards } from '@nestjs/common';
import { Throttle } from '@nestjs/throttler';
import { SubdomainTenantGuard, AuthenticatedRequest } from '@elm/shared';
import { RegisterDto, MfaSetupDto, LoginDto, MfaVerifyDto } from './dto/auth.dto';
import { RegisterService } from './register.service';
import { MfaSetupService } from './mfa-setup.service';
import { LoginService } from './login.service';
import { MfaVerifyService } from './mfa-verify.service';

// Stricter than the app-wide default (100/min): these are the endpoints a
// credential-stuffing or MFA-brute-force attempt would hit (constitution
// Principle I / PRD NFR "rate limiting; anti-bot").
const CREDENTIAL_ENDPOINT_THROTTLE = { default: { limit: 5, ttl: 60_000 } };

/**
 * Pre-authentication endpoints (spec User Story 1). Tenant is resolved from
 * subdomain via `SubdomainTenantGuard` since no access token exists yet on
 * any of these routes — see contracts/auth-api.md.
 */
@Controller('api/v1/auth')
@UseGuards(SubdomainTenantGuard)
export class AuthController {
  constructor(
    private readonly registerService: RegisterService,
    private readonly mfaSetupService: MfaSetupService,
    private readonly loginService: LoginService,
    private readonly mfaVerifyService: MfaVerifyService,
  ) {}

  @Post('register')
  @Throttle(CREDENTIAL_ENDPOINT_THROTTLE)
  register(@Body() dto: RegisterDto, @Req() request: AuthenticatedRequest) {
    return this.registerService.register({ tenantId: request.tenantId!, ...dto });
  }

  @Post('mfa/setup')
  @HttpCode(200)
  @Throttle(CREDENTIAL_ENDPOINT_THROTTLE)
  mfaSetup(@Body() dto: MfaSetupDto, @Req() request: AuthenticatedRequest) {
    return this.mfaSetupService.setup(request.tenantId!, dto.email, dto.password);
  }

  @Post('login')
  @HttpCode(200)
  @Throttle(CREDENTIAL_ENDPOINT_THROTTLE)
  login(@Body() dto: LoginDto, @Req() request: AuthenticatedRequest) {
    return this.loginService.login(request.tenantId!, dto.email, dto.password);
  }

  @Post('mfa/verify')
  @HttpCode(200)
  @Throttle(CREDENTIAL_ENDPOINT_THROTTLE)
  mfaVerify(@Body() dto: MfaVerifyDto) {
    return this.mfaVerifyService.verify(dto.mfaChallengeToken, dto.code);
  }
}
