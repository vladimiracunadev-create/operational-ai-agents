#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target="${1:-$HOME/.claude/agents}"
mkdir -p "$target"
conflicts=0
for source in "$repo_root"/agents/*/AGENT.md; do
  agent_id="$(basename "$(dirname "$source")")"
  destination="$target/$agent_id.md"
  if [[ -e "$destination" && ! -L "$destination" ]] && ! grep -q "managed-by: operational-ai-agents" "$destination"; then
    echo "CONFLICTO: se preservó $destination" >&2
    conflicts=1
    continue
  fi
  rm -f "$destination"
  if ! ln -s "$source" "$destination" 2>/dev/null; then
    cp "$source" "$destination"
  fi
done
if [[ "$conflicts" -ne 0 ]]; then
  exit 2
fi
echo "Instalados en: $target"
