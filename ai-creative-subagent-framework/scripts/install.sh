#!/bin/bash
# ai-creative-subagent-framework — Cross-platform install script
# Usage: bash scripts/install.sh [harness]
# Supported harnesses: claude-code | claude-desktop | codex-cli | openclaw | hermes

SKILL_NAME="ai-creative-subagent-framework"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

detect_harness() {
  if command -v claude &>/dev/null; then echo "claude-code"; return 0; fi
  if command -v codex &>/dev/null; then echo "codex-cli"; return 0; fi
  if command -v openclaw &>/dev/null; then echo "openclaw"; return 0; fi
  if [ -d "$HOME/.hermes" ]; then echo "hermes"; return 0; fi
  echo "unknown"
}

INSTALL_HARNESS="${1:-$(detect_harness)}"

case "$INSTALL_HARNESS" in
  claude-code|claude-desktop)
    TARGET="$HOME/.claude/skills/$SKILL_NAME"
    mkdir -p "$(dirname "$TARGET")"
    cp -r "$SCRIPT_DIR" "$TARGET"
    echo "✅ Installed to: $TARGET"
    echo "   Activate in Claude Code: claude skills list"
    ;;
  codex-cli)
    TARGET="$HOME/.agents/skills/$SKILL_NAME"
    mkdir -p "$(dirname "$TARGET")"
    cp -r "$SCRIPT_DIR" "$TARGET"
    echo "✅ Installed to: $TARGET"
    echo "   Activate in Codex CLI: codex skills list"
    ;;
  openclaw)
    TARGET="$HOME/.openclaw/skills/$SKILL_NAME"
    mkdir -p "$(dirname "$TARGET")"
    cp -r "$SCRIPT_DIR" "$TARGET"
    echo "✅ Installed to: $TARGET"
    echo "   Register: openclaw skill register $SKILL_NAME"
    ;;
  hermes)
    TARGET="$HOME/.hermes/skills/$SKILL_NAME"
    mkdir -p "$(dirname "$TARGET")"
    cp -r "$SCRIPT_DIR" "$TARGET"
    echo "✅ Installed to: $TARGET"
    echo "   Activate by using trigger keywords in conversation"
    ;;
  *)
    echo "❌ Unknown harness: $INSTALL_HARNESS"
    echo "Usage: bash scripts/install.sh [claude-code|claude-desktop|codex-cli|openclaw|hermes]"
    echo "Detected: $(detect_harness)"
    exit 1
    ;;
esac
