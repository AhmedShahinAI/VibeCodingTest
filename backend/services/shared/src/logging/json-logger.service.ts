import { LoggerService } from '@nestjs/common';

/**
 * Structured JSON logger (constitution Principle VII: "structured JSON
 * logging with alerting when error rate exceeds 1%"). Emits one JSON object
 * per line to stdout so a log shipper (e.g. a Kubernetes sidecar → SIEM) can
 * parse it without a custom grok pattern, and tracks a rolling error-rate
 * counter that calls `onErrorRateExceeded` when the 1% threshold is crossed
 * over the trailing `windowSize` log lines.
 *
 * Implements `LoggerService` directly (rather than extending
 * `ConsoleLogger`) because Nest's built-in logger methods take a
 * `context?: string` as their second argument, while this logger takes a
 * structured `meta` object — extending would make the override signatures
 * incompatible.
 */
export class JsonLoggerService implements LoggerService {
  private windowEvents: boolean[] = []; // true = error-level event
  private readonly windowSize = 200;
  private alertFired = false;

  constructor(
    private readonly context: string,
    private readonly onErrorRateExceeded?: (rate: number) => void,
  ) {}

  private write(level: string, message: unknown, meta?: Record<string, unknown>) {
    const entry = {
      timestamp: new Date().toISOString(),
      level,
      context: this.context,
      message,
      ...meta,
    };
    // eslint-disable-next-line no-console
    console.log(JSON.stringify(entry));
    this.trackErrorRate(level === 'error');
  }

  private trackErrorRate(isError: boolean) {
    this.windowEvents.push(isError);
    if (this.windowEvents.length > this.windowSize) {
      this.windowEvents.shift();
    }
    if (this.windowEvents.length < 20) {
      return; // not enough samples yet to compute a meaningful rate
    }
    const errorRate = this.windowEvents.filter(Boolean).length / this.windowEvents.length;
    if (errorRate > 0.01 && !this.alertFired) {
      this.alertFired = true;
      this.onErrorRateExceeded?.(errorRate);
    } else if (errorRate <= 0.01) {
      this.alertFired = false;
    }
  }

  log(message: unknown, meta?: Record<string, unknown>) {
    this.write('info', message, meta);
  }

  error(message: unknown, trace?: string, meta?: Record<string, unknown>) {
    this.write('error', message, { trace, ...meta });
  }

  warn(message: unknown, meta?: Record<string, unknown>) {
    this.write('warn', message, meta);
  }

  debug(message: unknown, meta?: Record<string, unknown>) {
    this.write('debug', message, meta);
  }
}
