#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target="${1:-$HOME/.claude/agents}"
removed=0
for source in "$repo_root"/agents/*/AGENT.md; do
  agent_id="$(basename "$(dirname "$source")")"
  destination="$target/$agent_id.md"
  if [[ -L "$destination" ]]; then
    rm "$destination"
    removed=$((removed + 1))
  elif [[ -f "$destination" ]] && grep -q "managed-by: operational-ai-agents" "$destination"; then
    rm "$destination"
    removed=$((removed + 1))
  fi
done
echo "Eliminados $removed agentes administrados"
