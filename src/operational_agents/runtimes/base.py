
"""Contrato común de runtime.

Un runtime es cualquier cosa capaz de llevar un contrato de agente a la
realidad: un CLI agentic, una API, un modelo local o una persona siguiendo un
paquete de instrucciones. El agente no sabe cuál lo ejecuta.

`run()` es un método plantilla deliberadamente cerrado: detecta, prepara,
resuelve capacidades y solo entonces ejecuta. Ningún adaptador puede saltarse
la resolución, porque no es él quien decide el orden.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..capabilities import DEFAULT_MODALITIES, UNSUPPORTED, Resolution, resolve
from ..planner import create_plan, packet
from ..render import render_instructions

# Estados de una ejecución. `NOT_EXECUTED` no es un fallo: es el resultado
# normal de un runtime que prepara trabajo para que lo ejecute una persona.
COMPLETED = "COMPLETED"
FAILED = "FAILED"
BLOCKED = "BLOCKED"
NOT_EXECUTED = "NOT_EXECUTED"


@dataclass(frozen=True)
class RuntimeDescriptor:
    """Identidad de un adaptador.

    `maturity` usa la misma escala que los agentes y se aplica al adaptador, no
    al producto que envuelve: declara cuánto se ha demostrado de *esta*
    integración, y ningún runtime asciende sin evidencia registrada.
    """

    id: str
    name: str
    kind: str
    summary: str
    autonomous: bool
    maturity: str = "DRAFT"
    docs: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "summary": self.summary,
            "autonomous": self.autonomous,
            "maturity": self.maturity,
            "docs": self.docs,
        }


@dataclass(frozen=True)
class RuntimeCapabilities:
    """Lo que el runtime declara saber hacer, sin mirar el entorno.

    Es una declaración estable: la misma en cualquier máquina. Lo que cambia
    entre máquinas es `Detection`, y las dos cosas se informan por separado.
    """

    provides: dict[str, str] = field(default_factory=dict)
    modalities: tuple[str, ...] = DEFAULT_MODALITIES
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {"provides": dict(self.provides), "modalities": list(self.modalities), "notes": list(self.notes)}


@dataclass(frozen=True)
class Detection:
    """Disponibilidad real del runtime en esta máquina."""

    available: bool
    detail: str
    version: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {"available": self.available, "detail": self.detail, "version": self.version}


@dataclass(frozen=True)
class Preparation:
    agent_id: str
    runtime_id: str
    task: str
    target: str | None
    plan: dict[str, Any]
    prompt: str
    command: tuple[str, ...]
    resolution: Resolution

    def as_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "runtime_id": self.runtime_id,
            "task": self.task,
            "target": self.target,
            "plan": self.plan,
            "command": list(self.command),
            "resolution": self.resolution.as_dict(),
        }


@dataclass(frozen=True)
class ExecutionResult:
    status: str
    exit_code: int
    detail: str
    artifacts: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {"status": self.status, "exit_code": self.exit_code, "detail": self.detail, "artifacts": dict(self.artifacts)}


class AgentRuntime(ABC):
    """Interfaz que debe cumplir cualquier adaptador de runtime."""

    descriptor: RuntimeDescriptor

    @abstractmethod
    def capabilities(self) -> RuntimeCapabilities:
        """Capacidades declaradas, independientes del entorno."""

    @abstractmethod
    def detect(self) -> Detection:
        """Comprueba si el runtime está disponible aquí y ahora."""

    @abstractmethod
    def execute(self, preparation: Preparation, cwd: Path) -> ExecutionResult:
        """Lleva a cabo la ejecución ya preparada y autorizada."""

    def command(self, agent: dict[str, Any], task: str) -> tuple[str, ...]:  # noqa: ARG002 - firma del contrato: los adaptadores que sí invocan un proceso la usan
        """Invocación concreta, si el runtime la tiene. Vacía si no aplica."""
        return ()

    def resolve(self, agent: dict[str, Any]) -> Resolution:
        declared = self.capabilities()
        return resolve(agent, declared.provides, runtime_id=self.descriptor.id, modalities=declared.modalities)

    def prepare(self, agent: dict[str, Any], task: str, target: str | None = None) -> Preparation:
        plan = create_plan(agent, task, target)
        return Preparation(
            agent_id=agent["id"],
            runtime_id=self.descriptor.id,
            task=plan["task"],
            target=target,
            plan=plan,
            prompt=packet(agent, render_instructions(agent), plan["task"], target),
            command=tuple(self.command(agent, plan["task"])),
            resolution=self.resolve(agent),
        )

    def run(
        self,
        agent: dict[str, Any],
        task: str,
        *,
        target: str | None = None,
        cwd: Path | None = None,
    ) -> tuple[Preparation, ExecutionResult]:
        """Detecta, prepara, resuelve y solo entonces ejecuta."""
        detection = self.detect()
        if not detection.available:
            raise FileNotFoundError(detection.detail)
        workdir = (cwd or Path.cwd()).expanduser().resolve()
        if not workdir.is_dir():
            raise ValueError(f"Directorio inexistente: {workdir}")
        preparation = self.prepare(agent, task, target)
        if preparation.resolution.status == UNSUPPORTED:
            faltan = ", ".join(preparation.resolution.missing)
            return preparation, ExecutionResult(
                status=BLOCKED,
                exit_code=1,
                detail=f"{self.descriptor.id} no ofrece las capacidades requeridas: {faltan}",
            )
        return preparation, self.execute(preparation, workdir)
