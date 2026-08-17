
"""Registro extensible de runtimes.

Añadir un adaptador es registrar una clase, no añadir una rama a un `if`. Un
paquete de terceros puede aportar el suyo declarando un entry point en el grupo
`operational_agents.runtimes`; si no hay ninguno instalado, el núcleo funciona
igual y sin importar nada opcional.
"""

from __future__ import annotations

from collections.abc import Iterator

from .base import AgentRuntime
from .claude import ClaudeCodeRuntime
from .manual import ManualRuntime

ENTRY_POINT_GROUP = "operational_agents.runtimes"


class RuntimeRegistry:
    def __init__(self) -> None:
        self._runtimes: dict[str, AgentRuntime] = {}
        self.plugin_errors: list[str] = []

    def register(self, runtime: AgentRuntime, *, replace: bool = False) -> None:
        identifier = runtime.descriptor.id
        if identifier in self._runtimes and not replace:
            raise ValueError(f"Runtime ya registrado: {identifier}")
        self._runtimes[identifier] = runtime

    def get(self, identifier: str) -> AgentRuntime:
        try:
            return self._runtimes[identifier]
        except KeyError as exc:
            disponibles = ", ".join(self.ids())
            raise KeyError(f"Runtime desconocido: {identifier}. Disponibles: {disponibles}") from exc

    def ids(self) -> tuple[str, ...]:
        return tuple(self._runtimes)

    def __contains__(self, identifier: object) -> bool:
        return identifier in self._runtimes

    def __iter__(self) -> Iterator[AgentRuntime]:
        return iter(self._runtimes.values())

    def __len__(self) -> int:
        return len(self._runtimes)


def load_plugins(registry: RuntimeRegistry) -> RuntimeRegistry:
    """Incorpora runtimes de terceros sin permitir que rompan el núcleo.

    Un plugin defectuoso se anota y se ignora: la CLI debe seguir listando,
    validando y planificando aunque el ecosistema de plugins falle.
    """
    try:
        from importlib.metadata import entry_points
    except ImportError:  # pragma: no cover - la stdlib siempre la trae en 3.11+
        return registry
    try:
        puntos = entry_points(group=ENTRY_POINT_GROUP)
    except Exception as exc:  # cualquier fallo del ecosistema es informativo, no fatal
        registry.plugin_errors.append(f"No se pudieron enumerar los plugins: {exc}")
        return registry
    for punto in puntos:
        try:
            registry.register(punto.load()(), replace=False)
        except Exception as exc:  # un plugin roto no puede tumbar la CLI
            registry.plugin_errors.append(f"{punto.name}: {exc}")
    return registry


def default_registry(*, with_plugins: bool = True) -> RuntimeRegistry:
    """Los runtimes que este repositorio implementa y demuestra."""
    registry = RuntimeRegistry()
    registry.register(ClaudeCodeRuntime())
    registry.register(ManualRuntime())
    return load_plugins(registry) if with_plugins else registry
