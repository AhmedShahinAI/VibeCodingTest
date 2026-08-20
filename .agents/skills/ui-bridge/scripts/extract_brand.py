"""
extract_brand.py - discover real brand signals and enforce brand policy.

Strict mode is the default. If no approved brand exists, this script writes a
brand-intake artifact and exits non-zero before any design/HTML generation can
continue.
"""
from __future__ import annotations

import argparse
import colorsys
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List

from ui_bridge_core import (
    ApprovalStore,
    SchemaValidator,
    VersionedArtifacts,
    ensure_bridge,
    iter_real_source_files,
    read_json,
    relative_posix,
    utc_now,
    write_json,
)
from infer_engine import ProjectTypeInferrer, collect_text_lines


HEX_RE = re.compile(r"(?<![&\w])#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b")
CSS_VAR_RE = re.compile(r"--(color|brand|primary|secondary|accent|bg|background|text|font)[^:]*:\s*([^;}\n]+)", re.IGNORECASE)
FONT_FAMILY_RE = re.compile(r"font-family\s*:\s*([^;}\n]+)", re.IGNORECASE)
GOOGLE_FONTS_RE = re.compile(r"fonts\.googleapis\.com/css[^\s\"'<>]+", re.IGNORECASE)
TAILWIND_COLOR_RE = re.compile(r"['\"]([a-zA-Z][a-zA-Z0-9-]*)['\"]\s*:\s*['\"]?(#[0-9A-Fa-f]{3,6})['\"]?")

SEARCH_EXTENSIONS = {".css", ".scss", ".sass", ".vue", ".tsx", ".jsx", ".ts", ".js", ".html", ".md", ".json"}
LOGO_EXTENSIONS = {".svg", ".png", ".webp", ".ico"}


BASE_PROPOSAL_DIRECTIONS = {
    "A": {
        "name": "Editorial",
        "references": ["editorial case-study sites", "evidence-led institutional pages", "publication-style service pages"],
        "photography": "Documentary scenes connected to the real domain, natural light, no stock laptop smiles.",
        "iconography": "Sparse outline icons, 1.75px stroke, inline with text, no icon tiles.",
        "density": "Airy editorial with fewer cards and larger reading blocks.",
        "personality": "Authoritative, calm, evidence-led.",
        "layout_style": "Editorial asymmetry, proof blocks, long-form sections, fewer equal grids.",
        "hero_style": "Proof-first or editorial hero with a specific headline and evidence below.",
        "cta_tone": "Specific action tied to the user's next decision.",
    },
    "B": {
        "name": "Corporate",
        "references": ["mature B2B service sites", "operational product pages", "trust-led company pages"],
        "photography": "Professional team/customer contexts, clear work environments, no generic handshake imagery.",
        "iconography": "Functional outline icons, 2px stroke, restrained badges, table-friendly density.",
        "density": "Medium density, structured sections, dashboard-compatible admin pages.",
        "personality": "Trusted, operational, polished, direct.",
        "layout_style": "Structured split sections, partner proof, process timelines, clean tables.",
        "hero_style": "Split hero with a concrete offer and proof tied to the domain.",
        "cta_tone": "Book, request, compare, or submit based on the project workflow.",
    },
    "C": {
        "name": "Premium",
        "references": ["premium service brands", "expert-led boutique sites", "high-trust editorial portfolios"],
        "photography": "Premium portraits and real spaces, controlled lighting, restrained color grading.",
        "iconography": "Minimal symbols, 1.5px stroke, no decorative icon rows.",
        "density": "Low-to-medium density, strong contrast, fewer but more confident sections.",
        "personality": "Selective, premium, expert-led, confident.",
        "layout_style": "Asymmetric hero, large proof quote, premium course cards, strong whitespace.",
        "hero_style": "Founder/expert or premium proof-first hero.",
        "cta_tone": "Reserve, request details, or speak to a specialist.",
    },
}


