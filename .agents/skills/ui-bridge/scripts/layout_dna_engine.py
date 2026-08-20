"""
Layout DNA engine.

Transforms page inventory, proposal/brand direction, and competitive analysis
into concrete layout rules and per-page layout assignments.
"""
from __future__ import annotations

from typing import Any, Dict, List


LAYOUT_PATTERNS = [
    "editorial-index",
    "proof-led-detail",
    "asymmetric-feature",
    "dense-admin-table",
    "methodology-flow",
    "premium-profile",
]


def page_layout_kind(slug: str, direction: Dict[str, Any], index: int) -> str:
    if slug.startswith("admin"):
        return "dense-admin-table"
    if "detail" in slug:
        return "proof-led-detail"
    if slug in ("index", "home"):
        if "premium" in direction.get("name", "").lower():
            return "premium-profile"
        return "editorial-index"
    return LAYOUT_PATTERNS[index % len(LAYOUT_PATTERNS)]


def build_layout_dna(
    slugs: List[str],
    direction: Dict[str, Any],
    competitive_analysis: Dict[str, Any],
    state: str,
) -> Dict[str, Any]:
    layout_style = direction.get("layout_style") or "; ".join(competitive_analysis.get("layout_observations", []))
    density = (direction.get("density") or "medium").lower()
    name = direction.get("name", "")
    editorialness = "high" if name == "Editorial" or "editorial" in layout_style.lower() else "medium"
    card_density = "low" if "fewer cards" in density else ("high" if "dense" in density else "medium")

    return {
        "state": state,
        "symmetry": "low-to-medium" if "asymmetric" in layout_style.lower() or editorialness == "high" else "medium",
        "editorialness": editorialness,
        "card_density": card_density,
        "grid_style": layout_style or "mixed page-specific grids with no repeated equal-card sections",
        "alignment_style": "mixed alignment by section purpose; avoid centered paragraphs as default",
        "section_rhythm": "rotate proof, narrative, data, methodology, and action sections by page type",
        "asymmetry_level": "medium" if editorialness == "high" else "low",
        "page_assignments": {
            slug: {
                "layout_pattern": page_layout_kind(slug, direction, idx),
                "hero_influence": direction.get("hero_style", ""),
                "density": direction.get("density", ""),
            }
            for idx, slug in enumerate(slugs)
        },
    }
