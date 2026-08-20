"""
Generate first-class design-direction artifacts.

These artifacts are allowed to exist as drafts, but the workflow must not generate
design-system/HTML until the required approval gates are present.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from ui_bridge_core import (
    ApprovalStore,
    SchemaValidator,
    VersionedArtifacts,
    ensure_bridge,
    read_json,
)
from layout_dna_engine import build_layout_dna


def latest_artifact(root: Path, basename: str) -> Dict[str, Any]:
    bridge = ensure_bridge(root)
    latest = read_json(bridge / "latest.json", default={}) or {}
    filename = latest.get(basename)
    if filename and (bridge / filename).exists():
        return read_json(bridge / filename, default={}) or {}
    candidates = sorted(bridge.glob("%s.v*.json" % basename))
    if candidates:
        return read_json(candidates[-1], default={}) or {}
    return {}


def approved_direction(root: Path) -> Dict[str, Any]:
    intake = latest_artifact(root, "brand-intake")
    return intake.get("approved_direction", {})


def selected_proposal(root: Path, proposal: str | None) -> Dict[str, Any]:
    proposals = latest_artifact(root, "brand-proposals")
    directions = proposals.get("directions", [])
    if not directions:
        return {}
    if proposal:
        for direction in directions:
            if direction.get("id") == proposal:
                return direction
    return directions[0]


def page_records(root: Path) -> List[Dict[str, Any]]:
    page_map = read_json(ensure_bridge(root) / "page-map.json", default={}) or {}
    return page_map.get("pages", [])


def page_kind(page: Dict[str, Any]) -> str:
    slug = page.get("slug", "")
    sections = " ".join(page.get("sections", [])).lower()
    if page.get("is_admin"):
        if "login" in slug:
            return "auth"
        if "detail" in slug:
            return "admin-detail"
        return "admin-list"
    if slug in ("index", "home"):
        return "home"
    if "detail" in slug:
        return "detail"
    if any(token in sections for token in ("grid", "pagination", "filter", "listing")):
        return "listing"
    if "form" in sections:
        return "form"
    return "content"


def assign_hero_patterns(pages: List[Dict[str, Any]]) -> Dict[str, str]:
    mapping = {
        "home": "proof-first",
        "detail": "founder/expert",
        "listing": "editorial",
        "form": "split",
        "content": "magazine",
        "auth": "split",
        "admin-list": "proof-first",
        "admin-detail": "asymmetric",
    }
    return {page["slug"]: mapping.get(page_kind(page), "asymmetric") for page in pages}


def assign_narrative_patterns(pages: List[Dict[str, Any]]) -> Dict[str, str]:
    mapping = {
        "home": "authority",
        "detail": "methodology",
        "listing": "comparison",
        "form": "transformation",
        "content": "editorial",
        "auth": "utility",
        "admin-list": "operational",
        "admin-detail": "case-study",
    }
    return {page["slug"]: mapping.get(page_kind(page), "editorial") for page in pages}


def assign_section_patterns(pages: List[Dict[str, Any]]) -> Dict[str, str]:
    mapping = {
        "home": "proof-strip",
        "detail": "split-detail",
        "listing": "editorial-list",
        "form": "methodology-flow",
        "content": "timeline",
        "auth": "focused-panel",
        "admin-list": "data-table",
        "admin-detail": "record-workspace",
    }
    return {page["slug"]: mapping.get(page_kind(page), "bento") for page in pages}


def content_density(pages: List[Dict[str, Any]]) -> str:
    if any(p.get("is_admin") for p in pages):
        return "high for admin surfaces, medium for public pages"
    avg_sections = sum(len(p.get("sections", [])) for p in pages) / max(1, len(pages))
    if avg_sections >= 6:
        return "medium-high"
    if avg_sections <= 3:
        return "low"
    return "medium"


def photography_system(direction: Dict[str, Any], project_type: str, pages: List[Dict[str, Any]], state: str) -> Dict[str, Any]:
    has_profiles = any("expert" in p.get("slug", "") or "team" in p.get("slug", "") for p in pages)
    has_products = project_type in ("E-commerce", "Real Estate")
    return {
        "state": state,
        "style": direction.get("photography", ""),
        "aspect_ratios": {
            "hero": "21:9 or 16:9" if len(pages) == 1 and pages[0].get("slug") in ("index", "home") else "16:9 or 4:3",
            "cards": "1:1 or 4:3" if has_products else "4:3",
            "portraits": "3:4" if has_profiles else "not primary unless real people are part of the domain",
        },
        "color_grading": "natural contrast; domain-appropriate warmth; no glossy AI stock grading",
        "background_style": "real environments tied to %s, not abstract backdrops" % project_type,
        "portrait_rules": "named real people with role context; avoid anonymous stock headshots",
    }


def iconography_system(direction: Dict[str, Any], project_type: str, pages: List[Dict[str, Any]], state: str) -> Dict[str, Any]:
    admin_heavy = sum(1 for p in pages if p.get("is_admin")) > len(pages) / 2
    return {
        "state": state,
        "style": direction.get("iconography", ""),
        "stroke_width": "1.5px" if direction.get("name") == "Premium" else ("2px" if admin_heavy else "1.75px"),
        "corner_radius": "square-to-soft for admin density" if admin_heavy else "match approved component geometry",
        "density": "functional and compact" if admin_heavy else "sparse; icons support scanning, not decoration",
        "placement": "inline with labels or functional controls; never repeated decorative icon tiles",
        "domain_rule": "choose symbols from actual %s workflows, not generic feature icons" % project_type,
    }


def content_realism_system(project_type: str, pages: List[Dict[str, Any]], state: str) -> Dict[str, Any]:
    return {
        "state": state,
        "numbers": "derive numbers from visible records or page-specific inventory; explain if estimated",
        "names": "use locale/domain-appropriate names for %s; admin records must look operational" % project_type,
        "titles": "real page/entity titles from the page map and spec vocabulary, never numbered placeholders",
        "testimonials": "only with named context and believable outcome; omit if the spec has no testimonial signal",
        "metrics_logic": "prefer counts from static_content_needed; avoid broad success claims unless sourced",
        "name_logic": "Arabic-first public names when Arabic/RTL is detected; role-specific admin names",
        "forbidden": ["John Doe", "Jane Doe", "Course 1", "500+", "99%", "24/7", "Get Started Today"],
    }


def build_artifacts(root: Path, direction: Dict[str, Any], draft: bool) -> Dict[str, Dict[str, Any]]:
    pages = page_records(root)
    slugs = [p["slug"] for p in pages]
    project_type = direction.get("project_type") or direction.get("project_type", "Generic Professional")
    if isinstance(project_type, dict):
        project_type = project_type.get("category", "Generic Professional")
    hero_patterns = ["proof-first", "editorial", "asymmetric", "founder/expert", "magazine", "split"]
    narrative_patterns = ["authority", "transformation", "methodology", "case-study", "editorial", "premium", "comparison", "operational", "utility"]
    section_patterns = ["bento", "timeline", "editorial-list", "proof-strip", "split-detail", "data-table", "focused-panel", "record-workspace", "methodology-flow"]
    state = "draft" if draft else "approved-source"

    competitive_analysis = {
            "state": state,
            "patterns_to_copy": direction.get("references", []),
            "patterns_to_avoid": ["generic SaaS hero", "three-card syndrome", "fake metrics", "centered everything"],
            "hero_types": hero_patterns,
            "section_types": section_patterns,
            "copy_tone": [direction.get("cta_tone", "specific and outcome-led")],
            "spacing_observations": [direction.get("density", "intentional density")],
            "layout_observations": [direction.get("layout_style", "non-repetitive page rhythm")],
            "visual_personality": [direction.get("personality", "distinct")],
    }
    layout_dna = build_layout_dna(slugs, direction, competitive_analysis, state)

    return {
        "competitive-analysis": competitive_analysis,
        "moodboard": {
            "state": state,
            "photography": direction.get("photography", ""),
            "density": direction.get("density", ""),
            "card_style": direction.get("layout_style", ""),
            "spacing_style": direction.get("density", ""),
            "icon_style": direction.get("iconography", ""),
            "color_temperature": "derived from approved/proposed palette",
            "editorial_feel": direction.get("personality", ""),
        },
        "visual-dna": {
            "state": state,
            "personality": direction.get("personality", ""),
            "geometry": "restrained, no decorative blobs",
            "density": direction.get("density", ""),
            "motion": "minimal, functional transitions only",
            "contrast": "AA minimum, strong hierarchy",
            "photography_style": direction.get("photography", ""),
            "iconography": direction.get("iconography", ""),
        },
        "layout-dna": layout_dna,
        "photography-system": {
            **photography_system(direction, project_type, pages, state),
        },
        "iconography-system": iconography_system(direction, project_type, pages, state),
        "hero-diversity": {
            "state": state,
            "patterns": hero_patterns,
            "page_assignments": assign_hero_patterns(pages),
            "assignment_logic": "page-type aware: home/detail/listing/admin/auth, not round-robin",
            "anti_repetition_rules": ["no same hero pattern on adjacent public pages", "homepage must not use generic centered SaaS hero"],
        },
        "component-personality": {
            "state": state,
            "buttons": "specific CTA text, clear primary/secondary hierarchy",
            "cards": "vary layout by content type; no six equal cards",
            "badges": "max three badge types per page",
            "stats": "one featured metric or real table; no fake metric row",
            "forms": "labeled, compact, realistic validation states",
            "tables": "dense admin utility, restrained borders, no zebra-striping",
        },
        "content-realism": content_realism_system(project_type, pages, state),
        "narrative-patterns": {
            "state": state,
            "patterns": narrative_patterns,
            "page_assignments": assign_narrative_patterns(pages),
            "assignment_logic": "page-purpose aware: home authority, detail methodology, listing comparison, admin operational",
            "anti_repetition_rules": ["do not repeat Problem-Proof-CTA on every page", "detail pages should use evidence and methodology"],
        },
        "section-diversity": {
            "state": state,
            "patterns": section_patterns,
            "page_assignments": assign_section_patterns(pages),
            "assignment_logic": "content-structure aware: listing/detail/form/admin sections choose different section systems",
            "anti_repetition_rules": ["no repeated Hero-Cards-CTA-Footer sequence", "alternate data-heavy and story-heavy sections"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate design-direction artifacts")
    parser.add_argument("--root", default=".")
    parser.add_argument("--proposal", help="Use a proposal ID as draft source when no approved brand exists")
    parser.add_argument("--draft", action="store_true", help="Allow draft artifacts from a proposal")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    direction = approved_direction(root)
    draft = False
    if not direction:
        if not args.draft:
            print("ERROR: no approved brand direction. Use --draft --proposal A to create draft artifacts.", file=sys.stderr)
            sys.exit(1)
        direction = selected_proposal(root, args.proposal)
        draft = True
    if not direction:
        print("ERROR: no approved direction or proposal found.", file=sys.stderr)
        sys.exit(1)

    validator = SchemaValidator()
    store = VersionedArtifacts(root)
    written = []
    for name, data in build_artifacts(root, direction, draft).items():
        errors = validator.validate(name, data)
        if errors:
            print("ERROR: %s" % "; ".join(errors), file=sys.stderr)
            sys.exit(1)
        path = store.write_new(name, data)
        written.append(str(path))

    print(json.dumps({"written": written, "draft": draft}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