DOMAIN_PROPOSAL_OVERLAYS = {
    "EdTech": {
        "references": ["training organization websites", "executive education pages", "Arabic course catalog experiences"],
        "photography": "Real training rooms, named instructors, course materials, cohort moments, no anonymous classroom stock.",
        "section_types": ["methodology", "course evidence", "expert proof", "partner proof", "registration form", "admin table"],
        "cta_tone": "Browse courses, reserve a seat, request program details.",
    },
    "Healthcare": {
        "references": ["clinic service pages", "patient trust pages", "medical practice websites"],
        "photography": "Real care environments, practitioners with patients where appropriate, clean clinical backgrounds.",
        "section_types": ["care pathway", "provider proof", "service detail", "patient FAQ", "appointment form", "admin table"],
        "cta_tone": "Book an appointment, view services, contact the clinic.",
    },
    "E-commerce": {
        "references": ["premium product catalogs", "conversion-focused product pages", "trust-led checkout flows"],
        "photography": "Product-first images, real-use context, clean detail crops, no generic shopping stock.",
        "section_types": ["product grid", "category story", "reviews", "shipping proof", "checkout form", "admin table"],
        "cta_tone": "Shop, compare products, add to cart, complete checkout.",
    },
    "Real Estate": {
        "references": ["property listing portals", "brokerage brand pages", "neighborhood guide pages"],
        "photography": "Actual properties, exterior/interior detail, neighborhood context, no staged generic interiors.",
        "section_types": ["listing grid", "property proof", "neighborhood context", "agent profile", "inquiry form", "admin table"],
        "cta_tone": "View listings, schedule viewing, request property details.",
    },
    "SaaS Dashboard": {
        "references": ["mature product dashboards", "B2B feature pages", "workflow-led SaaS sites"],
        "photography": "Product UI, real workflow screenshots, customer operating context; avoid floating mockups only.",
        "section_types": ["workflow proof", "feature comparison", "integrations", "case study", "demo form", "admin table"],
        "cta_tone": "Request demo, compare features, start workspace setup.",
    },
    "Marketing/CRM": {
        "references": ["CRM workflow pages", "lead management dashboards", "campaign operations sites"],
        "photography": "Real operations teams, dashboards, campaign materials, customer pipeline contexts.",
        "section_types": ["pipeline proof", "workflow stages", "dashboard evidence", "team roles", "lead form", "admin table"],
        "cta_tone": "Submit inquiry, review pipeline, contact the team.",
    },
}


FORBIDDEN_PROPOSAL_COLORS = {
    "#1E40AF", "#0EA5E9", "#F8FAFC", "#F9FAFB", "#F3F4F6", "#F1F5F9",
    "#6366F1", "#4F46E5", "#7C3AED", "#8B5CF6", "#10B981", "#059669",
}

FORBIDDEN_PROPOSAL_FONTS = {
    "inter", "cairo", "tajawal", "plus jakarta sans", "poppins", "dm sans",
    "geist", "system-ui", "arial", "helvetica",
}


def scan_tailwind(root: Path) -> Dict[str, str]:
    colors = {}
    for name in ("tailwind.config.ts", "tailwind.config.js", "tailwind.config.mjs"):
        path = root / name
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        for match in TAILWIND_COLOR_RE.finditer(content):
            role, value = match.group(1), match.group(2).upper()
            colors[role] = value
    return colors


def scan_project(root: Path) -> Dict:
    signals = {
        "hex_colors": [],
        "css_variables": [],
        "font_families": [],
        "google_fonts": [],
        "tailwind_colors": scan_tailwind(root),
        "logos": [],
        "rtl_detected": False,
        "arabic_detected": False,
    }

    hex_seen = set()
    font_seen = set()

    for path in iter_real_source_files(root, SEARCH_EXTENSIONS | LOGO_EXTENSIONS):
        rel = relative_posix(path, root)
        lower = path.name.lower()
        if path.suffix.lower() in LOGO_EXTENSIONS and any(token in lower for token in ("logo", "brand", "mark", "favicon")):
            signals["logos"].append({"path": rel, "confidence": "explicit"})
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        if re.search(r'dir=["\']rtl["\']|direction:\s*rtl|[\u0600-\u06ff]', content, re.IGNORECASE):
            signals["rtl_detected"] = True
        if re.search(r'lang=["\']ar["\']|[\u0600-\u06ff]{3,}', content, re.IGNORECASE):
            signals["arabic_detected"] = True

        for match in HEX_RE.finditer(content):
            value = match.group().upper()
            key = (value, rel)
            if key not in hex_seen:
                hex_seen.add(key)
                signals["hex_colors"].append({"hex": value, "file": rel, "confidence": "implicit"})

        for match in CSS_VAR_RE.finditer(content):
            var = match.group(0).strip()
            confidence = "explicit" if any(token in var.lower() for token in ("primary", "brand", "accent")) else "implicit"
            signals["css_variables"].append({"variable": var, "file": rel, "confidence": confidence})

        for match in FONT_FAMILY_RE.finditer(content):
            value = match.group(1).strip().strip("'\"").split(",")[0].strip()
            if value and len(value) > 2 and value.lower() not in ("sans-serif", "serif", "monospace", "system-ui"):
                key = (value, rel)
                if key not in font_seen:
                    font_seen.add(key)
                    signals["font_families"].append({"font": value, "file": rel, "confidence": "implicit"})

        for match in GOOGLE_FONTS_RE.finditer(content):
            signals["google_fonts"].append({"url": match.group(), "file": rel, "confidence": "implicit"})

    return signals


