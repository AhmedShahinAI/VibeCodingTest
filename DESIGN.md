# Design System: SimpleElm (سيمبل إلم)

Brand direction: **SimpleElm** — approved directly from user-supplied brand identity sheets
(`.ui-bridge/brand-intake.v3.json`). Friendly, modern, AI-forward, confident but approachable:
"Learn Deeply. Simply." / "تعلم بعمق. ببساطة." Technical credibility without corporate coldness.

This brand ships with **two approved identities — Light and Dark — and a required
user-controlled toggle** between them (see [Theming](#theming) below). Neither mode is a
fallback of the other; both are first-class and must be built/reviewed together.

## Brand Colors — Light

| Role | Hex | Usage |
|------|-----|-------|
| Primary | #2563EB | Main CTAs, active nav, links, filled buttons |
| Accent | #7C3AED | Highlights, badges, hover states, gradient partner |
| Cyan (extended) | #00D1FF | Gradient stop, data-viz accents, glow effects |
| Violet-2 (extended) | #B026FF | Gradient far stop, decorative glow only |
| Background | #F8FAFC | Page canvas |
| Surface | #FFFFFF | Cards, panels, modals |
| Border | #E5E7EB | Dividers, input borders, table lines |
| Text Primary | #071426 | Headings and primary body text |
| Text Secondary | #475569 | Captions, labels, metadata |
| Warning | #D97706 | Non-blocking notices |
| Success | #16A34A | Confirmations, positive states |
| Error | #DC2626 | Validation errors, destructive actions |

## Brand Colors — Dark

| Role | Hex | Usage |
|------|-----|-------|
| Primary | #3B82F6 | Main CTAs, active nav, links (brightened for AA contrast on navy) |
| Accent | #8B5CF6 | Highlights, badges, hover states |
| Cyan (extended) | #00D1FF | Gradient stop, data-viz accents, glow effects |
| Violet-2 (extended) | #B026FF | Gradient far stop, decorative glow only |
| Background | #071426 | Page canvas |
| Surface | #0B1D3A | Cards, panels, modals |
| Border | #1E3358 | Dividers, input borders, table lines |
| Text Primary | #F7FAFC | Headings and primary body text |
| Text Secondary | #C3CAD6 | Captions, labels, metadata |
| Muted | #A1A8B3 | Tertiary text, placeholders, disabled state |
| Warning | #FBBF24 | Non-blocking notices |
| Success | #4ADE80 | Confirmations, positive states |
| Error | #F87171 | Validation errors, destructive actions |

Full token set (primary/accent tints, subtle backgrounds, etc.) lives in
`.ui-bridge/design-system.css` and `ui-prototypes/design-tokens.css` as CSS custom properties —
never hardcode these hexes in components.

## Typography

| Role | Font Family | Weight | Approx Size |
|------|-------------|--------|-------------|
| Heading (Arabic) | IBM Plex Sans Arabic | 700 | 2rem–3.5rem |
| Body (Arabic) | IBM Plex Sans Arabic | 400 | 1rem |
| Heading (Latin) | Inter | 700 | 2rem–3.5rem |
| Body (Latin) | Inter | 400 | 1rem |
| Monospace | JetBrains Mono | 400 | 0.875rem |

Font stack: `'IBM Plex Sans Arabic', 'Inter', sans-serif` for both heading and body — Arabic
runs render in Plex Arabic, Latin runs fall through to Inter, so neither language looks bolted
onto the other.

## Theming

SimpleElm is a **toggle-based** dual-identity brand, not a `prefers-color-scheme`-only one:

- Mechanism: `data-theme="light"` or `data-theme="dark"` on `<html>`.
- Persistence: `localStorage['simpleelm-theme']`.
- Default: on first visit, respect the OS preference (`prefers-color-scheme`); once a visitor
  explicitly toggles, that choice persists and overrides the OS preference on every later visit.
- CSS contract: light tokens live on bare `:root`; dark tokens are defined twice — once under
  `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {...} }` for
  OS-driven defaults, and again under `:root[data-theme="dark"] {...}` so an explicit toggle
  always wins in both directions. Every component must reference `var(--color-*)` tokens only,
  never a literal hex, so both themes stay correct automatically.
- A toggle control (sun/moon icon button) must be present in the shared header partial on every
  page, next to the language toggle.

## Layout

- **Text direction**: Bidirectional — RTL for Arabic, LTR for English; admin surfaces always LTR
- **Max content width**: 1280px (public pages), full-width fluid for admin/dashboard tables
- **Base spacing unit**: 4px (0.25rem)
- **Border radius**: 12–16px (cards/tiles), 8px (inputs), 999px (badges/pills)
- **Shadow style**: Subtle single-layer elevation in light mode; soft outer glow (accent-tinted,
  low opacity) permitted in dark mode to read as "glowing" rather than flat

## Component Style

- **Buttons**: Filled primary (`--color-primary`), 12px vertical / 24px horizontal padding, 8px
  radius. Ghost/outline for secondary actions. Max 1 `.btn-primary` per viewport section.
- **Cards / feature tiles**: Surface background, 12–16px radius, one icon chip + title + one
  line of support copy. No nested cards. Max 1 primary CTA per card.
- **Inputs**: Outlined, 1px border, 8px radius, 12px padding. Focus ring: 2px accent color, 2px
  offset. Every input has an associated `<label>`.
- **Interactive / data panels** (e.g. the loss-curve hyperparameter simulator): denser than
  marketing sections, live-updating on slider input, values always shown numerically next to
  any slider.
- **Tables** (admin, always LTR): no zebra striping, compact density, row hover with a subtle
  tint using the current theme's `--color-bg-subtle`.
- **Badges/tags**: Pill shape, max 3 badge types per card, never rely on color alone.

## Accessibility

- **Minimum text contrast**: 4.5:1 (WCAG AA) — verified independently for both light and dark
- **Large text contrast**: 3:1 (text ≥ 18pt or 14pt bold)
- **Focus indicator**: 2px solid accent color, 2px offset, never hidden
- **Motion preference**: Respect `prefers-reduced-motion: reduce`, including the theme-switch
  transition itself

## Overall Aesthetic

Friendly and technically confident, not corporate. A cool blue-cyan-violet gradient family
carries the brand across a near-white light identity and a deep-navy dark identity that feel
like two sides of the same object, not two different products. No photography of people —
abstract 3D renders, neural-network motifs, and a glowing gradient "S" mark do the visual work
instead. Arabic (IBM Plex Sans Arabic) and Latin (Inter) headings carry equal typographic
weight. The interactive learning module (hyperparameter sliders driving a live loss-curve
chart) is the platform's signature proof element and should read as a real, working tool, not a
decorative illustration.
