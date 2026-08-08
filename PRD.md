# Elm Platform (منصة علم) — Product Requirements Document

---

## 1. Project Identity

| Field | Value |
|-------|-------|
| Project Name | Elm Platform (منصة علم) |
| Project Type | Web Application / Multi-Tenant Educational SaaS |
| Project ID | PRD-001 |
| Version | v1.0 |
| Status | Draft |
| Priority | High |
| Created Date | 2026-08-06 |
| Last Updated | 2026-08-06 |
| Owner | Dr. Ahmed Shahin |
| Team Members | Frontend Dev, Backend Dev, DevOps Engineer, ML/AI Engineer, Designer, QA Engineer |
| Tech Stack | React 18 + TypeScript + Tailwind (Frontend) · Node.js/NestJS + TypeScript (Backend, microservices) · PostgreSQL + Redis · Kubernetes + CDN |
| Repository | [TBD] |
| Git Branch Prefix | NNN-feature-name |
| PRD File Path | docs/PRD.md |

---

## 2. Problem & Purpose

### Problem Statement
Existing learning platforms fall into two gaps. Simple platforms are shallow — no AI simulators, no interactive labs, weak assessment. Professional platforms are capable but do not treat Arabic as a first-class language (poor RTL support, machine-translated UI) and provide weak protection for instructor content, exposing course material to unauthorized download and redistribution. Instructors therefore lack a trusted marketplace that protects their intellectual property and pays fair commissions, while Arabic-speaking learners lack a genuinely world-class, bilingual, high-interactivity learning experience.

### Project Purpose
Deliver a multi-tenant educational SaaS where instructors can create and publish protected courses, and learners can purchase, follow, and complete them with certificates — fully bilingual (Arabic/English, RTL/LTR) with strong content protection and integrated AI-powered learning tools.

### Business Value
A learning marketplace generating revenue through subscriptions plus per-course commissions. Core differentiation: robust content protection (DRM, dynamic watermarking, signed URLs), embedded AI tooling (tutor, grading, recommendations), and complete first-class Arabic support.

### Opportunity
Demand for high-interactivity digital learning in the Arabic-speaking region is growing rapidly, and no incumbent combines strong content protection, native bilingual support, and AI-driven interactivity in a single scalable platform.

---

## 3. Goals & Objectives

### Primary Goal
Launch a multi-tenant educational platform enabling a course provider to create and publish a protected course, and a learner to purchase, follow, assess, and earn a certificate — fully bilingual (Arabic/English) end to end.

### Objectives
1. Enable secure, role-based access for six user roles across isolated tenants.
2. Allow instructors to author, upload, protect, and publish complete courses.
3. Protect delivered content against unauthorized download and redistribution.
4. Process subscriptions, purchases, payments, and instructor commissions reliably.
5. Provide bilingual (AR/EN) UI, notifications, and content with full RTL/LTR support.

### Success Definition
The platform is successful when an instructor can publish a protected course and a learner can purchase it, consume the protected video/files, pass assessments, and receive a certificate — with payment and commission correctly settled — in both Arabic and English.

### Non-Goals
Native mobile applications, languages beyond Arabic/English at launch, and third-party external marketplace integrations are explicitly excluded from v1.

---

## 4. Scope

### In Scope
- Authentication + MFA and RBAC for six roles
- Multi-tenant architecture with tenant isolation
- Course authoring and publishing (video + files)
- Content protection: DRM, signed URLs, dynamic watermark, anti-download
- Subscriptions, payments, and instructor commissions
- Progress tracking and certificates
- Assessments / quizzes
- CMS with feature flags
- Bilingual AR/EN with RTL/LTR
- Electronic instructor agreement
- AI Simulators, Interactive Labs, AI Tutor, AI Grading, AI Feedback, AI Recommendations
- Community/Forums, Live Sessions, Webinars
- Leaderboard, Gamification, Badges, Challenges, Coupons
- Advanced reports and analytics

### Out of Scope
- Native mobile app (web is responsive)
- Additional languages beyond AR/EN at launch (architecture supports later)
- Third-party external marketplace integrations

### Assumptions
- Cloud-native infrastructure (Kubernetes-ready) is available.
- A commercial DRM provider (e.g., Widevine/PlayReady/FairPlay) can be licensed.
- Payment gateway(s) supporting the target regions are available.
- Instructors own or are licensed for the content they upload.

### Constraints
- No content protection guarantees 100% prevention of screen recording on internet-connected devices; the design maximizes difficulty, not absolute prevention.
- The v1 feature set is unusually large; timeline and phasing reflect a realistic multi-quarter build.

