<!--
Sync Impact Report
==================
Version change: TEMPLATE → 1.0.0 (initial ratification)
Modified principles: N/A (first concrete version; all placeholders filled)
Added sections:
  - Core Principles I–VII (Security & Zero-Trust First, Multi-Tenant Isolation,
    Bilingual-by-Default, Content Protection as a First-Class Concern,
    Architecture & Technology Discipline, MoSCoW & Phase Discipline,
    Non-Functional Bars)
  - Technology & Compliance Constraints (Section 2)
  - Development Workflow & Quality Gates (Section 3)
  - Governance
Removed sections: none (template placeholders only)
Deferred items: none — all placeholders resolved from docs/PRD.md and user input
Templates requiring follow-up:
  - .specify/templates/plan-template.md — ✅ no changes required (reads constitution at runtime)
  - .specify/templates/spec-template.md — ✅ no changes required
  - .specify/templates/tasks-template.md — ✅ no changes required
  - .claude/skills/* — ✅ no changes required (read constitution at runtime)
-->

# Elm Platform (منصة علم) Constitution

## Core Principles

### I. Security & Zero-Trust First (NON-NEGOTIABLE)
Every sensitive action MUST require authentication, and MFA MUST be enforced for
sign-in and other sensitive operations defined in the PRD. Authorization MUST
follow RBAC with least privilege across all six platform roles (Platform Owner,
Platform Administrator, Platform Supervisor, Course Provider/Instructor, Teaching
Assistant, Learner); no endpoint may skip a permission check. All data MUST be
encrypted at rest (AES-256) and in transit (TLS 1.3). Service-to-service calls
MUST authenticate under a Zero-Trust model — no implicit trust between internal
services. Every authentication attempt, permission denial, and sensitive action
(publish, payment, payout, content access, cross-tenant attempt) MUST be written
to an audit log. New code MUST be evaluated against the OWASP Top 10 before
merge. Rationale: the platform handles paid educational content, learner PII, and
instructor payouts across multiple tenants — a single authorization or encryption
gap is a breach, not a bug.

### II. Multi-Tenant Isolation (NON-NEGOTIABLE)
Every data query and write MUST be scoped to a resolved tenant context; there is
no code path that queries across tenants implicitly. Tenant context MUST be
resolved from the authenticated token/subdomain before any data access, and a
request with missing or mismatched tenant context MUST be rejected and logged as
suspicious. Cross-tenant data leakage is treated as a critical-severity defect
class, not a standard bug, and MUST block release. Rationale: this is a
multi-tenant SaaS; tenant isolation is the platform's core trust guarantee to
every instructor and learner organization on it.

### III. Bilingual-by-Default (Arabic/English, RTL/LTR)
Every user-facing screen, notification, and message MUST support both Arabic and
English with correct RTL and LTR rendering respectively. UI text MUST be
localized through the i18n resource system — hardcoded user-facing strings are
not permitted in application code. A missing translation key MUST fall back to
English and log the gap rather than rendering a raw key or crashing. Rationale:
first-class Arabic support (not a translated afterthought) is the platform's
stated market differentiator; RTL/LTR defects are UX-breaking, not cosmetic.

### IV. Content Protection as a First-Class Concern
Instructor media MUST never be exposed via direct, permanent, or guessable URLs.
Delivery MUST use DRM-protected streaming, short-lived signed URLs, and a dynamic
watermark carrying learner-identifying data during playback. Hotlinking MUST be
blocked, and every content-access event MUST be logged. Content-protection
requirements apply to any feature that streams or serves instructor-owned media,
including future AI/labs features that expose recorded or generated media.
Absolute prevention of screen recording is explicitly out of scope; controls
MUST maximize difficulty of unauthorized redistribution, not claim to eliminate
it. Rationale: instructor trust in the marketplace depends on credible content
protection; this is the platform's primary competitive differentiator alongside
Arabic-first support.

### V. Architecture & Technology Discipline
The frontend MUST be React 18 + TypeScript + Tailwind CSS with i18n/RTL support
and a DRM-capable video player. The backend MUST be Node.js/NestJS + TypeScript,
organized as independently deployable microservices aligned to platform domains
(auth, tenancy, courses, media, payments, assessments, certificates, AI,
community, notifications). PostgreSQL is the tenant-scoped system of record;
Redis is used for cache, sessions, and queues; media uses distributed object
storage. All infrastructure MUST be Kubernetes-ready and designed for horizontal
auto-scaling behind a CDN. Deviating from this stack for a new service requires
explicit justification recorded in that feature's plan. Rationale: a consistent,
microservices-first stack is what lets the platform scale 10x+ without a rewrite,
per the PRD's stated scalability target.

### VI. MoSCoW & Phase Discipline
Feature work MUST respect the PRD's MoSCoW prioritization: all P0 (Must Have)
features for a phase ship and pass validation before P1 (Should Have) work in
that phase begins, and P1 before P2. Features MUST be delivered in the PRD's
four-phase order (Foundation → Core Course Experience → Commerce, Assessment &
Certification → Engagement, AI & Launch Hardening) unless a deviation is
explicitly agreed and recorded, since later phases depend on earlier ones
(e.g., payments depend on auth/tenancy; certificates depend on assessments).
Each spec created via `/speckit-specify` MUST map to one or more PRD feature IDs
(e.g., P0-F001) so scope stays traceable to the PRD. Rationale: the PRD
explicitly names scope-creep-under-timeline-pressure (R1) as the platform's
top risk; phase gating is the agreed mitigation.

### VII. Non-Functional Bars
The following are release gates, not aspirations: API p95 response time < 500ms;
page load < 2s; protected video stream start < 3s; uptime ≥ 99.9% via multi-zone
HA; WCAG 2.1 AA accessibility on all learner- and instructor-facing UI;
structured JSON logging with alerting when error rate exceeds 1%. A feature that
does not meet these bars MUST NOT be marked done; it MUST either be optimized or
have an explicit, time-boxed, tracked exception. Rationale: these thresholds are
directly copied from the PRD's Non-Functional Requirements and Success Metrics —
they are commitments to users and stakeholders, not internal targets.

## Technology & Compliance Constraints

- Stack: React 18 + TypeScript + Tailwind (frontend); Node.js/NestJS + TypeScript
  microservices (backend); PostgreSQL + Redis; Kubernetes + CDN; JWT with
  refresh-token rotation for session auth.
- External dependencies requiring integration contracts before use: a commercial
  DRM provider (Widevine/PlayReady/FairPlay), a regional payment gateway, an
  AI/LLM provider (tutor, grading, recommendations), and a CDN/distributed
  storage provider.
- Compliance: GDPR-aligned data handling; daily backups with 30-day retention; a
  documented disaster-recovery plan; a content-access audit trail; SIEM and WAF
  integration for production environments.
- AI-powered features (tutor, grading, feedback, recommendations, simulators,
  labs) MUST ship behind a feature flag (via the CMS/feature-flag system) so
  quality and cost can be evaluated before general availability, per the PRD's
  risk register (R5).

## Development Workflow & Quality Gates

- Every feature spec MUST identify which of the six user roles it affects and
  what each role can/cannot do, consistent with the PRD's permission matrix.
- Every feature touching payments, commissions, or refunds MUST use idempotent
  transaction handling and be covered by tests that assert duplicate-charge
  prevention, per the PRD's risk register (R4).
- Every feature touching tenant-scoped data MUST include an explicit
  cross-tenant-isolation test case before it is considered complete.
- Every feature touching protected media MUST include a test or manual
  verification step confirming no direct/unsigned media URL is ever returned to
  a client.
- Localization (AR/EN, RTL/LTR) MUST be verified for any new user-facing screen
  before merge — this is a required review checklist item, not optional polish.
- Plans and tasks generated by Spec Kit commands MUST cite the PRD feature ID(s)
  (e.g., P0-F005) they implement so a reviewer can trace scope back to Section 6
  of docs/PRD.md.

## Governance

This constitution supersedes ad hoc practice for all Elm Platform work planned
or executed through Spec Kit. Every `/speckit-plan` and `/speckit-tasks` output
MUST be checked against these principles before implementation begins; any
violation MUST be justified in that feature's plan under an explicit
"Constitution Deviation" note or resolved before proceeding.

Amendments: propose a change via `/speckit-constitution` with the specific
principle(s) affected and rationale. Versioning follows semantic versioning:
MAJOR for backward-incompatible governance/principle removals or redefinitions,
MINOR for a new principle or materially expanded guidance, PATCH for wording or
clarification fixes. Every amendment updates the Sync Impact Report at the top
of this file and the Last Amended date below.

Compliance review: each feature's `/speckit-analyze` pass (or, absent that, its
plan review) MUST confirm alignment with this constitution before
`/speckit-implement` is invoked. Unresolved conflicts block implementation.

**Version**: 1.0.0 | **Ratified**: 2026-08-11 | **Last Amended**: 2026-08-11