def has_explicit_brand(signals: Dict) -> bool:
    explicit_vars = [s for s in signals.get("css_variables", []) if s.get("confidence") == "explicit"]
    return bool(signals.get("logos") or explicit_vars or signals.get("tailwind_colors") or signals.get("font_families"))


def build_approved_brand(signals: Dict, approvals: Dict) -> Dict:
    brand_approval = approvals.get("brand_direction", {})
    return {
        "state": "approved_brand",
        "approval": brand_approval,
        "signals": signals,
        "source": "approved user selection" if brand_approval else "explicit project assets",
    }


def build_intake(root: Path, policy: str, signals: Dict) -> Dict:
    return {
        "state": "brand_intake_required",
        "policy": policy,
        "generated_at": utc_now(),
        "required_user_action": [
            "Provide logo/colors/fonts/references, or run proposal mode.",
            "Approve a brand direction before Impeccable, DESIGN.md, design-system.json, or HTML generation.",
        ],
        "allowed_next_commands": [
            "ui-plan --brand-policy=proposal",
            "ui-approve-brand --proposal=A",
            "ui-plan --continue",
        ],
        "signals": signals,
        "warning": "No reliable approved brand identity was found. No defaults were selected.",
    }


def infer_project_type(root: Path) -> Dict:
    return ProjectTypeInferrer().infer(collect_text_lines(root))


def domain_overlay(project_type: Dict) -> Dict:
    category = project_type.get("category", "Generic Professional")
    return DOMAIN_PROPOSAL_OVERLAYS.get(category, {
        "references": ["domain-specific competitors", "mature service/product pages", "trust-led conversion pages"],
        "photography": "Real people, real product/service context, no generic stock scenes.",
        "section_types": ["proof", "methodology", "comparison", "case study", "form", "admin table"],
        "cta_tone": "Use action language tied to the project workflow.",
    })


def build_competitive_analysis(signals: Dict, project_type: Dict) -> Dict:
    arabic = bool(signals.get("arabic_detected") or signals.get("rtl_detected"))
    overlay = domain_overlay(project_type)
    return {
        "state": "draft",
        "project_type": project_type,
        "patterns_to_copy": overlay["references"],
        "patterns_to_avoid": [
            "generic SaaS hero",
            "three-card syndrome",
            "fake metrics",
            "centered everything",
        ],
        "hero_types": ["proof-first", "editorial", "asymmetric", "founder/expert", "magazine", "split"],
        "section_types": overlay["section_types"],
        "copy_tone": ["Arabic-first and evidence-led" if arabic else "evidence-led and specific"],
        "spacing_observations": ["public pages can breathe; admin pages stay compact and scannable"],
        "layout_observations": ["avoid repeated centered hero plus equal-card grid; vary by page purpose"],
        "visual_personality": ["professional", "trustworthy", "approachable"],
    }


def _hex_from_hsl(hue: int, sat: float, light: float) -> str:
    r, g, b = colorsys.hls_to_rgb((hue % 360) / 360.0, light, sat)
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def _signal_seed(signals: Dict, direction_id: str) -> int:
    source = json.dumps(signals, ensure_ascii=True, sort_keys=True) + direction_id
    return int(hashlib.sha256(source.encode("utf-8")).hexdigest()[:8], 16)


