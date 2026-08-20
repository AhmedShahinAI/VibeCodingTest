"""
update_plan.py - Safely insert UI Phase 0 into plan.md and tasks.md.

Usage:
    python scripts/update_plan.py [--root PATH]

Reads:
    .ui-bridge/parsed-speckit.json
    .ui-bridge/page-map.json

Creates backups before modifying:
    plan.md.backup
    tasks.md.backup
    .ui-bridge/backups/*.backup

Also writes:
    .ui-bridge/phase0-plan.md
    .ui-bridge/phase0-tasks.md
    .ui-bridge/phase0-plan.json
"""
import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


PHASE_0_EXISTS_RE = re.compile(r"^##\s+Phase\s+0\b", re.MULTILINE)
FIRST_PHASE_RE = re.compile(r"^(##\s+(?:Phase\s+[1-9]|Setup|Foundational))", re.MULTILINE)
NEXT_TOP_LEVEL_AFTER_PHASE0_RE = re.compile(r"^##\s+(?!Phase\s+0\b).+", re.MULTILINE)


def utc_stamp() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def backup(path: Path) -> Path:
    backup_path = path.with_suffix(path.suffix + ".backup")
    shutil.copy2(path, backup_path)
    return backup_path


def backup_versioned(path: Path, bridge: Path) -> Path:
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    backup_dir = bridge / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    archive_path = backup_dir / f"{path.name}.{stamp}.backup"
    shutil.copy2(path, archive_path)
    return archive_path


def replace_existing_phase0(content: str, phase0_block: str) -> tuple[str, bool]:
    match = PHASE_0_EXISTS_RE.search(content)
    if not match:
        return content, False
    next_match = NEXT_TOP_LEVEL_AFTER_PHASE0_RE.search(content, match.end())
    if next_match:
        new_content = (
            content[:match.start()].rstrip()
            + "\n\n"
            + phase0_block.strip()
            + "\n\n---\n\n"
            + content[next_match.start():]
        )
    else:
        new_content = content[:match.start()].rstrip() + "\n\n" + phase0_block.strip() + "\n"
    return new_content, True


def safe_insert(file_path: Path, phase0_block: str, label: str, bridge: Path) -> str:
    if not file_path.exists():
        return f"ERROR: {label} not found at {file_path}"

    content = file_path.read_text(encoding="utf-8")
    backup_path = backup(file_path)
    archive_path = backup_versioned(file_path, bridge)

    new_content, replaced = replace_existing_phase0(content, phase0_block)
    appended = False
    if not replaced:
        match = FIRST_PHASE_RE.search(content)
        if match:
            insert_pos = match.start()
            new_content = (
                content[:insert_pos].rstrip()
                + "\n\n"
                + phase0_block.strip()
                + "\n\n---\n\n"
                + content[insert_pos:]
            )
        else:
            # No implementation-phase heading to insert before (this template
            # keeps phase breakdown in tasks.md instead) — append Phase 0 as
            # its own top-level section instead of failing.
            new_content = content.rstrip() + "\n\n---\n\n" + phase0_block.strip() + "\n"
            appended = True

    file_path.write_text(new_content, encoding="utf-8")
    verify = file_path.read_text(encoding="utf-8")
    if not PHASE_0_EXISTS_RE.search(verify):
        shutil.copy2(backup_path, file_path)
        return f"ERROR: Write verification failed for {label}. Backup restored from {backup_path}"

    action = "replaced" if replaced else ("appended" if appended else "inserted")
    return (
        f"OK: Phase 0 {action} in {label} "
        f"(backup at {backup_path.name}, archive at {archive_path.relative_to(bridge.parent)})"
    )


def generate_phase0_plan_block(pages: list, project_name: str) -> str:
    lines = [
        "## Phase 0 - UI Prototypes",
        "",
        f"**Project**: {project_name}",
        "**Goal**: Build approved HTML prototypes for every planned UI page before engineering implementation begins.",
        "**Execution rule**: complete this UI phase first. Do not mix Phase 0 prototype work with later engineering phases.",
        "",
        "**Generated foundations in this phase**:",
        "- Approved brand and direction artifacts in `.ui-bridge/`",
        "- Shared design system in `.ui-bridge/design-system.json`",
        "- Shared token stylesheet in `.ui-bridge/design-system.css` and `ui-prototypes/design-tokens.css`",
        "- Shared partials in `ui-prototypes/_partials/`",
        "- One approved HTML file per page in `ui-prototypes/`",
        "",
        "**Design token rule**: colors, typography, spacing, radius, shadow, and motion must resolve through CSS variables.",
        "**Phase ordering rule**: `/ui-implement` must follow the page order defined below, one page sub-phase at a time.",
        "",
        "---",
        "",
    ]

    for index, page in enumerate(pages, 1):
        slug = page.get("slug", "unknown")
        name = page.get("name", slug)
        html_output = page.get("html_output", f"ui-prototypes/{slug}.html")
        direction = page.get("direction", "ltr").upper()
        sections = page.get("sections", ["Main content"])
        page_type = "Admin" if page.get("is_admin") else "Public"

        lines += [
            f"### Phase 0.{index} - {name} -> `{html_output}`",
            "",
            f"**Page type**: {page_type}",
            f"**Direction**: {direction}",
            f"**Shared tokens**: `ui-prototypes/design-tokens.css`",
            f"**Reference source**: `.ui-bridge/page-map.json` -> `{slug}`",
            "",
            "Required section order:",
        ]
        for section_number, section in enumerate(sections, 1):
            lines.append(f"{section_number}. {section}")
        lines += [
            "",
            "Definition of done:",
            "- Approved HTML exists for this page.",
            "- Styling values are CSS-variable driven rather than hardcoded.",
            "- Shared navigation, footer, or sidebar content comes from project partials.",
            "",
        ]

    return "\n".join(lines)


