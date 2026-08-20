import { UserRole } from '@elm/shared';

/**
 * Representative permission catalog for Phase 1. Course/payment/community
 * services land in later PRD phases, so several keys here are placeholders
 * for capabilities described in PRD Section 5's role table (e.g.
 * `course.manage_own`) rather than backed by a live service yet — they
 * exist so RBAC enforcement (spec FR-010 through FR-014) is provable now,
 * and later services attach their own real permission keys to this same
 * matrix rather than inventing a parallel mechanism.
 */
export const ALL_PERMISSION_KEYS = [
  // Platform Owner only (spec FR-013 — ownership-level, never delegable)
  'tenant.provision',
  'billing.manage_ownership',
  'permission_scheme.define',
  // Platform Owner + Administrator
  'tenant.manage_settings',
  'user.manage_all',
  'course.review_approve',
  'community.moderate_all',
  // Platform Supervisor default (customizable per spec FR-014)
  'course.review_flagged',
  // Course Provider / Instructor (scoped to their own courses)
  'course.manage_own',
  'community.moderate_own',
  // Teaching Assistant (delegated, scoped to assigned courses)
  'course.grade_assigned',
  'course.answer_questions_assigned',
  // Learner
  'course.enroll',
  'community.participate',
] as const;

export type PermissionKey = (typeof ALL_PERMISSION_KEYS)[number];

const OWNER_ONLY: PermissionKey[] = ['tenant.provision', 'billing.manage_ownership', 'permission_scheme.define'];
const OWNER_AND_ADMIN_SHARED: PermissionKey[] = [
  'tenant.manage_settings',
  'user.manage_all',
  'course.review_approve',
  'community.moderate_all',
];

/** Default per-role grants, per PRD Section 5's role/permission table. */
export const DEFAULT_PERMISSION_MATRIX: Record<UserRole, PermissionKey[]> = {
  platform_owner: [...OWNER_ONLY, ...OWNER_AND_ADMIN_SHARED],
  platform_administrator: [...OWNER_AND_ADMIN_SHARED],
  platform_supervisor: ['course.review_flagged', 'community.moderate_all'],
  course_provider: ['course.manage_own', 'community.moderate_own'],
  teaching_assistant: ['course.grade_assigned', 'course.answer_questions_assigned'],
  learner: ['course.enroll', 'community.participate'],
};