def _detected_primary(signals: Dict) -> str | None:
    for item in signals.get("css_variables", []):
        text = item.get("variable", "")
        if item.get("confidence") == "explicit":
            match = HEX_RE.search(text)
            if match:
                return match.group().upper()
    for _, value in signals.get("tailwind_colors", {}).items():
        if value:
            return str(value).upper()
    return None


def generate_proposal_palette(signals: Dict, direction_id: str) -> Dict[str, str]:
    detected = _detected_primary(signals)
    seed = _signal_seed(signals, direction_id)
    hue = seed % 360
    primary = detected or _hex_from_hsl(hue, 0.42, 0.31)
    if primary.upper() in FORBIDDEN_PROPOSAL_COLORS:
        hue = (hue + 47) % 360
        primary = _hex_from_hsl(hue, 0.38, 0.29)
    accent = _hex_from_hsl(hue + 151, 0.45, 0.43)
    surface = _hex_from_hsl(hue + 18, 0.14, 0.96)
    text = _hex_from_hsl(hue + 4, 0.24, 0.14)
    return {
        "primary": primary,
        "accent": accent,
        "background": "#FFFFFF",
        "surface": surface,
        "text": text,
        "generation": "project-signal-hash" if not detected else "explicit-project-signal",
    }


def generate_proposal_fonts(signals: Dict) -> Dict[str, str]:
    detected = []
    for item in signals.get("font_families", []):
        font = item.get("font", "").strip()
        if font and font.lower() not in FORBIDDEN_PROPOSAL_FONTS and font not in detected:
            detected.append(font)
    if detected:
        heading = detected[0]
        body = detected[1] if len(detected) > 1 else detected[0]
        return {
            "arabic_heading": heading,
            "arabic_body": body,
            "latin_fallback": body,
            "generation": "explicit-project-font-signal",
        }
    return {
        "arabic_heading": "USER_APPROVED_ARABIC_HEADING_REQUIRED",
        "arabic_body": "USER_APPROVED_ARABIC_BODY_REQUIRED",
        "latin_fallback": "USER_APPROVED_LATIN_FALLBACK_REQUIRED",
        "generation": "user-required",
    }


def proposal_directions(project_type: Dict) -> Dict[str, Dict]:
    overlay = domain_overlay(project_type)
    directions = {}
    for key, base in BASE_PROPOSAL_DIRECTIONS.items():
        item = dict(base)
        item["references"] = overlay["references"] + base.get("references", [])
        item["photography"] = overlay["photography"] + " " + base.get("photography", "")
        item["cta_tone"] = overlay["cta_tone"]
        item["project_type"] = project_type.get("category", "Generic Professional")
        directions[key] = item
    return directions


def build_proposals(signals: Dict, competitive_analysis: Dict, project_type: Dict) -> Dict:
    directions = []
    for key, data in proposal_directions(project_type).items():
        item = {"id": key, "state": "inferred_proposal"}
        item.update(data)
        item["palette"] = generate_proposal_palette(signals, key)
        item["fonts"] = generate_proposal_fonts(signals)
        item["competitive_basis"] = {
            "patterns_to_copy": competitive_analysis.get("patterns_to_copy", []),
            "patterns_to_avoid": competitive_analysis.get("patterns_to_avoid", []),
            "hero_types": competitive_analysis.get("hero_types", []),
            "section_types": competitive_analysis.get("section_types", []),
            "copy_tone": competitive_analysis.get("copy_tone", []),
            "spacing_observations": competitive_analysis.get("spacing_observations", []),
        }
        directions.append(item)
    return {
        "state": "inferred_proposal",
        "generated_at": utc_now(),
        "project_type": project_type,
        "directions": directions,
        "approval_required": True,
        "raw_signals": signals,
        "signals_summary": {
            "logos_found": len(signals.get("logos", [])),
            "colors_found": len(signals.get("hex_colors", [])),
            "fonts_found": len(signals.get("font_families", [])),
        },
    }


