
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .catalog import load_catalog
from .render import render_agent_readme, render_claude, render_instructions


def generated_files(root: Path, agent: dict[str, Any]) -> dict[Path, str]:
    base = root / "agents" / agent["id"]
    return {
        base / "agent.yaml": json.dumps(agent, indent=2, ensure_ascii=False) + "\n",
        base / "instructions.md": render_instructions(agent),
        base / "AGENT.md": render_claude(agent, preload_skills=False),
        base / "README.md": render_agent_readme(agent),
    }


def sync(root: Path, check: bool = False) -> list[str]:
    changed: list[str] = []
    for agent in load_catalog(root)["agents"]:
        for path, expected in generated_files(root, agent).items():
            actual = path.read_text(encoding="utf-8") if path.exists() else None
            if actual != expected:
                changed.append(str(path.relative_to(root)))
                if not check:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(expected, encoding="utf-8", newline="\n")
    return changed
