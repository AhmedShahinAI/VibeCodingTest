import { Body, Controller, Get, Put, Req, UseGuards } from '@nestjs/common';
import { IsIn } from 'class-validator';
import { JwtAuthGuard, TenantContextGuard, AuthenticatedRequest } from '@elm/shared';
import { UserRepository } from './user.repository';

export class UpdateLocaleDto {
  @IsIn(['ar', 'en'])
  locale!: 'ar' | 'en';
}

/** `GET /me` / `PUT /me/locale` — profile and language preference (spec FR-019). */
@Controller('api/v1')
@UseGuards(JwtAuthGuard, TenantContextGuard)
export class MeController {
  constructor(private readonly users: UserRepository) {}

  @Get('me')
  async me(@Req() request: AuthenticatedRequest) {
    const user = await this.users.findById(request.tenantId!, request.userId!);
    return { userId: user!.id, tenantId: user!.tenantId, role: user!.role, locale: user!.locale };
  }

  @Put('me/locale')
  async updateLocale(@Body() dto: UpdateLocaleDto, @Req() request: AuthenticatedRequest) {
    await this.users.updateLocale(request.tenantId!, request.userId!, dto.locale);
    return { locale: dto.locale };
  }
}
