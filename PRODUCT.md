# Elm Platform (منصة علم)

## What is this product?

Elm Platform is a multi-tenant, bilingual (Arabic/English) training and
course-delivery platform. Phase 1 delivers its identity and access
foundation: account registration and sign-in with mandatory MFA, a six-role
permission system, strict per-tenant data isolation, and a fully localized
RTL/LTR dashboard shell.

## Who uses it?

Training organizations (tenants) and the people inside them: Platform
Owners and Administrators who run the tenant, Platform Supervisors who
oversee operations, Course Providers/Instructors who deliver training,
Teaching Assistants who support instructors, and Learners who take courses.

## Core problems it solves

- No trustworthy identity boundary exists without registration + MFA-backed sign-in
- Six distinct roles need enforced, auditable permission boundaries — not just UI hiding
- Tenants must never see or affect each other's data, even under application bugs
- Arabic-speaking and English-speaking users both need a first-class, direction-aware experience — not a translated afterthought

## Key capabilities (Phase 1)

- Registration and sign-in with mandatory TOTP-based MFA, rotating refresh tokens with reuse detection
- Role-scoped access across six roles (Owner, Administrator, Supervisor, Instructor, Teaching Assistant, Learner), enforced server-side and logged
- Multi-tenant isolation: every request resolved to one tenant, Postgres row-level security as defense-in-depth
- Bilingual AR/EN shell with RTL/LTR layout switching and graceful fallback on missing translations

## Register

Professional, authoritative, expert-led. Never salesy, never casual.

## Users

Arabic-speaking and English-speaking training organizations and their staff/instructors/learners in the MENA region, evaluating whether this platform is credible enough to run their training operations on.

## Voice

Direct and clear. Uses active voice. Speaks to institutional trust and operational control — not consumer excitement. Avoids jargon and avoids hype language ("revolutionary", "AI-powered", "#1").

## Anti-references

Avoid: consumer social-media aesthetic, generic SaaS dashboard blue, startup landing-page tropes (three-icon feature rows, gradient hero text, oversized emoji as icons). This is a premium, expert-led training institution product — not a consumer app.

## Goals

1. Build institutional trust through visual credibility and restraint
2. Make the security/access model (MFA, RBAC, tenant isolation) feel like a first-class trust signal, not fine print
3. Give Arabic content full parity with English — never a bolted-on translation
4. Keep admin/dashboard surfaces compact and scannable while public-facing surfaces stay premium and spacious

## Language and text direction

Bilingual: Arabic (RTL) and English (LTR), user-selectable. Admin/dashboard interfaces remain functional and legible in both directions; the language switcher persists the user's choice.
