import { IsEmail, IsIn, IsString, MinLength } from 'class-validator';

export class RegisterDto {
  @IsEmail()
  email!: string;

  @IsString()
  @MinLength(8)
  password!: string;

  @IsIn(['learner', 'course_provider'])
  role!: 'learner' | 'course_provider';

  @IsIn(['ar', 'en'])
  locale!: 'ar' | 'en';
}

export class MfaSetupDto {
  @IsEmail()
  email!: string;

  @IsString()
  password!: string;
}

export class LoginDto {
  @IsEmail()
  email!: string;

  @IsString()
  password!: string;
}

export class MfaVerifyDto {
  @IsString()
  mfaChallengeToken!: string;

  @IsString()
  code!: string;
}

export class RefreshDto {
  @IsString()
  refreshToken!: string;
}