### Dependencies
- Third-party DRM/licensing provider
- Payment gateway provider
- AI/LLM provider for tutor, grading, and recommendation features
- CDN and distributed storage provider

---

## 5. Users & Personas

### Primary Users
Learners who use the platform weekly to purchase and follow courses, run simulators and labs, and earn certificates.

### Secondary Users
Course Providers/Instructors who author and publish protected content and track learner performance; platform staff (Owner, Administrator, Supervisor) who govern the platform.

### User Roles & Permissions

| Role | Access Level | Key Permissions |
|------|-------------|-----------------|
| Platform Owner | Full | Full control over all courses, users, subscriptions, pricing, commissions, payments, reports, platform settings, CMS, AI, categories, certificates, assessments, languages, permissions, and feature flags |
| Platform Administrator | High | All operational controls except ownership-level settings (billing ownership, permission-scheme definition, tenant provisioning) |
| Platform Supervisor | Medium (customizable) | Review/approve/reject courses, moderate community, monitor users; no pricing/commission/settings control unless granted |
| Course Provider / Instructor | Scoped to own courses | Create/edit own courses, upload video/files, build quizzes/assignments/question banks, issue course certificates, track own learners, view own analytics, answer questions, moderate own course forum, create coupons/bundles/offers, host live sessions/webinars, manage own reviews |
| Teaching Assistant | Delegated (scoped) | Grade, answer questions, and moderate within assigned courses; no publishing, pricing, or payout control |
| Learner | Own account only | Enroll, purchase, consume protected content, take assessments, use AI tools/labs/simulators, earn certificates, participate in community, view own progress |

Instructors explicitly cannot control: platform-wide pricing/commission rules, other instructors' courses, user management beyond their own learners, platform settings, CMS, feature flags, or payout policy — these are platform-administration only.

### Personas

**Persona 1 — Primary**
- Name: Layla (Learner)
- Role: Learner
- Goal: Complete high-quality interactive courses in Arabic or English and earn a recognized certificate.
- Pain Point: Existing platforms are shallow, poorly localized for Arabic, or serve untrusted/unprotected content.
- Tech Level: Medium
- Frequency: Weekly
- Success: Purchases a course, completes it with passing assessments, and downloads a verifiable certificate.

**Persona 2 — Secondary**
- Name: Kareem (Instructor / Course Provider)
- Role: Course Provider
- Goal: Publish protected courses, reach paying learners, and earn fair commissions.
- Pain Point: Fear of content theft and unclear/unfair payout terms on other platforms.
- Tech Level: Medium to High
- Frequency: Weekly
- Success: Publishes a protected course, tracks learner analytics, and receives correct commission payouts.

**Persona 3 — Governance**
- Name: Nour (Platform Administrator)
- Role: Administrator
- Goal: Keep the platform healthy — approve quality courses, manage users, monitor revenue.
- Pain Point: No single console to govern courses, users, payments, and features.
- Tech Level: High
- Frequency: Daily
- Success: Reviews/approves courses, toggles features via CMS, and reads platform-wide reports without engineering help.

---

## 6. MoSCoW Feature Prioritization

### Must Have — P0

| ID | Feature | Status | Description | Assigned To | Sprint |
|----|---------|--------|-------------|-------------|--------|
| P0-F001 | Authentication + MFA | TODO | Email/social sign-in, JWT with refresh rotation, MFA | Backend Dev | S1 |
| P0-F002 | RBAC (6 roles) | TODO | Role/permission enforcement across all endpoints | Backend Dev | S1 |
| P0-F003 | Multi-Tenant Isolation | TODO | Tenant-scoped data, routing, and configuration | Backend Dev | S1 |
| P0-F004 | Course Authoring & Publishing | TODO | Create courses, upload video/files, submit for approval, publish | Backend Dev | S2 |
| P0-F005 | Content Protection | TODO | DRM, signed short-lived URLs, dynamic watermark, anti-download/hotlink | DevOps Engineer | S2 |
| P0-F006 | Payments & Commissions | TODO | Purchase, subscription, payout/commission settlement | Backend Dev | S3 |
| P0-F007 | Progress Tracking | TODO | Per-learner lesson/course completion state | Backend Dev | S3 |
| P0-F008 | Certificates | TODO | Auto-issued, verifiable, encrypted certificates | Backend Dev | S3 |
| P0-F009 | Assessments / Quizzes | TODO | Question banks, quizzes, pass/fail scoring | Backend Dev | S3 |
| P0-F010 | CMS + Feature Flags | TODO | Toggle platform features without code changes | Frontend Dev | S2 |
| P0-F011 | Bilingual AR/EN (RTL/LTR) | TODO | Localized UI, content, notifications; RTL/LTR layouts | Frontend Dev | S1 |
| P0-F012 | Instructor Agreement | TODO | Electronic acceptance gate before publishing | Backend Dev | S2 |

