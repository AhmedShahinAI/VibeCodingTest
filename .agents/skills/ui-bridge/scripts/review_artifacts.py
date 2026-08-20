"""
Dedicated reviewer agents for UI Bridge artifacts and HTML.

Severity rules:
- critical: block
- major: block unless auto_fixed=true
- minor/suggestion: report only
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

from anti_slop_database import AntiSlopDatabase
from ui_bridge_core import ensure_bridge, read_json, review_passes, severity_counts, utc_now, write_json


GENERIC_TEXT = [
    "John Doe",
    "Jane Doe",
    "Course 1",
    "500+",
    "99%",
    "24/7",
    "Get Started Today",
    "Transform your business",
    "course title",
    "specific Arabic value proposition",
    "proof statement",
]
GENERIC_PATTERNS = ["hero cards cta footer", "problem proof cta", "three cards", "centered everything"]
EDTECH_ONLY_REFS = ["Harvard Online", "MIT Professional Education", "MasterClass", "Coursera for Business", "LinkedIn Learning"]


class BaseReviewer:
    name = "Base Reviewer"

    def review(self, path: Path, text: str, data: Any | None) -> List[Dict[str, Any]]:
        return []

    def finding(self, severity: str, id_: str, message: str, auto_fixed: bool = False) -> Dict[str, Any]:
        return {
            "reviewer": self.name,
            "severity": severity,
            "id": id_,
            "message": message,
            "auto_fixed": auto_fixed,
        }


class LayoutReviewer(BaseReviewer):
    name = "Layout Reviewer"

    def review(self, path: Path, text: str, data: Any | None) -> List[Dict[str, Any]]:
        findings = []
        if path.name.startswith("layout-dna") and isinstance(data, dict):
            if data.get("symmetry") in ("high", "very high"):
                findings.append(self.finding("major", "high_symmetry", "Layout DNA allows too much symmetry."))
            if "center" in str(data.get("alignment_style", "")).lower() and "mixed" not in str(data.get("alignment_style", "")).lower():
                findings.append(self.finding("major", "centered_alignment", "Alignment style risks centered-everything layouts."))
            assignments = data.get("page_assignments", {})
            if len(assignments) > 1 and len({str(v) for v in assignments.values()}) <= 1:
                findings.append(self.finding("major", "static_layout_assignments", "Layout assignments are not meaningfully page-specific."))
        if path.suffix.lower() == ".html":
            class_values = re.findall(r'class=["\']([^"\']+)["\']', text, re.IGNORECASE)
            repeated_names = {}
            for value in class_values:
                for cls in value.split():
                    if re.search(r"(?:^|[-_])(card|feature)(?:$|[-_])", cls, re.IGNORECASE):
                        repeated_names[cls] = repeated_names.get(cls, 0) + 1
            if any(count >= 6 for count in repeated_names.values()):
                findings.append(self.finding("major", "repeated_cards", "Repeated card structure detected."))
        if path.suffix.lower() == ".html" and re.search(r"<section\b[^>]*>\s*</section>", text, re.IGNORECASE):
            findings.append(self.finding("critical", "empty_sections", "HTML contains empty section shells."))
        if path.suffix.lower() == ".html" and "data-content-slot" in text:
            findings.append(self.finding("critical", "unfilled_stage_slots", "HTML still contains unfilled stage content slots."))
        return findings


class TypographyReviewer(BaseReviewer):
    name = "Typography Reviewer"

    def review(self, path: Path, text: str, data: Any | None) -> List[Dict[str, Any]]:
        findings = []
        if re.search(r"font-family\s*:\s*['\"]?Inter['\"]?\s*;", text, re.IGNORECASE):
            findings.append(self.finding("major", "inter_only", "Inter appears as sole font choice."))
        if re.search(r"letter-spacing\s*:\s*-\d", text, re.IGNORECASE):
            findings.append(self.finding("minor", "negative_tracking", "Negative tracking should be reserved for large display text only."))
        return findings


class BrandReviewer(BaseReviewer):
    name = "Brand Reviewer"

    def review(self, path: Path, text: str, data: Any | None) -> List[Dict[str, Any]]:
        findings = []
        if path.name.startswith("design-system") and isinstance(data, dict):
            if not data.get("approved_brand"):
                findings.append(self.finding("critical", "missing_approved_brand", "Design system is not tied to approved brand."))
        if path.name.startswith("brand-proposals") and isinstance(data, dict):
            if data.get("project_type", {}).get("category") in (None, "", "unknown"):
                findings.append(self.finding("major", "unknown_project_type", "Brand proposals are not tied to inferred project type."))
            text_lower = text.lower()
            for ref in EDTECH_ONLY_REFS:
                if ref.lower() in text_lower and data.get("project_type", {}).get("category") != "EdTech":
                    findings.append(self.finding("major", "domain_biased_reference", "Proposal contains an education-specific reference outside EdTech: %s" % ref))
        if "unapproved_fallback" in text and "UNAPPROVED FALLBACK PROTOTYPE" not in text:
            findings.append(self.finding("critical", "unmarked_fallback", "Fallback output is not visibly marked."))
        return findings


class ContentRealismReviewer(BaseReviewer):
    name = "Content Realism Reviewer"

    def review(self, path: Path, text: str, data: Any | None) -> List[Dict[str, Any]]:
        findings = []
        if path.name.startswith("content-realism") and isinstance(data, dict):
            forbidden = " ".join(data.get("forbidden", []))
            if not forbidden:
                findings.append(self.finding("critical", "missing_forbidden_content", "Content realism artifact has no forbidden content list."))
            return findings
        for item in GENERIC_TEXT:
            if item.lower() in text.lower():
                findings.append(self.finding("critical", "generic_content", "Generic/placeholder content found: %s" % item))
        return findings


class NarrativeReviewer(BaseReviewer):
    name = "Narrative Reviewer"

    def review(self, path: Path, text: str, data: Any | None) -> List[Dict[str, Any]]:
        findings = []
        lowered = text.lower()
        is_rule_artifact = isinstance(data, dict) and (
            "patterns_to_avoid" in data
            or "anti_repetition_rules" in data
            or "competitive_basis" in lowered
            or path.name.startswith("brand-proposals")
        )
        if not is_rule_artifact and any(p in lowered for p in GENERIC_PATTERNS):
            findings.append(self.finding("major", "generic_narrative", "Generic narrative/layout pattern detected."))
        if path.name.startswith("narrative-patterns") and isinstance(data, dict):
            patterns = data.get("patterns", [])
            if len(set(patterns)) < 5:
                findings.append(self.finding("major", "low_narrative_diversity", "Narrative artifact needs at least five distinct patterns."))
            if "assignment_logic" not in data:
                findings.append(self.finding("major", "missing_narrative_logic", "Narrative assignments need page-purpose logic, not positional rotation."))
        if path.name.startswith(("hero-diversity", "section-diversity")) and isinstance(data, dict):
            assignments = data.get("page_assignments", {})
            if "assignment_logic" not in data:
                findings.append(self.finding("major", "missing_diversity_logic", "%s needs explicit assignment logic." % path.name))
            if len(assignments) >= 4:
                values = list(assignments.values())
                if len(set(values)) == len(values) and values[:4] == data.get("patterns", [])[:4]:
                    findings.append(self.finding("major", "round_robin_diversity", "%s appears to use positional round-robin assignment." % path.name))
        return findings


class AntiSlopReviewer(BaseReviewer):
    name = "Anti-Slop Reviewer"

    def __init__(self) -> None:
        self.db = AntiSlopDatabase()

    def review(self, path: Path, text: str, data: Any | None) -> List[Dict[str, Any]]:
        findings = []
        if path.suffix.lower() == ".json":
            if path.name.startswith("content-realism"):
                if isinstance(data, dict) and ("metrics_logic" not in data or "name_logic" not in data):
                    findings.append(self.finding("major", "weak_content_realism", "Content realism needs metric and naming logic, not only forbidden placeholders."))
                return findings
            lowered = text.lower()
            for phrase in ("generic saas hero", "centered everything", "three-card syndrome"):
                if phrase in lowered and "patterns_to_avoid" not in lowered and "anti_repetition_rules" not in lowered:
                    findings.append(self.finding("major", "artifact_ai_tell", "Artifact contains an AI-tell without framing it as something to avoid: %s" % phrase))
            return findings
        result = self.db.check_html(text, str(path))
        for violation in result.get("violations", []):
            findings.append(self.finding("critical" if violation.get("severity") == "CRITICAL" else "major", violation.get("id", "slop"), violation.get("description", "")))
        for warning in result.get("warnings", []):
            findings.append(self.finding("minor", warning.get("id", "slop_warning"), warning.get("description", "")))
        for missing in result.get("missing_required", []):
            findings.append(self.finding("critical", "missing_required_element", "Required element missing from HTML: %s" % missing))
        return findings


class ImpeccableReviewer(BaseReviewer):
    name = "Impeccable Reviewer"

    def review(self, path: Path, text: str, data: Any | None) -> List[Dict[str, Any]]:
        findings = []
        if path.suffix.lower() == ".json":
            return findings
        if path.suffix.lower() == ".html":
            lower_head = text[:2000].lower()
            expects_arabic = 'lang="ar"' in lower_head or "lang='ar'" in lower_head or 'dir="rtl"' in lower_head or "dir='rtl'" in lower_head
            arabic_chars = sum(1 for ch in text if "\u0600" <= ch <= "\u06ff")
            mojibake_markers = sum(text.count(marker) for marker in ("Ø", "Ù", "Â", "â", "賲", "丕", "乇", "鬲"))
            if mojibake_markers:
                findings.append(self.finding("critical", "mojibake_text", "HTML contains mojibake text; encoding is corrupted."))
            if expects_arabic and arabic_chars < 40:
                findings.append(self.finding("critical", "missing_arabic_text", "Arabic/RTL HTML contains too few real Arabic Unicode characters."))
        if path.suffix.lower() == ".html" and re.search(r"<(?:link|script)\b[^>]+(?:href|src)=['\"]https?://", text, re.IGNORECASE):
            findings.append(self.finding("critical", "external_asset_reference", "Final HTML references external assets."))
        if path.suffix.lower() == ".html" and re.search(r"<img\b[^>]+src=['\"]https?://", text, re.IGNORECASE):
            findings.append(self.finding("critical", "external_image_reference", "Final HTML references external images."))
        unresolved_template = (
            "{{" in text
            or "}}" in text
            or re.search(r"\b(?:TODO|PLACEHOLDER|REPLACE_ME|TBD)\b", text)
        )
        if unresolved_template:
            findings.append(self.finding("critical", "template_placeholder", "Unresolved template placeholder found."))
        if path.suffix.lower() == ".html" and "<!DOCTYPE html>" not in text:
            findings.append(self.finding("critical", "not_html_document", "Final HTML is missing <!DOCTYPE html>."))
        if path.suffix.lower() == ".html" and not re.search(r"<main\b|role=['\"]main['\"]", text, re.IGNORECASE):
            findings.append(self.finding("critical", "missing_main_landmark", "Final HTML is missing the main landmark."))
        if path.suffix.lower() == ".html" and "UNAPPROVED FALLBACK PROTOTYPE" in text and "draft-watermark" not in text:
            findings.append(self.finding("critical", "weak_fallback_watermark", "Fallback watermark is not visible markup."))
        return findings


REVIEWERS = [
    LayoutReviewer(),
    TypographyReviewer(),
    BrandReviewer(),
    ContentRealismReviewer(),
    NarrativeReviewer(),
    AntiSlopReviewer(),
    ImpeccableReviewer(),
]


def load_data(path: Path) -> Any | None:
    if path.suffix.lower() != ".json":
        return None
    return read_json(path, default=None)


def main() -> None:
    parser = argparse.ArgumentParser(description="Review artifacts/HTML with dedicated reviewers")
    parser.add_argument("--root", default=".")
    parser.add_argument("--max-review-fix-rounds", type=int, default=2)
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    review_dir = ensure_bridge(root) / "reviews"
    review_dir.mkdir(exist_ok=True)

    all_findings = []
    reviewed = []
    for raw in args.paths:
        path = Path(raw)
        if not path.exists():
            all_findings.append({
                "reviewer": "Artifact Reviewer",
                "severity": "critical",
                "id": "missing_file",
                "message": "%s does not exist" % path,
                "auto_fixed": False,
            })
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        data = load_data(path)
        reviewed.append(str(path))
        for reviewer in REVIEWERS:
            all_findings.extend(reviewer.review(path, text, data))

    report = {
        "reviewer": "combined",
        "reviewers": [r.name for r in REVIEWERS],
        "generated_at": utc_now(),
        "reviewed": reviewed,
        "max_review_fix_rounds": args.max_review_fix_rounds,
        "severity_counts": severity_counts(all_findings),
        "findings": all_findings,
        "passes": review_passes(all_findings),
    }
    out = review_dir / "review-report.json"
    write_json(out, report)

    if not report["passes"]:
        print("Review failed. Blocking findings written to %s" % out, file=sys.stderr)
        sys.exit(1)
    print("Review passed. Report written to %s" % out)


if __name__ == "__main__":
    main()
