#!/bin/bash
# install.sh - Install ui-generate-from-plan skill (Mac / Linux)

set -e

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_NAME="ui-gernreate-from-plan"
CLAUDE_GLOBAL="$HOME/.claude"
CODEX_GLOBAL="${CODEX_HOME:-$HOME/.codex}"
CLAUDE_LOCAL=".claude"
CODEX_LOCAL=".codex"

copy_skill_files() {
  local dest="$1"
  mkdir -p "$dest"

  for item in SKILL.md README.md requirements.txt package.json; do
    if [ -e "$SKILL_DIR/$item" ]; then
      cp "$SKILL_DIR/$item" "$dest/"
    fi
  done

  for dir in scripts subskills references templates agents .claude .codex; do
    if [ -d "$SKILL_DIR/$dir" ]; then
      rm -rf "$dest/$dir"
      cp -R "$SKILL_DIR/$dir" "$dest/"
    fi
  done
}

echo "Installing $SKILL_NAME skill..."

copy_skill_files "$CLAUDE_GLOBAL/skills/$SKILL_NAME"
echo "  OK Claude skill files copied to $CLAUDE_GLOBAL/skills/$SKILL_NAME/"

copy_skill_files "$CODEX_GLOBAL/skills/$SKILL_NAME"
echo "  OK Codex skill files copied to $CODEX_GLOBAL/skills/$SKILL_NAME/"

mkdir -p "$CLAUDE_GLOBAL/commands"
cp "$SKILL_DIR/.claude/commands/"*.md "$CLAUDE_GLOBAL/commands/"
echo "  OK Claude commands installed to $CLAUDE_GLOBAL/commands/"

mkdir -p "$CLAUDE_LOCAL/commands"
cp "$SKILL_DIR/.claude/commands/"*.md "$CLAUDE_LOCAL/commands/"
echo "  OK Project Claude commands installed to $CLAUDE_LOCAL/commands/"

mkdir -p "$CODEX_GLOBAL/skills"
cp -R "$SKILL_DIR/.codex/skills/"* "$CODEX_GLOBAL/skills/"
echo "  OK Codex alias skills installed to $CODEX_GLOBAL/skills/"

mkdir -p "$CODEX_LOCAL/skills"
cp -R "$SKILL_DIR/.codex/skills/"* "$CODEX_LOCAL/skills/"
echo "  OK Project Codex alias skills installed to $CODEX_LOCAL/skills/"

if command -v python3 > /dev/null 2>&1; then
  echo "  OK Python3 found: $(python3 --version)"
elif command -v python > /dev/null 2>&1; then
  echo "  OK Python found: $(python --version)"
else
  echo "  WARN python3 not found -- install Python 3.8+ from https://python.org"
fi

if command -v npx > /dev/null 2>&1; then
  echo "Installing Impeccable (optional validation layer)..."
  npx impeccable install --providers=claude 2>/dev/null || true
  echo "  OK Impeccable checked"
else
  echo "  WARN npx not found -- Impeccable CLI validation disabled"
fi

echo ""
echo "OK $SKILL_NAME installed successfully"
echo ""
echo "Restart your agent, then use:"
echo "  /ui-plan or \$ui-plan"
echo "  /ui-implement or \$ui-implement"
echo "  /ui-link-html-to-plan or \$ui-link-html-to-plan"
echo "  /ui-into-preview or \$ui-into-preview"
echo ""
echo "Docs: https://github.com/rakymat-plugins/ui-gernreate-from-plan"
