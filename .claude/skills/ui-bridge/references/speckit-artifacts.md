# Reference: Spec Kit Artifacts

How to find, read, and extract data from Spec Kit files.

---

## 1. Where Spec Kit Stores Files

| File | Primary location | Fallback |
|------|-----------------|---------|
| `plan.md` | `specs/[NNN-feature]/plan.md` | root `plan.md` |
| `tasks.md` | `specs/[NNN-feature]/tasks.md` | root `tasks.md` |
| `spec.md` | `specs/[NNN-feature]/spec.md` | — |
| `data-model.md` | `specs/[NNN-feature]/data-model.md` | — |
| `contracts/auth.md` | `specs/[NNN-feature]/contracts/auth.md` | — |
| `contracts/public.md` | `specs/[NNN-feature]/contracts/public.md` | — |
| `contracts/admin.md` | `specs/[NNN-feature]/contracts/admin.md` | — |
| `constitution.md` | `.specify/memory/constitution.md` | — |
| `feature.json` | `.specify/feature.json` | — |

### Reading `feature.json`

```json
{ "feature_directory": "specs/001-my-feature" }
```

Use this to locate the active feature directory. All other files are relative to it.

---

## 2. Parsing plan.md

### Phase headings

```regex
^##\s+Phase\s+\S+[^\n]*
```

Example matches:
- `## Phase 1: Setup (Monorepo Initialization)`
- `## Phase 2: Foundational (Blocking Prerequisites)`
- `## Phase 3: User Story 1 — Course Discovery`

### User stories

```regex
US\d+[^):\n]*
```

Example: `US1 — Course Discovery & Lead Capture (Priority: P1)`

### Tech stack signals

Look for: `Nuxt`, `Vue`, `React`, `Next.js`, `Express`, `FastAPI`, `Django`, `Tailwind`,
`TypeScript`, `Prisma`, `PostgreSQL`, `MongoDB`, `Redis`

### Direction / language signals

```regex
dir="rtl"|RTL|Arabic|عربي|lang.*ar
```

---

## 3. Parsing tasks.md

### Task checkbox format

```
- [ ] T043 [US1] Create courses list page at apps/web/pages/courses/index.vue
- [x] T001 Create pnpm-workspace.yaml at repo root
```

Regex: `^- \[[ x]\]\s+(T\d+.*)$`

### Task ID
`T\d+` at the start of the task content

### Parallelizable tag
`\[P\]` — this task can run in parallel with others

### User story tag
`\[US\d+\]` — maps to a user story from spec.md

### File path extraction

Page files:
```regex
pages/[^\s`'"]+\.(?:vue|tsx|jsx|html)
```

Component files:
```regex
components/[^\s`'"]+\.(?:vue|tsx|jsx)
```

API route files:
```regex
(?:modules|routes)/[^\s`'"]+\.(?:ts|js)
```

---

## 4. Extracting Pages from Task Descriptions

| Pattern in task description | Resulting page |
|---|---|
| `pages/index.vue` | Homepage → `index.html` |
| `pages/courses/index.vue` | Courses list → `courses.html` |
| `pages/courses/[slug].vue` | Course detail → `courses-detail.html` |
| `pages/experts/index.vue` | Experts list → `experts.html` |
| `pages/experts/[slug].vue` | Expert detail → `experts-detail.html` |
| `pages/admin/index.vue` | Admin dashboard → `admin-dashboard.html` |
| `pages/admin/login.vue` | Admin login → `admin-login.html` |
| `pages/admin/courses/index.vue` | Admin courses → `admin-courses.html` |
| `pages/admin/courses/[id].vue` | Admin course form → `admin-courses-detail.html` |

---

## 5. Example plan.md Excerpt (Annotated)

```markdown
# EdTech Marketing & CRM Website               ← PROJECT NAME
                                                ← extract this
## Phase 3: User Story 1                        ← PHASE HEADING
                                                ← extract phase list
### Frontend — US1

- [ ] T043 [US1] Create courses list page at   ← PAGE TASK
  apps/web/pages/courses/index.vue              ← extract page path
  
- [ ] T044 [US1] Create course detail page at  ← PAGE TASK
  apps/web/pages/courses/[slug].vue             ← extract page path
```

---

## 6. Example tasks.md Excerpt (Annotated)

```markdown
## Phase 3: User Story 1 — Course Discovery    ← PHASE BOUNDARY

- [ ] T036 [P] [US1] Implement courses service ← [P] = parallel, [US1] = story
  at apps/api/src/modules/courses/...           ← API task, not a page

- [ ] T043 [US1] Create courses list page       ← PAGE TASK (no [P] = sequential)
  at apps/web/pages/courses/index.vue           ← extract this path

- [ ] T044 [US1] Create course detail page     ← Another page task
  at apps/web/pages/courses/[slug].vue         ← extract this path
```

Extraction rule: any task line containing `pages/` followed by a `.vue|.tsx|.jsx|.html`
path is a frontend page task and should generate a corresponding HTML prototype.
