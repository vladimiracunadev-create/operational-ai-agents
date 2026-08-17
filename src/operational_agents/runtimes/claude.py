
"""Adaptador de Claude Code: el primer runtime, y el único con ejecución autónoma demostrada.

Traduce el contrato a la invocación del CLI ya instalado. No añade ninguna
bandera que omita permisos: los gates que el runtime pide siguen intactos.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from .base import COMPLETED, FAILED, AgentRuntime, Detection, ExecutionResult, Preparation, RuntimeCapabilities, RuntimeDescriptor

# Cada capacidad se apoya en una tool nativa del runtime. La tabla es la única
# parte del sistema que necesita conocer estos nombres.
TOOL_MAPPING = {
    "filesystem.read": "Read",
    "filesystem.find": "Glob",
    "filesystem.search": "Grep",
    "filesystem.write": "Write/Edit",
    "shell.execute": "Bash",
    "network.fetch": "WebFetch/WebSearch",
    "knowledge.skill": "Skill",
    "orchestration.delegate": "Agent",
}


class ClaudeCodeRuntime(AgentRuntime):
    descriptor = RuntimeDescriptor(
        id="claude",
        name="Claude Code",
        kind="cli",
        summary="CLI agentic con contexto separado, permisos, gates y aislamiento por worktree.",
        autonomous=True,
        maturity="IMPLEMENTED",
        docs="docs/CLAUDE_CODE.md",
    )

    def capabilities(self) -> RuntimeCapabilities:
        return RuntimeCapabilities(
            provides={
                "filesystem.read": "full",
                "filesystem.find": "full",
                "filesystem.search": "full",
                "filesystem.write": "full",
                "shell.execute": "full",
                "network.fetch": "full",
                "knowledge.skill": "full",
                "orchestration.delegate": "full",
            },
            modalities=("text", "image", "document"),
            notes=(
                "Cada capacidad se resuelve con una tool nativa del runtime.",
                "Las tools disponibles siguen filtradas por la allowlist del agente y por el modo de permisos.",
            ),
        )

    def detect(self) -> Detection:
        executable = shutil.which("claude")
        if not executable:
            return Detection(False, "No se encontró Claude Code; use export o instálelo antes de run")
        return Detection(True, executable)

    def command(self, agent: dict[str, Any], task: str) -> tuple[str, ...]:
        return (shutil.which("claude") or "claude", "--agent", agent["id"], "--print", task)

    def execute(self, preparation: Preparation, cwd: Path) -> ExecutionResult:
        completed = subprocess.run(list(preparation.command), cwd=cwd, check=False)
        status = COMPLETED if completed.returncode == 0 else FAILED
        return ExecutionResult(
            status=status,
            exit_code=completed.returncode,
            detail=f"claude terminó con código {completed.returncode}",
        )
