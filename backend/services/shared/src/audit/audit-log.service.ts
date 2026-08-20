import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma.service';
import { AuditEventType, Prisma } from '../../prisma/generated/client';

export interface RecordAuditEventInput {
  tenantId: string | null;
  userId?: string | null;
  eventType: AuditEventType;
  detail?: Prisma.InputJsonValue;
}

/**
 * Writes AuditLogEntry rows synchronously, in the same transaction as the
 * action being recorded (see research.md "Audit Logging"). Every auth
 * attempt, permission denial, and cross-tenant attempt MUST go through this
 * service — spec SC-005 requires the entry to exist within the same request
 * cycle as the event, so no queue/async path is used here.
 *
 * The `audit_log_entries` RLS policy (see prisma/migrations) allows a row
 * whose tenant_id matches `app.current_tenant` OR is NULL. A tenant-scoped
 * event therefore MUST be written inside `PrismaService.withTenant` so that
 * session variable is set — otherwise Postgres silently rejects the insert.
 */
@Injectable()
export class AuditLogService {
  constructor(private readonly prisma: PrismaService) {}

  async record(event: RecordAuditEventInput): Promise<void> {
    const data = {
      tenantId: event.tenantId ?? undefined,
      userId: event.userId ?? undefined,
      eventType: event.eventType,
      detail: event.detail,
    };

    if (event.tenantId) {
      await this.prisma.withTenant(event.tenantId, (tx) => tx.auditLogEntry.create({ data }));
    } else {
      // No tenant to resolve (e.g. malformed token/subdomain) — RLS still
      // accepts this because tenant_id IS NULL is unconditionally allowed.
      await this.prisma.auditLogEntry.create({ data });
    }
  }
}