def write_brand_decisions(root: Path, result: Dict) -> None:
    out = ensure_bridge(root) / "brand-decisions.md"
    lines = [
        "# Brand Decisions",
        "",
        "## State",
        "",
        "- State: `%s`" % result.get("state", "unknown"),
        "- Generated: %s" % date.today().isoformat(),
        "",
        "## Important",
        "",
        "No industry defaults are silently selected. Inferred proposals are not approved brand decisions.",
        "",
    ]
    signals = result.get("signals") or result.get("raw_signals") or {}
    lines += [
        "## Real Project Signals",
        "",
        "- Logos found: %d" % len(signals.get("logos", [])),
        "- Colors found: %d" % len(signals.get("hex_colors", [])),
        "- CSS variables found: %d" % len(signals.get("css_variables", [])),
        "- Fonts found: %d" % len(signals.get("font_families", [])),
        "",
    ]
    if result.get("state") == "brand_intake_required":
        lines += [
            "## Required User Action",
            "",
            "Approve a brand direction or provide explicit brand assets before continuing.",
            "",
        ]
    out.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract brand signals from real project sources")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", default=".")
    parser.add_argument("--brand-policy", choices=["strict", "proposal", "fallback"], default="strict")
    parser.add_argument("--allow-unapproved-html", action="store_true")
    parser.add_argument("--continue", dest="continue_run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    bridge = ensure_bridge(root)
    approvals = ApprovalStore(root).data()
    store = VersionedArtifacts(root)

    print("Scanning real project sources for brand signals: %s" % root, file=sys.stderr)
    signals = scan_project(root)
    project_type = infer_project_type(root)
    approved = ApprovalStore(root).is_approved("brand_direction")

    if approved:
        result = build_approved_brand(signals, approvals)
    elif args.brand_policy == "proposal":
        competitive_analysis = build_competitive_analysis(signals, project_type)
        comp_errors = SchemaValidator().validate("competitive-analysis", competitive_analysis)
        if comp_errors:
            print("Schema error: %s" % "; ".join(comp_errors), file=sys.stderr)
            sys.exit(2)
        comp_path = store.write_new("competitive-analysis", competitive_analysis)
        result = build_proposals(signals, competitive_analysis, project_type)
        proposal_errors = SchemaValidator().validate("brand-proposals", result)
        if proposal_errors:
            print("Schema error: %s" % "; ".join(proposal_errors), file=sys.stderr)
            sys.exit(2)
        path = store.write_new("brand-proposals", result)
        print("Competitive analysis written: %s" % comp_path, file=sys.stderr)
        print("Brand proposals written: %s" % path, file=sys.stderr)
        print("Approve one with: python scripts/approve_brand.py --proposal A --root .", file=sys.stderr)
    elif args.brand_policy == "fallback":
        result = {
            "state": "unapproved_fallback",
            "policy": "fallback",
            "allow_unapproved_html": bool(args.allow_unapproved_html),
            "warning": "UNAPPROVED FALLBACK PROTOTYPE. Not client-presentable unless explicitly allowed.",
            "signals": signals,
        }
        path = store.write_new("brand-intake", result)
        print("Unsafe fallback artifact written: %s" % path, file=sys.stderr)
    elif has_explicit_brand(signals):
        result = {
            "state": "brand_intake_required",
            "policy": "strict",
            "required_user_action": ["Explicit assets were found, but a brand direction still requires approval."],
            "signals": signals,
        }
        path = store.write_new("brand-intake", result)
        print("Brand approval required: %s" % path, file=sys.stderr)
    else:
        result = build_intake(root, args.brand_policy, signals)
        errors = SchemaValidator().validate("brand-intake", result)
        if errors:
            print("Schema error: %s" % "; ".join(errors), file=sys.stderr)
            sys.exit(2)
        path = store.write_new("brand-intake", result)
        print("Brand intake required: %s" % path, file=sys.stderr)

    output = {
        "generated": date.today().isoformat(),
        "project_type": project_type,
        "state": result.get("state"),
        "policy": args.brand_policy,
        "raw_signals": signals,
        "brand_decisions": result if result.get("state") == "approved_brand" else None,
    }
    write_json(bridge / "brand-signals.json", output)
    write_brand_decisions(root, result if "signals" in result else {"state": result.get("state"), "signals": signals})

    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))

    if args.brand_policy == "strict" and not approved:
        print("ERROR: strict brand policy requires approved brand before continuing.", file=sys.stderr)
        sys.exit(1)
    if args.brand_policy == "fallback" and not args.allow_unapproved_html:
        print("WARNING: fallback is not approved for client-presentable HTML.", file=sys.stderr)


if __name__ == "__main__":
    main()
