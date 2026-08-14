
from __future__ import annotations

from pathlib import Path
from typing import Any

from .render import render_claude


def export_claude(agents: list[dict[str, Any]], target: Path, preload_skills: bool = False) -> list[Path]:
    target = target.expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for agent in agents:
        path = target / f"{agent['id']}.md"
        if path.exists() and not path.is_symlink():
            existing = path.read_text(encoding="utf-8", errors="replace")
            if "managed-by: operational-ai-agents" not in existing:
                raise FileExistsError(f"Se preservó un agente no administrado: {path}")
        if path.is_symlink():
            path.unlink()
        path.write_text(render_claude(agent, preload_skills=preload_skills), encoding="utf-8", newline="\n")
        written.append(path)
    return written


def uninstall_claude(agents: list[dict[str, Any]], target: Path) -> list[Path]:
    removed: list[Path] = []
    for agent in agents:
        path = target.expanduser().resolve() / f"{agent['id']}.md"
        managed = False
        if path.is_symlink():
            managed = True
        elif path.is_file():
            managed = "managed-by: operational-ai-agents" in path.read_text(encoding="utf-8", errors="replace")
        if managed:
            path.unlink()
            removed.append(path)
    return removed