### Should Have — P1

| ID | Feature | Status | Description | Assigned To | Sprint |
|----|---------|--------|-------------|-------------|--------|
| P1-F001 | AI Simulators | TODO | Scenario-based AI-driven practice modules | ML/AI Engineer | S5 |
| P1-F002 | Interactive Labs | TODO | Hands-on sandboxed practice environments | ML/AI Engineer | S5 |
| P1-F003 | AI Tutor | TODO | Conversational per-course learning assistant | ML/AI Engineer | S5 |
| P1-F004 | AI Grading | TODO | Automated grading of open-ended submissions | ML/AI Engineer | S6 |
| P1-F005 | AI Feedback | TODO | Personalized learner feedback generation | ML/AI Engineer | S6 |
| P1-F006 | AI Recommendations | TODO | Course/path recommendations per learner | ML/AI Engineer | S6 |
| P1-F007 | Community / Forums | TODO | Course and platform discussion spaces | Backend Dev | S4 |
| P1-F008 | Live Sessions | TODO | Scheduled live instructor sessions | Backend Dev | S6 |
| P1-F009 | Webinars | TODO | Broadcast webinar events | Backend Dev | S6 |
| P1-F010 | Leaderboard | TODO | Ranked learner standings | Frontend Dev | S4 |
| P1-F011 | Gamification | TODO | Points, streaks, progression | Frontend Dev | S4 |
| P1-F012 | Badges | TODO | Achievement badges | Frontend Dev | S4 |
| P1-F013 | Challenges | TODO | Time-bound learning challenges | Frontend Dev | S4 |
| P1-F014 | Coupons | TODO | Instructor/platform discount codes | Backend Dev | S3 |
| P1-F015 | Advanced Reports & Analytics | TODO | Revenue, engagement, and course analytics | Backend Dev | S4 |

### Could Have — P2

| ID | Feature | Status | Description | Assigned To | Sprint |
|----|---------|--------|-------------|-------------|--------|
| P2-F001 | Affiliate System | TODO | Affiliate tracking and payouts | Backend Dev | S7 |
| P2-F002 | Referral System | TODO | Learner referral rewards | Backend Dev | S7 |
| P2-F003 | Extended Marketplace | TODO | Bundles and broader discovery | Frontend Dev | S7 |
| P2-F004 | Dark Mode | TODO | Theme toggle | Frontend Dev | S7 |
| P2-F005 | Keyboard Shortcuts | TODO | Power-user navigation | Frontend Dev | S7 |
| P2-F006 | Bulk Actions | TODO | Admin bulk operations | Frontend Dev | S7 |

### Won't Have — P3

| ID | Feature | Status | Description | Assigned To | Sprint |
|----|---------|--------|-------------|-------------|--------|
| P3-F001 | Native Mobile App | SKIPPED | Deferred to v2; web is responsive | — | — |
| P3-F002 | Languages beyond AR/EN | SKIPPED | Architecture supports later addition | — | — |
| P3-F003 | External Marketplace Integrations | SKIPPED | Third-party integrations deferred | — | — |

---

## 7. Functional Requirements

### P0-F001 — Authentication + MFA
**Description:** Secure sign-in with JWT (refresh-token rotation) and MFA.
**User Story:** As any user, I want to sign in securely with MFA so that my account and tenant data are protected.
**Trigger:** User submits credentials on the login screen.
**Pre-conditions:** User account exists and is active within a tenant.
**Post-conditions:** Authenticated session with scoped access token issued.
**Main Flow:**
1. User enters email and password.
2. System validates credentials.
3. System prompts for MFA code.
4. User submits MFA code.
5. System validates code and issues access + refresh tokens.
6. User is routed to their role-based dashboard.
**Alternate Flows:**
- A1: Invalid credentials → system rejects and shows an inline error.
- A2: MFA code invalid/expired → system prompts to retry or resend.
**Acceptance Criteria:**
- [ ] Valid credentials + valid MFA grant a scoped session.
- [ ] Invalid credentials never issue a token.
- [ ] Refresh tokens rotate and old tokens are invalidated.
- [ ] All auth attempts are recorded in audit logs.

