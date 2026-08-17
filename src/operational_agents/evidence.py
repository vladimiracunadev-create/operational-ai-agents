
"""Sobre de evidencia portable.

Una ejecución con Claude Code y otra con ejecución humana asistida deben poder
compararse. Para eso el registro tiene la misma forma en ambos casos: quién,
con qué runtime, con qué capacidades, con qué aprobaciones y con qué resultado.

Lo que no entra: credenciales, tokens, rutas absolutas del ejecutable ni el
prompt completo. La evidencia demuestra qué ocurrió, no reproduce el entorno.
"""

from __future__ import annotations

from pathlib import PurePath
from typing import Any

from .capabilities import approval_required_capabilities, effect_summary
from .redaction import redact
from .runtimes.base import Detection, ExecutionResult, Preparation

ENVELOPE_VERSION = "1.0"


def _clean(value: str | None) -> str | None:
    return redact(value) if isinstance(value, str) else value


def _safe_command(command: tuple[str, ...]) -> list[str]:
    """El ejecutable se reduce a su nombre: la ruta local no es evidencia."""
    if not command:
        return []
    return [PurePath(command[0]).name, *(redact(item) for item in command[1:])]


def execution_envelope(
    agent: dict[str, Any],
    preparation: Preparation,
    detection: Detection,
    result: ExecutionResult,
    *,
    runtime_descriptor: dict[str, Any],
    approvals: list[dict[str, Any]] | None = None,
    verification: list[dict[str, Any]] | None = None,
    residual_risk: list[str] | None = None,
) -> dict[str, Any]:
    plan = preparation.plan
    resolution = preparation.resolution
    return {
        "schema_version": ENVELOPE_VERSION,
        "agent": {
            "id": agent["id"],
            "version": agent["version"],
            "status": agent["status"],
            "risk": agent["risk"],
            "permission_mode": agent["permission_mode"],
            "isolation": agent.get("isolation"),
        },
        "runtime": {
            **runtime_descriptor,
            "detected": detection.available,
            "version": detection.version,
        },
        "execution": {
            "execution_id": plan["execution_id"],
            "created_at": plan["created_at"],
            "mode": plan["mode"],
            "task": _clean(preparation.task),
            "target": _clean(preparation.target),
            "command": _safe_command(preparation.command),
            "phases": [item["id"] for item in plan["phases"]],
        },
        "capabilities": {
            "status": resolution.status,
            "executable": list(resolution.executable),
            "degraded": list(resolution.degraded),
            "missing": list(resolution.missing),
            "blocked": list(resolution.blocked),
            "effects": effect_summary(agent),
            "requires_approval": list(approval_required_capabilities(agent)),
        },
        # Los gates declarados no son aprobaciones concedidas: `granted` solo se
        # llena con una decisión humana registrada fuera de la CLI.
        "approvals": approvals if approvals is not None else [{"gate": gate, "granted": None} for gate in plan["approval_gates"]],
        "evidence": [],
        "result": {
            "status": result.status,
            "exit_code": result.exit_code,
            "detail": _clean(result.detail),
        },
        "verification": verification or [],
        "residual_risk": residual_risk or list(resolution.notes),
        "notice": "Registro de invocación. No acredita que el runtime cumpliera el contrato ni sustituye la revisión humana.",
    }