def generate_phase0_tasks_block(pages: list) -> tuple[str, int, list[dict]]:
    task_count = 0
    metadata_pages = []
    lines = [
        "## Phase 0 - UI Prototypes",
        "",
        "**Execution rule**: finish the UI prototype phase first and in order before moving into later implementation phases.**",
        "**Granularity rule**: one sub-phase equals one page; one task equals one shared requirement or page section.**",
        "",
        "---",
        "",
    ]

    for index, page in enumerate(pages, 1):
        slug = page.get("slug", "unknown")
        name = page.get("name", slug)
        html_output = page.get("html_output", f"ui-prototypes/{slug}.html")
        sections = list(page.get("sections", ["Main content"]))
        is_admin = page.get("is_admin", False)
        us_tag = "[US2]" if is_admin else "[US1]"
        page_task_ids = []

        lines += [
            f"### Phase 0.{index} - {name} -> `{html_output}`",
            "",
        ]

        fixed_tasks = [
            f"T0-{index:02d}00",
            f"T0-{index:02d}01",
            f"T0-{index:02d}02",
        ]
        fixed_lines = [
            f"- [ ] {fixed_tasks[0]} [P] {us_tag} Create or update the shared HTML shell for `{slug}`",
            f"- [ ] {fixed_tasks[1]} [P] {us_tag} Ensure `{slug}` links `design-tokens.css` and copies required root tokens inline",
            f"- [ ] {fixed_tasks[2]} [P] {us_tag} Ensure `{slug}` uses CSS variables for color, type, spacing, radius, and motion",
        ]
        lines.extend(fixed_lines)
        page_task_ids.extend(fixed_tasks)
        task_count += len(fixed_lines)

        for section in sections:
            task_count += 1
            tid = f"T0-{200 + task_count:03d}"
            lines.append(f"- [ ] {tid} [P] {us_tag} Build section: {section} - `{html_output}`")
            page_task_ids.append(tid)

        end_tasks = [
            f"T0-{index:02d}98",
            f"T0-{index:02d}99",
        ]
        end_lines = [
            f"- [ ] {end_tasks[0]} [P] {us_tag} Stamp shared partials into `{slug}` and verify active navigation state",
            f"- [ ] {end_tasks[1]} [P] {us_tag} Publish the approved prototype file `{html_output}`",
            "",
        ]
        lines.extend(end_lines)
        page_task_ids.extend(end_tasks)
        task_count += 2

        metadata_pages.append(
            {
                "phase": f"0.{index}",
                "slug": slug,
                "name": name,
                "html_output": html_output,
                "is_admin": is_admin,
                "sections": sections,
                "task_ids": page_task_ids,
            }
        )

    return "\n".join(lines), task_count, metadata_pages


def main() -> None:
    parser = argparse.ArgumentParser(description="Insert UI Phase 0 into plan.md and tasks.md")
    parser.add_argument("--root", default=".", help="Project root path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    ui_bridge = root / ".ui-bridge"

    speckit_json = ui_bridge / "parsed-speckit.json"
    if not speckit_json.exists():
        print("ERROR: .ui-bridge/parsed-speckit.json not found. Run parse_speckit.py first.", file=sys.stderr)
        sys.exit(1)
    speckit = json.loads(speckit_json.read_text(encoding="utf-8"))

    plan_path = Path(speckit["found"]["plan"]) if speckit["found"].get("plan") else root / "plan.md"
    tasks_path = Path(speckit["found"]["tasks"]) if speckit["found"].get("tasks") else root / "tasks.md"
    project_name = speckit.get("plan", {}).get("project_name", "Project")

    page_map_json = ui_bridge / "page-map.json"
    if not page_map_json.exists():
        print("ERROR: .ui-bridge/page-map.json not found. Run generate_page_map.py first.", file=sys.stderr)
        sys.exit(1)
    page_map = json.loads(page_map_json.read_text(encoding="utf-8"))
    pages = page_map.get("pages", [])

    phase0_plan_block = generate_phase0_plan_block(pages, project_name)
    phase0_tasks_block, task_count, metadata_pages = generate_phase0_tasks_block(pages)

    phase0_plan_path = ui_bridge / "phase0-plan.md"
    phase0_tasks_path = ui_bridge / "phase0-tasks.md"
    phase0_json_path = ui_bridge / "phase0-plan.json"
    phase0_plan_path.write_text(phase0_plan_block, encoding="utf-8")
    phase0_tasks_path.write_text(phase0_tasks_block, encoding="utf-8")
    phase0_json_path.write_text(
        json.dumps(
            {
                "generated_at": utc_stamp(),
                "project_name": project_name,
                "page_count": len(pages),
                "pages": metadata_pages,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Phase 0 plan saved to {phase0_plan_path}", file=sys.stderr)
    print(f"Phase 0 tasks saved to {phase0_tasks_path}", file=sys.stderr)
    print(f"Phase 0 metadata saved to {phase0_json_path}", file=sys.stderr)

    result_plan = safe_insert(plan_path, phase0_plan_block, "plan.md", ui_bridge)
    result_tasks = safe_insert(tasks_path, phase0_tasks_block, "tasks.md", ui_bridge)

    print(result_plan, file=sys.stderr)
    print(result_tasks, file=sys.stderr)

    sub_phases = phase0_plan_block.count("### Phase 0.")
    print(f"Updated UI Phase 0: {sub_phases} page sub-phases, {task_count} tasks", file=sys.stderr)

    if "ERROR" in result_plan or "ERROR" in result_tasks:
        sys.exit(1)


if __name__ == "__main__":
    main()