### P0-F002 — RBAC (6 Roles)
**Description:** Enforce role/permission checks on every action.
**User Story:** As a platform owner, I want each role restricted to its permitted actions so that access follows least privilege.
**Trigger:** Any authenticated request to a protected resource.
**Pre-conditions:** User has an assigned role within a tenant.
**Post-conditions:** Action is allowed or denied per the permission matrix.
**Main Flow:**
1. Request arrives with an access token.
2. System resolves role and tenant.
3. System checks the permission matrix for the requested action.
4. If permitted, action proceeds; otherwise it is denied.
**Alternate Flows:**
- A1: Insufficient permission → 403 with a clear message.
- A2: Cross-tenant access attempt → denied and logged as suspicious.
**Acceptance Criteria:**
- [ ] Each of the six roles can perform only its permitted actions.
- [ ] Instructors cannot access other instructors' courses.
- [ ] Every denied action is logged.

### P0-F003 — Multi-Tenant Isolation
**Description:** Isolate data and configuration per tenant.
**User Story:** As a platform administrator, I want tenants isolated so that no tenant can read or affect another's data.
**Trigger:** Any tenant-scoped request.
**Pre-conditions:** Request carries a resolved tenant context.
**Post-conditions:** Only the tenant's data is accessible.
**Main Flow:**
1. Request resolves tenant from token/subdomain.
2. System scopes all queries to that tenant.
3. Response contains only tenant-owned data.
**Alternate Flows:**
- A1: Missing tenant context → request rejected.
- A2: Tenant mismatch → denied and logged.
**Acceptance Criteria:**
- [ ] Queries are always tenant-scoped.
- [ ] Cross-tenant reads/writes are impossible.

### P0-F004 — Course Authoring & Publishing
**Description:** Instructors create courses, upload media, and publish after approval.
**User Story:** As an instructor, I want to build and publish a course so that learners can enroll.
**Trigger:** Instructor selects "Create Course".
**Pre-conditions:** Instructor has accepted the instructor agreement.
**Post-conditions:** Course is in Draft, Pending Review, or Published state.
**Main Flow:**
1. Instructor creates a course and adds sections/lessons.
2. Instructor uploads videos and files.
3. Instructor attaches quizzes and a certificate template.
4. Instructor submits for review.
5. Supervisor/Admin approves.
6. Course is published and discoverable.
**Alternate Flows:**
- A1: Upload fails (network) → system retries and preserves draft.
- A2: Review rejected → course returns to Draft with reviewer notes.
**Acceptance Criteria:**
- [ ] Draft state persists partial content across sessions.
- [ ] Publishing requires an approval.
- [ ] Published courses expose only protected media URLs.

### P0-F005 — Content Protection
**Description:** Protect video/files via DRM, signed short-lived URLs, dynamic watermark, and anti-download/hotlink measures.
**User Story:** As an instructor, I want my content protected so that it cannot be easily downloaded or redistributed.
**Trigger:** Learner requests to view protected content.
**Pre-conditions:** Learner is enrolled and authorized.
**Post-conditions:** Content is delivered through a protected, watermarked, time-limited channel.
**Main Flow:**
1. Learner opens a lesson.
2. System verifies enrollment and issues a short-lived signed URL.
3. Player loads DRM-protected stream.
4. Dynamic watermark with learner identity is overlaid during playback.
5. Access event is logged.
**Alternate Flows:**
- A1: Unauthorized/expired URL → access denied.
- A2: Suspicious access pattern detected → account can be auto-suspended.
**Acceptance Criteria:**
- [ ] Direct file/download URLs are never exposed.
- [ ] Signed URLs expire within a short TTL.
- [ ] Watermark carries learner-identifying data during playback.
- [ ] Hotlinking is blocked.
- [ ] All access attempts are logged.

*Note: No protection guarantees 100% prevention of screen recording on connected devices; controls maximize difficulty.*

### P0-F006 — Payments & Commissions
**Description:** Process purchases/subscriptions and settle instructor commissions.
**User Story:** As a learner, I want to pay for a course so that I gain access; as an instructor, I want correct commission payouts.
**Trigger:** Learner confirms a purchase or subscription.
**Pre-conditions:** Valid payment method; course is published.
**Post-conditions:** Payment recorded; enrollment granted; commission accrued.
**Main Flow:**
1. Learner selects a course/plan and proceeds to checkout.
2. System applies any valid coupon.
3. Payment gateway processes the charge.
4. System grants enrollment and records the transaction.
5. System accrues the instructor commission per platform rules.
**Alternate Flows:**
- A1: Payment declined → enrollment not granted; learner notified.
- A2: Duplicate charge attempt → system detects and prevents double billing.
- A3: Refund requested → processed per refund policy; access revoked.
**Acceptance Criteria:**
- [ ] Successful payment grants immediate access.
- [ ] Failed payment grants no access.
- [ ] Commissions are computed and recorded correctly.
- [ ] Duplicate charges are prevented.

