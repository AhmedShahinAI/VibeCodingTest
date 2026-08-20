import { Body, Controller, HttpCode, Post } from '@nestjs/common';
import { RefreshTokenStore } from '@elm/shared';
import { RefreshDto } from './dto/auth.dto';

/** `POST /auth/logout` — revokes the token family the given refresh token belongs to. */
@Controller('api/v1/auth')
export class LogoutController {
  constructor(private readonly refreshTokens: RefreshTokenStore) {}

  @Post('logout')
  @HttpCode(204)
  async logout(@Body() dto: RefreshDto): Promise<void> {
    // Rotate-then-revoke rather than looking up the family directly: this
    // reuses the store's own hash lookup so logout works from the current
    // token without exposing a separate "resolve family by token" method.
    try {
      const rotated = await this.refreshTokens.rotate(dto.refreshToken);
      await this.refreshTokens.revokeFamily(rotated.familyId);
    } catch {
      // Already invalid/expired/revoked — logout is idempotent either way.
    }
  }
}
