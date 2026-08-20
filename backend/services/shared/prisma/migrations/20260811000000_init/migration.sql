-- CreateEnum
CREATE TYPE "TenantStatus" AS ENUM ('active', 'suspended');
CREATE TYPE "UserRole" AS ENUM ('platform_owner', 'platform_administrator', 'platform_supervisor', 'course_provider', 'teaching_assistant', 'learner');
CREATE TYPE "UserStatus" AS ENUM ('pending_verification', 'active', 'disabled');
CREATE TYPE "Locale" AS ENUM ('ar', 'en');
CREATE TYPE "AuditEventType" AS ENUM ('login_success', 'login_failure', 'mfa_failure', 'permission_denied', 'cross_tenant_attempt', 'token_reuse_detected');

-- CreateTable
CREATE TABLE "tenants" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "domain" TEXT NOT NULL,
    "status" "TenantStatus" NOT NULL DEFAULT 'active',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "tenants_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "users" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "password_hash" TEXT,
    "google_subject_id" TEXT,
    "role" "UserRole" NOT NULL,
    "mfa_enrolled" BOOLEAN NOT NULL DEFAULT false,
    "mfa_totp_secret" TEXT,
    "locale" "Locale" NOT NULL DEFAULT 'en',
    "status" "UserStatus" NOT NULL DEFAULT 'pending_verification',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "supervisor_permission_overrides" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "permission_key" TEXT NOT NULL,
    "granted" BOOLEAN NOT NULL,
    "set_by_user_id" TEXT NOT NULL,
    "updated_at" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "supervisor_permission_overrides_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "audit_log_entries" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT,
    "user_id" TEXT,
    "event_type" "AuditEventType" NOT NULL,
    "detail" JSONB,
    "occurred_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "audit_log_entries_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "tenants_domain_key" ON "tenants"("domain");
CREATE UNIQUE INDEX "users_google_subject_id_key" ON "users"("google_subject_id");
CREATE INDEX "users_tenant_id_idx" ON "users"("tenant_id");
CREATE UNIQUE INDEX "users_tenant_id_email_key" ON "users"("tenant_id", "email");
CREATE INDEX "supervisor_permission_overrides_tenant_id_idx" ON "supervisor_permission_overrides"("tenant_id");
CREATE UNIQUE INDEX "supervisor_permission_overrides_user_id_permission_key_key" ON "supervisor_permission_overrides"("user_id", "permission_key");
CREATE INDEX "audit_log_entries_tenant_id_idx" ON "audit_log_entries"("tenant_id");
CREATE INDEX "audit_log_entries_event_type_idx" ON "audit_log_entries"("event_type");

-- AddForeignKey
ALTER TABLE "users" ADD CONSTRAINT "users_tenant_id_fkey" FOREIGN KEY ("tenant_id") REFERENCES "tenants"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "supervisor_permission_overrides" ADD CONSTRAINT "supervisor_permission_overrides_tenant_id_fkey" FOREIGN KEY ("tenant_id") REFERENCES "tenants"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "supervisor_permission_overrides" ADD CONSTRAINT "supervisor_permission_overrides_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "supervisor_permission_overrides" ADD CONSTRAINT "supervisor_permission_overrides_set_by_user_id_fkey" FOREIGN KEY ("set_by_user_id") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "audit_log_entries" ADD CONSTRAINT "audit_log_entries_tenant_id_fkey" FOREIGN KEY ("tenant_id") REFERENCES "tenants"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "audit_log_entries" ADD CONSTRAINT "audit_log_entries_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;