### P0-F007 — Progress Tracking
**Description:** Track lesson and course completion per learner.
**User Story:** As a learner, I want my progress saved so that I can resume where I stopped.
**Trigger:** Learner completes or resumes a lesson.
**Pre-conditions:** Learner is enrolled.
**Post-conditions:** Progress state is persisted.
**Main Flow:**
1. Learner completes a lesson.
2. System marks the lesson complete and updates course percentage.
3. On return, learner resumes at the last position.
**Alternate Flows:**
- A1: No progress yet (empty state) → shows a start prompt.
- A2: Sync failure → retried; state preserved locally until confirmed.
**Acceptance Criteria:**
- [ ] Completion percentage is accurate.
- [ ] Resume returns to the correct lesson.

### P0-F008 — Certificates
**Description:** Issue verifiable, encrypted certificates on course completion.
**User Story:** As a learner, I want a verifiable certificate so that I can prove completion.
**Trigger:** Learner meets completion and passing criteria.
**Pre-conditions:** Course complete and assessments passed.
**Post-conditions:** Encrypted, verifiable certificate issued.
**Main Flow:**
1. System detects completion + passing score.
2. System generates the certificate from the course template.
3. Certificate is stored encrypted and made downloadable/verifiable.
**Alternate Flows:**
- A1: Criteria not met → certificate withheld with reason.
**Acceptance Criteria:**
- [ ] Certificate issues only when criteria are met.
- [ ] Certificate is verifiable via a unique identifier.
- [ ] Certificate is stored encrypted.

### P0-F009 — Assessments / Quizzes
**Description:** Question banks, quizzes, and pass/fail scoring.
**User Story:** As an instructor, I want to assess learners so that certificates reflect real mastery.
**Trigger:** Learner starts a quiz.
**Pre-conditions:** Quiz is published within an enrolled course.
**Post-conditions:** Score recorded; pass/fail determined.
**Main Flow:**
1. Learner starts the quiz.
2. Learner answers questions.
3. System scores and records the result.
4. Result feeds progress and certificate eligibility.
**Alternate Flows:**
- A1: Invalid/blank submission → validation prompt.
- A2: Timeout → submission auto-finalized.
**Acceptance Criteria:**
- [ ] Scoring is accurate and recorded.
- [ ] Pass/fail thresholds are enforced.

### P0-F010 — CMS + Feature Flags
**Description:** Toggle platform features without code changes.
**User Story:** As an administrator, I want to enable/disable features from the CMS so that rollout is controlled without deployments.
**Trigger:** Admin toggles a feature.
**Pre-conditions:** Admin has feature-management permission.
**Post-conditions:** Feature availability updates platform-wide.
**Main Flow:**
1. Admin opens the feature panel.
2. Admin toggles a feature on/off.
3. System applies the change without a deploy.
**Alternate Flows:**
- A1: Toggle without permission → denied.
**Acceptance Criteria:**
- [ ] Toggling requires no code change.
- [ ] Disabled features are hidden across the platform.

### P0-F011 — Bilingual AR/EN (RTL/LTR)
**Description:** Full Arabic/English UI, content, and notifications with RTL/LTR.
**User Story:** As an Arabic-speaking user, I want a fully localized RTL experience so that the platform feels native.
**Trigger:** User selects or is detected in a language.
**Pre-conditions:** Localization resources exist.
**Post-conditions:** UI, notifications, and messages render in the chosen language and direction.
**Main Flow:**
1. User selects a language.
2. System applies localized strings and RTL/LTR layout.
3. Notifications and messages use the chosen language.
**Alternate Flows:**
- A1: Missing translation key → falls back to English and logs the gap.
**Acceptance Criteria:**
- [ ] All UI text is localized (no hardcoded strings).
- [ ] RTL and LTR layouts render correctly.
- [ ] Notifications are language-aware.

