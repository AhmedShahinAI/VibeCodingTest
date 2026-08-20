import { DynamicModule, Module } from '@nestjs/common';
import Redis from 'ioredis';
import { REDIS_CLIENT } from './auth/refresh-token.store';

@Module({})
export class RedisModule {
  static forRoot(): DynamicModule {
    return {
      module: RedisModule,
      global: true,
      providers: [
        {
          provide: REDIS_CLIENT,
          useFactory: () => new Redis(process.env.REDIS_URL ?? 'redis://localhost:6379'),
        },
      ],
      exports: [REDIS_CLIENT],
    };
  }
}
