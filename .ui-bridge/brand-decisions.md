# Brand Decisions

## State

- State: `approved_brand`
- Generated: 2026-08-18

## Important

No industry defaults are silently selected. This brand direction was provided directly by the
user as explicit project assets (SimpleElm light + dark brand identity sheets), not inferred.

## Real Project Signals

- Logos found: 1 (SimpleElm gradient "S" mark, light + dark variants)
- Colors found: 10 (7 light swatches, 7 dark swatches, overlapping on the shared accent family)
- CSS variables found: 4
- Fonts found: 2 (IBM Plex Sans Arabic, Inter)

## Approved Direction: SimpleElm

- Brand: **SimpleElm** ("سيمبل إلم" / تعلم بعمق. ببساطة / Learn Deeply. Simply.)
- Personality: friendly, modern, AI-forward, confident but approachable.
- Palette (light): primary `#2563EB`, accent `#7C3AED`, cyan `#00D1FF`, violet-2 `#B026FF`,
  background `#F8FAFC`, surface `#FFFFFF`, ink `#071426`, border `#E5E7EB`.
- Palette (dark): background `#071426`, surface `#0B1D3A`, ink-inverse `#F7FAFC`,
  muted `#A1A8B3`, same blue/cyan/violet accent family.
- Typography: IBM Plex Sans Arabic (Arabic heading + body), Inter (Latin fallback).
- Iconography: Lucide outline, 1.75–2px stroke — home, book-open, flask-conical, brain, route,
  users, message-circle.
- Photography: no human photography — abstract 3D renders, neural-network motifs, glowing
  gradient S-mark compositions only.
- Theming: **both** a light and a dark identity are approved. The product must expose a
  user-controlled toggle (`data-theme` on `<html>`, persisted in `localStorage` under
  `simpleelm-theme`), defaulting to the visitor's OS preference until they choose explicitly.

See `.ui-bridge/brand-intake.v3.json` for the full structured record.