### P0-F012 — Instructor Agreement
**Description:** Electronic acceptance of the instructor agreement before publishing.
**User Story:** As the platform, I want instructors to accept terms electronically so that IP, commission, and content policies are binding before any course goes live.
**Trigger:** Instructor attempts to publish a first course.
**Pre-conditions:** Instructor role assigned.
**Post-conditions:** Acceptance recorded with timestamp and version.
**Main Flow:**
1. System presents the agreement.
2. Instructor reviews and accepts electronically.
3. System records acceptance and unlocks publishing.
**Alternate Flows:**
- A1: Declined → publishing remains locked.
**Acceptance Criteria:**
- [ ] Publishing is blocked until acceptance.
- [ ] Acceptance is stored with version and timestamp.

*(P1 features follow the same functional-requirement structure and are elaborated at the start of their respective phases.)*

---

## 8. Non-Functional Requirements

**Performance:** Page load < 2s; API responses < 500ms (p95); video start (protected stream) < 3s.
**Security:** Auth + MFA on all sensitive actions; RBAC + least privilege; input validation; AES-256 at rest; TLS 1.3 in transit; encrypted databases, files, videos, certificates, and user data; WAF; rate limiting; anti-bot; OWASP Top 10 compliance; Zero-Trust posture; SIEM integration; audit logs.
**Availability:** 99.9% uptime; High Availability with multi-zone deployment.
**Scalability:** Microservices + multi-tenant, cloud-native, Kubernetes-ready; horizontal + auto-scaling; distributed storage/cache; queue systems; event-driven architecture; CDN. Launch target: low initial traffic (< 5,000 monthly active users) with architecture designed to scale 10x+ toward millions of users, thousands of courses, and thousands of providers without a rewrite.
**Accessibility:** WCAG 2.1 AA.
**Compatibility:** Chrome 100+, Safari 15+, Firefox 100+; responsive web.
**Data & Compliance:** GDPR-aligned data handling; daily backups with 30-day retention; disaster recovery plan; content-access audit trail.
**Observability:** Structured JSON logging; error-rate > 1% triggers alerting; access and security-event monitoring.

---

## 9. Technical Architecture

**Frontend:** React 18 + TypeScript + Tailwind CSS; i18n with RTL/LTR support; DRM-capable video player.
**Backend:** Node.js + NestJS + TypeScript, organized as microservices (auth, tenancy, courses, media, payments, assessments, certificates, AI, community, notifications).
**Database:** PostgreSQL (primary, tenant-scoped) + Redis (cache/sessions/queues); distributed object storage for media; per-tenant data isolation.
**Auth & Authorization:** JWT with refresh-token rotation; MFA; RBAC permission matrix; least privilege; Zero-Trust service-to-service auth.
**Infrastructure & Deployment:** Kubernetes; CDN for static and protected media delivery; auto-scaling; CI/CD via GitHub Actions; multi-zone HA; daily backups; SIEM/WAF integration.
**External Integrations:** DRM provider (Widevine/PlayReady/FairPlay), payment gateway, AI/LLM provider, email/notification provider, live-streaming provider (for P1 live sessions/webinars).

---

## 10. Implementation Phases

### Phase 1 — Foundation (4 weeks)
**Goal:** Secure, multi-tenant, bilingual core with authentication.
- [ ] Auth + MFA (P0-F001)
- [ ] RBAC six roles (P0-F002)
- [ ] Multi-tenant isolation (P0-F003)
- [ ] Bilingual AR/EN + RTL/LTR shell (P0-F011)
- [ ] CI/CD, base infrastructure, observability
**Validation:** A user can register, sign in with MFA, and access a role-scoped, localized dashboard within an isolated tenant.

### Phase 2 — Core Course Experience (5 weeks)
**Goal:** Instructors publish protected courses; CMS controls features.
- [ ] Course authoring & publishing (P0-F004)
- [ ] Content protection: DRM, signed URLs, watermark (P0-F005)
- [ ] CMS + feature flags (P0-F010)
- [ ] Instructor agreement (P0-F012)
**Validation:** An instructor accepts the agreement, publishes a protected course, and a learner streams it via a watermarked, time-limited URL.

### Phase 3 — Commerce, Assessment & Certification (5 weeks)
**Goal:** Monetization and completion loop.
- [ ] Payments & commissions (P0-F006)
- [ ] Coupons (P1-F014)
- [ ] Progress tracking (P0-F007)
- [ ] Assessments / quizzes (P0-F009)
- [ ] Certificates (P0-F008)
**Validation:** A learner purchases a course, completes it, passes assessments, and receives a verifiable certificate with commission settled.

