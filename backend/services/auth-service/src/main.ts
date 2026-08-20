import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { JsonLoggerService } from '@elm/shared';
import { AppModule } from './app.module';

async function bootstrap() {
  const logger = new JsonLoggerService('auth-service', (rate) => {
    // eslint-disable-next-line no-console
    console.error(JSON.stringify({ level: 'alert', message: 'error rate exceeded 1%', rate }));
  });

  const app = await NestFactory.create(AppModule, { logger });
  app.useGlobalPipes(new ValidationPipe({ whitelist: true, forbidNonWhitelisted: true, transform: true }));

  const port = process.env.PORT ? Number(process.env.PORT) : 3001;
  await app.listen(port);
  logger.log(`auth-service listening on port ${port}`);
}

bootstrap();
