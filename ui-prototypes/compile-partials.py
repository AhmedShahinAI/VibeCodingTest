from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
PARTIALS = ROOT / "_partials"
MARKER_RE = re.compile(r"<!-- PARTIAL:([a-z0-9-]+) -->(.*?)<!-- /PARTIAL:\1 -->", re.DOTALL)


def partial_text(name: str) -> str:
    path = PARTIALS / f"{name}.html"
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


def stamp_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    changed = False

    def repl(match):
        nonlocal changed
        name = match.group(1)
        replacement = partial_text(name)
        changed = True
        return f"<!-- PARTIAL:{name} -->\n{replacement}\n<!-- /PARTIAL:{name} -->"

    updated = MARKER_RE.sub(repl, original)
    if changed and updated != original:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def main():
    for html_path in sorted(ROOT.glob("*.html")):
        if html_path.name == "prototype-hub.html":
            continue
        stamp_file(html_path)


if __name__ == "__main__":
    main()