### Phase 4 — Engagement, AI & Launch Hardening (6+ weeks)
**Goal:** Add AI, community, and live features; harden for launch.
- [ ] AI Tutor / Simulators / Labs (P1-F001..F003)
- [ ] AI Grading / Feedback / Recommendations (P1-F004..F006)
- [ ] Community, Leaderboard, Gamification, Badges, Challenges (P1-F007, F010..F013)
- [ ] Live Sessions & Webinars (P1-F008, F009)
- [ ] Advanced reports & analytics (P1-F015)
- [ ] Security, load, and DR testing
**Validation:** Engagement/AI features pass functional tests, security review clears OWASP checks, and the platform sustains a 10x load test.

---

## 11. Advanced Execution Detail

### User Flow (Learner — Purchase to Certificate)
1. Learner lands on the platform and selects a language (AR/EN).
2. Learner registers and verifies via MFA.
3. Learner browses the catalog and opens a course page.
4. Learner applies a coupon (optional) and completes payment.
5. System grants enrollment and opens the course player.
6. Learner watches DRM-protected, watermarked lessons; progress is saved per lesson.
7. Learner takes quizzes; system scores and updates eligibility.
8. On completion + passing, system issues a verifiable certificate.
9. Learner downloads/verifies the certificate and receives a completion notification.

### Edge Cases (Condition → System Behavior → User Feedback)
- Invalid input on checkout/quiz → request rejected → inline field error shown.
- No enrolled courses (empty state) → dashboard shows onboarding prompt → "Browse courses" CTA displayed.
- Network/API failure during upload or playback → retry with backoff, state preserved → "Connection issue, retrying…" banner.
- Unauthorized/cross-tenant access → request denied and logged → 403 "You don't have access" message.
- Duplicate payment/enrollment → transaction blocked → "You already own this course" message.
- Expired signed media URL → access denied, new URL requested → seamless re-authorization or "Session expired, reloading" notice.

### API Design (High Level, `/api/v1/`, REST)
- `POST /auth/login`, `POST /auth/mfa/verify`, `POST /auth/refresh`
- `GET /tenants/:id`, `GET /me`
- `GET /courses`, `POST /courses`, `PUT /courses/:id`, `POST /courses/:id/publish`
- `POST /courses/:id/media` (signed upload), `GET /lessons/:id/stream` (signed URL)
- `POST /enrollments`, `GET /enrollments/:id/progress`, `PUT /lessons/:id/progress`
- `POST /payments/checkout`, `POST /payments/webhook`, `GET /commissions`
- `POST /coupons`, `POST /assessments/:id/submit`
- `GET /certificates/:id`, `GET /certificates/verify/:code`
- `GET /admin/features`, `PUT /admin/features/:key` (feature flags)
- `POST /agreements/accept`

### Data Model (Core Entities)
- **Tenant:** id, name, domain, settings, status
- **User:** id, tenant_id, email, password_hash, role, mfa_enabled, locale
- **Course:** id, tenant_id, instructor_id, title, status, price, language
- **Lesson:** id, course_id, title, media_ref, order
- **Enrollment:** id, user_id, course_id, progress_pct, status
- **Payment:** id, user_id, course_id, amount, status, commission_amount, coupon_id
- **Assessment:** id, course_id, questions_ref, pass_threshold
- **Certificate:** id, user_id, course_id, verify_code, issued_at
- **Agreement:** id, instructor_id, version, accepted_at
- **FeatureFlag:** id, tenant_id, key, enabled
- Relationships: Tenant 1—* User/Course; Course 1—* Lesson/Assessment; User 1—* Enrollment/Payment/Certificate.

### Build Order
- Phase 1: Auth + MFA, RBAC, tenancy, localization shell.
- Phase 2: Course authoring, content protection, CMS.
- Phase 3: Payments, progress, assessments, certificates.
- Phase 4: AI, community, live features, hardening.

### UX Rules (Applied System-Wide)
- All forms validate instantly with inline errors.
- Loading states shown on every asynchronous action.
- Empty states provide a clear next action.
- Success feedback is shown after every save/purchase/submission.
- Language and direction (RTL/LTR) are respected on every screen.

---

## 12. Success Metrics and KPIs

