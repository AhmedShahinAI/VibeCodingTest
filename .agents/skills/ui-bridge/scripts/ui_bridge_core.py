"""
Shared UI Bridge workflow primitives.

This module is intentionally stdlib-only so every script can import it. It holds
the policy that must not drift between detection, parsing, brand extraction,
page mapping, approvals, and implementation gates.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


ARTIFACT_NAMES = ("plan.md", "tasks.md", "spec.md")

BLOCKED_DIRS = frozenset(
    [
        ".claude",
        ".codex",
        ".git",
        ".next",
        ".nuxt",
        ".output",
        ".specify",
        ".ui-bridge",
        "__pycache__",
        "build",
        "coverage",
        "dist",
        "node_modules",
        "references",
        "templates",
        "ui-prototypes",
        "ui-gernreate-from-plan",
    ]
)

REAL_SOURCE_DIRS = frozenset(
    [
        "app",
        "apps",
        "assets",
        "components",
        "docs",
        "img",
        "images",
        "public",
        "src",
        "static",
        "styles",
    ]
)

ROOT_SOURCE_FILES = (
    "PRD.md",
    "README.md",
    "package.json",
    "tailwind.config.js",
    "tailwind.config.mjs",
    "tailwind.config.ts",
    "vite.config.js",
    "vite.config.ts",
)

PHASE_RE = re.compile(
    r"^#{2,3}\s+Phase\s+([0-9A-Za-z]+)(?:\s*[:\-\u2014].*)?$",
    re.IGNORECASE | re.MULTILINE,
)


def utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def ensure_bridge(root: Path) -> Path:
    out = Path(root) / ".ui-bridge"
    out.mkdir(exist_ok=True)
    return out


def relative_posix(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def contains_blocked_part(path: Path) -> bool:
    return any(part in BLOCKED_DIRS for part in path.parts)


def is_real_project_source(path: Path, root: Path) -> bool:
    rel_parts = path.relative_to(root).parts
    if contains_blocked_part(Path(*rel_parts)):
        return False
    if not rel_parts:
        return False
    first = rel_parts[0]
    name = path.name
    if first == "specs":
        return True
    if first in REAL_SOURCE_DIRS:
        return True
    if name in ROOT_SOURCE_FILES:
        return True
    lower = name.lower()
    return lower.startswith("brand") or lower.startswith("logo")


def iter_real_source_files(root: Path, extensions: Iterable[str]) -> Iterable[Path]:
    root = Path(root).resolve()
    wanted = {e.lower() for e in extensions}
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        try:
            rel_parts = current.relative_to(root).parts
        except ValueError:
            rel_parts = current.parts
        dirnames[:] = [d for d in dirnames if d not in BLOCKED_DIRS]
        if any(part in BLOCKED_DIRS for part in rel_parts):
            dirnames[:] = []
            continue
        for filename in filenames:
            path = current / filename
            if path.suffix.lower() not in wanted:
                continue
            if is_real_project_source(path, root):
                yield path


def file_sha256(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_phase_headings(content: str) -> List[str]:
    phases = []
    for match in PHASE_RE.finditer(content):
        full = match.group(0).lstrip("#").strip()
        phases.append(full)
    return phases


class SpecKitResolver:
    """Resolve Spec Kit artifacts consistently for every script."""

    def __init__(self, root: Path):
        self.root = Path(root).resolve()

    def resolve_all(self, allow_ambiguous: bool = False) -> Dict[str, Optional[str]]:
        result: Dict[str, Optional[str]] = {}
        for name in ARTIFACT_NAMES:
            found = self.find(name, allow_ambiguous=allow_ambiguous)
            result[name.replace(".md", "")] = str(found) if found else None
        return result

    def find(self, filename: str, allow_ambiguous: bool = False) -> Optional[Path]:
        candidates: List[Path] = []
        direct = self.root / filename
        if direct.exists():
            candidates.append(direct)

        feature_dir = self._feature_directory()
        if feature_dir:
            p = self.root / feature_dir / filename
            if p.exists():
                candidates.append(p)

        specs = self.root / "specs"
        if specs.is_dir():
            candidates.extend(sorted(specs.rglob(filename)))

        specify = self.root / ".specify" / filename
        if specify.exists():
            candidates.append(specify)

        unique: List[Path] = []
        seen = set()
        for candidate in candidates:
            resolved = candidate.resolve()
            if resolved not in seen and not contains_blocked_part(candidate.relative_to(self.root)):
                seen.add(resolved)
                unique.append(resolved)

        if not unique:
            return None
        if len(unique) > 1 and not allow_ambiguous:
            preferred = self._prefer_same_feature(unique)
            if preferred:
                return preferred
            listed = ", ".join(relative_posix(p, self.root) for p in unique)
            raise RuntimeError("Ambiguous %s artifacts found: %s" % (filename, listed))
        return unique[0]

    def _feature_directory(self) -> Optional[str]:
        feature_json = self.root / ".specify" / "feature.json"
        if not feature_json.exists():
            return None
        try:
            data = json.loads(feature_json.read_text(encoding="utf-8"))
            return data.get("feature_directory")
        except Exception:
            return None

    def _prefer_same_feature(self, candidates: List[Path]) -> Optional[Path]:
        feature_dir = self._feature_directory()
        if not feature_dir:
            return None
        expected = (self.root / feature_dir).resolve()
        for candidate in candidates:
            try:
                candidate.relative_to(expected)
                return candidate
            except ValueError:
                continue
        return None


class ApprovalStore:
    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.path = ensure_bridge(self.root) / "approvals.json"

    def data(self) -> Dict[str, Any]:
        return read_json(self.path, default={}) or {}

    def approve(self, key: str, version: str, approved_by: str = "user", extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        data = self.data()
        item = {
            "approved": True,
            "version": version,
            "approved_at": utc_now(),
            "approved_by": approved_by,
        }
        if extra:
            item.update(extra)
        data[key] = item
        write_json(self.path, data)
        return data

    def is_approved(self, key: str, version: Optional[str] = None) -> bool:
        item = self.data().get(key, {})
        if not item.get("approved"):
            return False
        if version and item.get("version") != version:
            return False
        return True

    def require(self, keys: Iterable[str]) -> List[str]:
        missing = []
        for key in keys:
            if not self.is_approved(key):
                missing.append(key)
        return missing


class VersionedArtifacts:
    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.bridge = ensure_bridge(self.root)
        self.latest_path = self.bridge / "latest.json"

    def next_path(self, basename: str) -> Path:
        index = 1
        while (self.bridge / ("%s.v%d.json" % (basename, index))).exists():
            index += 1
        return self.bridge / ("%s.v%d.json" % (basename, index))

    def write_new(self, basename: str, data: Dict[str, Any]) -> Path:
        path = self.next_path(basename)
        version = re.search(r"\.v(\d+)\.json$", path.name).group(1)
        data = dict(data)
        data.setdefault("version", "v" + version)
        data.setdefault("generated_at", utc_now())
        write_json(path, data)
        latest = read_json(self.latest_path, default={}) or {}
        latest[basename] = path.name
        write_json(self.latest_path, latest)
        return path


class SchemaValidator:
    FORBIDDEN_BRAND_COLORS = {
        "#1E40AF", "#0EA5E9", "#F8FAFC", "#F9FAFB", "#F3F4F6", "#F1F5F9",
        "#6366F1", "#4F46E5", "#7C3AED", "#8B5CF6", "#10B981", "#059669",
    }
    FORBIDDEN_BRAND_FONTS = {
        "inter", "cairo", "tajawal", "plus jakarta sans", "poppins", "dm sans",
        "geist", "system-ui", "arial", "helvetica",
    }
    REQUIRED_KEYS = {
        "brand-intake": ["state", "policy", "required_user_action", "signals"],
        "brand-proposals": ["state", "directions"],
        "approvals": [],
        "competitive-analysis": ["patterns_to_copy", "patterns_to_avoid", "hero_types", "section_types", "copy_tone", "spacing_observations"],
        "moodboard": ["photography", "density", "card_style", "spacing_style", "icon_style", "color_temperature"],
        "visual-dna": ["personality", "geometry", "density", "motion", "contrast", "photography_style", "iconography"],
        "layout-dna": ["state", "symmetry", "editorialness", "card_density", "grid_style", "alignment_style", "section_rhythm", "asymmetry_level", "page_assignments"],
        "photography-system": ["style", "aspect_ratios", "color_grading", "background_style", "portrait_rules"],
        "iconography-system": ["style", "stroke_width", "corner_radius", "density", "placement"],
        "hero-diversity": ["patterns", "page_assignments", "anti_repetition_rules"],
        "component-personality": ["buttons", "cards", "badges", "stats", "forms", "tables"],
        "content-realism": ["numbers", "names", "titles", "testimonials", "forbidden"],
        "narrative-patterns": ["patterns", "page_assignments", "anti_repetition_rules"],
        "section-diversity": ["patterns", "page_assignments", "anti_repetition_rules"],
        "design-system": ["approved_brand", "colors", "typography"],
        "review-report": ["reviewer", "severity_counts", "findings", "passes"],
    }

    def validate(self, artifact_type: str, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not isinstance(data, dict):
            return ["%s must be a JSON object" % artifact_type]
        for key in self.REQUIRED_KEYS.get(artifact_type, []):
            if key not in data:
                errors.append("%s missing required key: %s" % (artifact_type, key))
        if errors:
            return errors
        custom = getattr(self, "_validate_" + artifact_type.replace("-", "_"), None)
        if custom:
            errors.extend(custom(data))
        return errors

    def _validate_brand_intake(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if data.get("state") not in ("approved_brand", "brand_intake_required", "inferred_proposal", "unapproved_fallback"):
            errors.append("brand-intake state is invalid")
        if data.get("policy") not in ("strict", "proposal", "fallback"):
            errors.append("brand-intake policy is invalid")
        signals = data.get("signals")
        if not isinstance(signals, dict):
            errors.append("brand-intake signals must be an object, never an array")
            return errors
        required_signal_keys = {
            "hex_colors": list,
            "css_variables": list,
            "font_families": list,
            "google_fonts": list,
            "tailwind_colors": dict,
            "logos": list,
            "rtl_detected": bool,
            "arabic_detected": bool,
        }
        for key, expected in required_signal_keys.items():
            if key not in signals:
                errors.append("brand-intake signals missing %s" % key)
            elif not isinstance(signals[key], expected):
                errors.append("brand-intake signals.%s must be %s" % (key, expected.__name__))
        actions = data.get("required_user_action", [])
        if data.get("state") == "brand_intake_required" and (not isinstance(actions, list) or not actions):
            errors.append("brand-intake required_user_action must explain the blocking user action")
        return errors

    def _validate_brand_proposals(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        directions = data.get("directions")
        if not isinstance(directions, list) or len(directions) != 3:
            return ["brand-proposals must contain exactly three directions"]
        required = ["id", "name", "palette", "fonts", "references", "photography", "iconography", "density", "personality", "layout_style", "hero_style", "cta_tone", "competitive_basis"]
        seen_ids = set()
        for idx, direction in enumerate(directions):
            if not isinstance(direction, dict):
                errors.append("brand-proposals direction %d must be object" % idx)
                continue
            missing = [key for key in required if key not in direction]
            for key in missing:
                errors.append("brand-proposals direction %s missing %s" % (direction.get("id", idx), key))
            seen_ids.add(direction.get("id"))
            palette = direction.get("palette", {})
            if not isinstance(palette, dict):
                errors.append("brand-proposals direction %s palette must be object" % direction.get("id", idx))
            elif not all(palette.get(k) for k in ("primary", "accent", "background", "surface", "text")):
                errors.append("brand-proposals direction %s palette incomplete" % direction.get("id", idx))
            else:
                for role, value in palette.items():
                    if isinstance(value, str) and value.upper() in self.FORBIDDEN_BRAND_COLORS:
                        errors.append("brand-proposals direction %s uses forbidden generic color %s for %s" % (direction.get("id", idx), value, role))
            fonts = direction.get("fonts", {})
            if not isinstance(fonts, dict):
                errors.append("brand-proposals direction %s fonts must be object" % direction.get("id", idx))
            else:
                for role, value in fonts.items():
                    if isinstance(value, str) and value.lower() in self.FORBIDDEN_BRAND_FONTS:
                        errors.append("brand-proposals direction %s uses forbidden generic font %s for %s" % (direction.get("id", idx), value, role))
        if seen_ids != {"A", "B", "C"}:
            errors.append("brand-proposals direction ids must be A, B, C")
        return errors

    def _validate_layout_dna(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        allowed = {
            "symmetry": {"low", "low-to-medium", "medium", "medium-to-high"},
            "editorialness": {"low", "medium", "high"},
            "card_density": {"low", "medium", "high"},
            "asymmetry_level": {"low", "medium", "high"},
        }
        for key, values in allowed.items():
            if data.get(key) not in values:
                errors.append("layout-dna %s invalid: %s" % (key, data.get(key)))
        if not isinstance(data.get("page_assignments"), dict) or not data.get("page_assignments"):
            errors.append("layout-dna page_assignments must map pages to layout rules")
        for key in ("grid_style", "alignment_style", "section_rhythm"):
            if not isinstance(data.get(key), str) or len(data.get(key, "")) < 12:
                errors.append("layout-dna %s is too vague" % key)
        return errors

    def _validate_review_report(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        counts = data.get("severity_counts", {})
        if not isinstance(counts, dict):
            errors.append("review-report severity_counts must be object")
        else:
            for key in ("critical", "major", "minor", "suggestion"):
                if not isinstance(counts.get(key), int):
                    errors.append("review-report severity_counts.%s must be integer" % key)
        if not isinstance(data.get("findings"), list):
            errors.append("review-report findings must be an array")
        else:
            for idx, finding in enumerate(data["findings"]):
                if not isinstance(finding, dict):
                    errors.append("review-report finding %d must be object" % idx)
                    continue
                if finding.get("severity") not in ("critical", "major", "minor", "suggestion"):
                    errors.append("review-report finding %d has invalid severity" % idx)
                for key in ("reviewer", "id", "message"):
                    if not isinstance(finding.get(key), str) or not finding.get(key):
                        errors.append("review-report finding %d missing %s" % (idx, key))
                if not isinstance(finding.get("auto_fixed"), bool):
                    errors.append("review-report finding %d auto_fixed must be boolean" % idx)
        if not isinstance(data.get("passes"), bool):
            errors.append("review-report passes must be boolean")
        return errors


SEVERITY_BLOCKS = {
    "critical": True,
    "major": True,
    "minor": False,
    "suggestion": False,
}


def review_passes(findings: List[Dict[str, Any]]) -> bool:
    for finding in findings:
        severity = str(finding.get("severity", "minor")).lower()
        if SEVERITY_BLOCKS.get(severity, False) and not finding.get("auto_fixed", False):
            return False
    return True


def severity_counts(findings: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {"critical": 0, "major": 0, "minor": 0, "suggestion": 0}
    for finding in findings:
        severity = str(finding.get("severity", "minor")).lower()
        counts[severity] = counts.get(severity, 0) + 1
    return counts
