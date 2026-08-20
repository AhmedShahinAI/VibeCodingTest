# Arabic Training Platform

An Arabic-first marketing website for a professional training organization.
Arabic RTL layout, fully responsive, SEO optimized.

Tech stack: Nuxt 3, Vue 3, TypeScript, Tailwind CSS, Express, PostgreSQL

---

## Phase 1: Setup

**Goal**: Initialize the monorepo and shared infrastructure.

- pnpm workspace with apps/web (Nuxt 3) and apps/api (Express)
- Shared packages: types, validation, shared utilities
- Base RTL layout via layouts/default.vue with dir="rtl"

---

## Phase 2: User Story 1 — Course Discovery

**Goal**: Public visitors can browse all courses and view course detail pages.

US1 — Course Discovery & Lead Capture (Priority: P1)

### Frontend — US1

- Create courses listing page at apps/web/pages/courses/index.vue
- Create course detail page at apps/web/pages/courses/[slug].vue
- Create homepage at apps/web/pages/index.vue

### Backend — US1

- Implement courses API at apps/api/src/modules/courses/
- GET /api/v1/courses endpoint
- GET /api/v1/courses/:slug endpoint
