import { IsBoolean, IsIn } from 'class-validator';
import { ALL_PERMISSION_KEYS } from '../permission-matrix';

export class SupervisorOverrideDto {
  @IsIn(ALL_PERMISSION_KEYS)
  permissionKey!: string;

  @IsBoolean()
  granted!: boolean;
}