| Category | Metric | Target | Measurement Method |
|----------|--------|--------|--------------------|
| Business | Learner activation rate | > 60% | % of registrants who enroll in ≥1 course within 7 days (analytics) |
| Business | Paid conversion | > 8% | % of active learners who purchase (payments data) |
| Product | Course completion rate | > 50% | Completed / enrolled (progress data) |
| Product | Task completion (checkout, quiz) | > 80% | Funnel completion (event tracking) |
| Technical | API response time | < 500ms (p95) | APM monitoring |
| Technical | Error rate | < 0.1% | Structured logs + alerting |
| Technical | Uptime | ≥ 99.9% | Monitoring dashboard |
| Satisfaction | Learner CSAT | ≥ 4.2 / 5 | Post-course survey |

**Tracking Tool:** PostHog or Mixpanel. **Review Frequency:** 1 week, 2 weeks, and 30 days post-launch. **Owner:** Dr. Ahmed Shahin.

---

## 13. Timeline and Milestones

**Start Date:** 2026-08-06 · **Target Launch:** 2026-12-31 · **Total Duration:** ~20 weeks.

| Milestone | Description | Due Date | Status | Owner |
|-----------|-------------|----------|--------|-------|
| Kickoff | Project start, environment setup | 2026-08-06 | TODO | Dr. Ahmed Shahin |
| PRD Approved | PRD signed off | 2026-08-13 | TODO | Dr. Ahmed Shahin |
| Phase 1 Done | Foundation complete | 2026-09-10 | TODO | Backend Dev |
| Phase 2 Done | Core course experience complete | 2026-10-15 | TODO | Backend Dev |
| Phase 3 Done | Commerce & certification complete | 2026-11-19 | TODO | Backend Dev |
| Phase 4 Done | AI, community & hardening complete | 2026-12-24 | TODO | ML/AI Engineer |
| Beta Launch | Limited-audience beta | 2026-12-24 | TODO | Dr. Ahmed Shahin |
| Public Launch | General availability | 2026-12-31 | TODO | Dr. Ahmed Shahin |

---

## 14. Risk Register

Score = Likelihood × Impact (High=3, Medium=2, Low=1).

| ID | Description | Likelihood | Impact | Score | Mitigation | Owner |
|----|-------------|-----------|--------|-------|------------|-------|
| R1 | Scope too large for v1 timeline (all features in v1) | High (3) | High (3) | 9 | Enforce phase gating; MoSCoW discipline; ship P0 first | Dr. Ahmed Shahin |
| R2 | Content protection insufficient / DRM integration complexity | Medium (2) | High (3) | 6 | Spike DRM in Phase 2; layered protection; document limits | DevOps Engineer |
| R3 | Multi-tenant data leakage | Low (1) | High (3) | 3 | Tenant-scoped queries; isolation tests; audits | Backend Dev |
| R4 | Payment/commission errors | Medium (2) | High (3) | 6 | Idempotent transactions; reconciliation; test coverage | Backend Dev |
| R5 | AI feature quality/cost unpredictability | Medium (2) | Medium (2) | 4 | Feature-flag AI; evaluate before GA; usage limits | ML/AI Engineer |
| R6 | Key-person dependency | Medium (2) | Medium (2) | 4 | Document everything; cross-train; code review | Dr. Ahmed Shahin |

**External Dependencies:** Third-party DRM/API availability, payment gateway readiness, AI/LLM provider availability, design-asset readiness, stakeholder availability for reviews.

---

## 15. Stakeholders and Approvals

| Name | Role | Involvement | Contact |
|------|------|-------------|---------|
| Dr. Ahmed Shahin | Product Owner / PM | Accountable; final approver | [TBD] |
| Engineering Lead | Technical Lead | Architecture & delivery approval | [TBD] |
| Design Lead | UX/UI | Design approval | [TBD] |
| Security Lead | Security | Security sign-off | [TBD] |

| Gate | Approver | Required By | Status |
|------|----------|-------------|--------|
| PRD Approval | Product Owner | 2026-08-13 | Pending |
| Architecture Sign-off | Engineering Lead | 2026-08-20 | Pending |
| Security Review | Security Lead | 2026-12-17 | Pending |
| Launch Approval | Product Owner + Engineering Lead | 2026-12-30 | Pending |

---

## 16. References and Links

| Item | Link |
|------|------|
| Design Files | [TBD] |
| Repository | [TBD] |
| API Docs | [TBD] |
| Architecture Diagrams | [TBD] |
| Staging Environment | [TBD] |
| Production Environment | [TBD] |
| CI/CD Pipeline | [TBD] |
| Monitoring Dashboard | [TBD] |
| Related PRDs | [TBD] |
| Slack Channel | [TBD] |
| Meeting Notes | [TBD] |

---

## 17. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-08-06 | Dr. Ahmed Shahin | Initial PRD created |
