
"""Modelo de capacidades: qué necesita el agente frente a qué ofrece el runtime.

Una tool es el nombre que un runtime concreto le da a una acción; una capacidad
es la acción misma. El contrato del agente se sigue escribiendo en tools —eso no
cambia y no puede cambiar sin romper el catálogo—, pero la portabilidad se decide
aquí: un agente pide `filesystem.read`, y cada adaptador resuelve con qué tool
suya lo satisface.

Dos reglas gobiernan este módulo:

- **La allowlist es exhaustiva.** Lo que el contrato no autoriza queda denegado,
  aunque el runtime sepa hacerlo. Que Claude Code ofrezca escritura no autoriza
  a escribir a un agente de solo lectura: esa capacidad se marca `BLOCKED`.
- **Nada se finge.** Si una capacidad requerida no existe en el runtime, el
  resultado es `UNSUPPORTED` y se dice cuál falta, en lugar de degradar en
  silencio o simular que la ejecución fue completa.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

# Resultado de resolver una capacidad contra un runtime.
SUPPORTED = "SUPPORTED"
DEGRADED = "DEGRADED"
UNSUPPORTED = "UNSUPPORTED"
BLOCKED = "BLOCKED"

# Nivel con el que un runtime declara ofrecer una capacidad.
FULL = "full"
CONDITIONAL = "conditional"


@dataclass(frozen=True)
class Capability:
    """Una acción sobre el mundo, independiente de quién la ejecute.

    `effects` es lo que la política mira para decidir: el nombre de la tool
    puede cambiar entre runtimes, el efecto sobre el sistema no.
    """

    id: str
    effects: tuple[str, ...]
    risk: str
    requires_approval: bool
    description: str
    optional: bool = False


CAPABILITIES: dict[str, Capability] = {
    capability.id: capability
    for capability in (
        Capability("filesystem.read", ("read",), "low", False, "Leer el contenido de un archivo"),
        Capability("filesystem.find", ("read",), "low", False, "Localizar archivos por patrón de ruta"),
        Capability("filesystem.search", ("read",), "low", False, "Buscar contenido dentro de los archivos"),
        Capability("filesystem.write", ("write",), "medium", True, "Crear o modificar archivos"),
        Capability("shell.execute", ("execute",), "high", True, "Ejecutar comandos en el sistema anfitrión"),
        Capability("network.fetch", ("network", "read"), "medium", True, "Recuperar contenido remoto"),
        Capability(
            "knowledge.skill",
            ("read",),
            "low",
            False,
            "Cargar un skill externo como conocimiento adicional",
            optional=True,
        ),
        Capability("orchestration.delegate", ("execute",), "medium", True, "Delegar trabajo en otro agente"),
    )
}

# Proyección de las tools del contrato actual a capacidades. Es la única tabla
# que conoce los nombres de Claude Code; el resto del modelo es vendor-neutral.
TOOL_CAPABILITIES: dict[str, str] = {
    "Read": "filesystem.read",
    "Glob": "filesystem.find",
    "Grep": "filesystem.search",
    "Write": "filesystem.write",
    "Edit": "filesystem.write",
    "NotebookEdit": "filesystem.write",
    "Bash": "shell.execute",
    "Skill": "knowledge.skill",
    "WebFetch": "network.fetch",
    "WebSearch": "network.fetch",
    "Task": "orchestration.delegate",
    "Agent": "orchestration.delegate",
}

# Un agente que no declara modalidades trabaja con texto. Declararlas es opt-in
# y no rompe ningún contrato existente.
DEFAULT_MODALITIES: tuple[str, ...] = ("text",)


def capability(capability_id: str) -> Capability:
    try:
        return CAPABILITIES[capability_id]
    except KeyError as exc:
        raise KeyError(f"Capacidad desconocida: {capability_id}") from exc


def _unique(values: Sequence[str]) -> tuple[str, ...]:
    """Preserva el orden de aparición: la salida debe ser reproducible."""
    seen: dict[str, None] = {}
    for value in values:
        seen.setdefault(value, None)
    return tuple(seen)


def tool_name(tool: str) -> str:
    """Nombre de la tool sin sus argumentos.

    El catálogo admite la forma parametrizada `Agent(a, b, c)` para acotar a qué
    agentes puede delegar un coordinador. La capacidad es la misma: delegar.
    """
    return tool.split("(", 1)[0].strip()


def tool_capabilities(tools: Sequence[str]) -> tuple[str, ...]:
    """Capacidades implicadas por una lista de tools, sin las desconocidas."""
    return _unique([TOOL_CAPABILITIES[name] for name in map(tool_name, tools) if name in TOOL_CAPABILITIES])


def unmapped_tools(tools: Sequence[str]) -> tuple[str, ...]:
    """Tools sin capacidad conocida: se informan, nunca se ignoran en silencio."""
    return _unique([name for name in map(tool_name, tools) if name not in TOOL_CAPABILITIES])


def declared_capabilities(agent: Mapping[str, Any]) -> dict[str, list[str]] | None:
    """Bloque `capabilities` del catálogo, si el agente lo declara.

    El campo es opcional a propósito: los trece agentes del catálogo derivan sus
    capacidades de las tools, y añadir el bloque no cambia su comportamiento.
    """
    block = agent.get("capabilities")
    return block if isinstance(block, dict) else None


def required_capabilities(agent: Mapping[str, Any]) -> tuple[str, ...]:
    """Lo que el agente necesita para cumplir su misión.

    Las capacidades opcionales —hoy solo los skills— quedan fuera: un agente que
    declara `Skill` sigue siendo válido en un runtime que no sabe cargar skills.
    """
    block = declared_capabilities(agent)
    if block is not None and "required" in block:
        return _unique(list(block["required"]))
    return _unique([item for item in tool_capabilities(agent["tools"]) if not capability(item).optional])


def optional_capabilities(agent: Mapping[str, Any]) -> tuple[str, ...]:
    """Capacidades que mejoran el resultado pero no condicionan la ejecución."""
    block = declared_capabilities(agent)
    if block is not None and "optional" in block:
        return _unique(list(block["optional"]))
    return _unique([item for item in tool_capabilities(agent["tools"]) if capability(item).optional])


def authorized_capabilities(agent: Mapping[str, Any]) -> tuple[str, ...]:
    """Todo lo que el contrato autoriza: requerido más opcional."""
    return _unique([*required_capabilities(agent), *optional_capabilities(agent)])


def denied_capabilities(agent: Mapping[str, Any]) -> tuple[str, ...]:
    """Capacidades que el contrato no autoriza.

    Incluye las denegadas de forma explícita en `disallowed_tools` y también
    todas las que la allowlist simplemente no menciona. Un agente sin `Bash` no
    ejecuta comandos porque un runtime sepa hacerlo.
    """
    authorized = set(authorized_capabilities(agent))
    return tuple(sorted(set(CAPABILITIES) - authorized))


def input_modalities(agent: Mapping[str, Any]) -> tuple[str, ...]:
    """Modalidades de entrada que el agente necesita recibir."""
    block = agent.get("input_modalities")
    if isinstance(block, dict) and block.get("required"):
        return _unique(list(block["required"]))
    return DEFAULT_MODALITIES


@dataclass(frozen=True)
class CapabilityOutcome:
    capability: str
    status: str
    level: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {"capability": self.capability, "status": self.status, "level": self.level, "detail": self.detail}


@dataclass(frozen=True)
class Resolution:
    """Intersección entre lo que el agente pide, lo que el runtime ofrece y lo que el contrato autoriza."""

    agent_id: str
    runtime_id: str
    status: str
    outcomes: tuple[CapabilityOutcome, ...]
    executable: tuple[str, ...]
    degraded: tuple[str, ...]
    missing: tuple[str, ...]
    blocked: tuple[str, ...]
    notes: tuple[str, ...]

    @property
    def executable_set(self) -> frozenset[str]:
        return frozenset(self.executable)

    def as_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "runtime_id": self.runtime_id,
            "status": self.status,
            "executable": list(self.executable),
            "degraded": list(self.degraded),
            "missing": list(self.missing),
            "blocked": list(self.blocked),
            "outcomes": [item.as_dict() for item in self.outcomes],
            "notes": list(self.notes),
        }


def resolve(
    agent: Mapping[str, Any],
    provides: Mapping[str, str],
    *,
    runtime_id: str,
    modalities: Sequence[str] = DEFAULT_MODALITIES,
) -> Resolution:
    """Resuelve un agente contra las capacidades declaradas por un runtime.

    `provides` mapea capacidad → `full` o `conditional`. Nunca se consulta la
    detección del entorno: la resolución debe dar el mismo resultado en
    cualquier máquina, para que la matriz de compatibilidad sea comparable.
    """
    outcomes: list[CapabilityOutcome] = []
    executable: list[str] = []
    degraded: list[str] = []
    missing: list[str] = []
    blocked: list[str] = []
    notes: list[str] = []

    for item in required_capabilities(agent):
        level = provides.get(item)
        if level == FULL:
            outcomes.append(CapabilityOutcome(item, SUPPORTED, FULL, "El runtime la ofrece de forma nativa"))
            executable.append(item)
        elif level == CONDITIONAL:
            outcomes.append(CapabilityOutcome(item, DEGRADED, CONDITIONAL, "Disponible con condiciones declaradas por el runtime"))
            executable.append(item)
            degraded.append(item)
        else:
            outcomes.append(CapabilityOutcome(item, UNSUPPORTED, "", "El runtime no ofrece esta capacidad"))
            missing.append(item)

    for item in optional_capabilities(agent):
        level = provides.get(item)
        if level in (FULL, CONDITIONAL):
            outcomes.append(CapabilityOutcome(item, SUPPORTED if level == FULL else DEGRADED, level, "Capacidad opcional disponible"))
            executable.append(item)
        else:
            outcomes.append(CapabilityOutcome(item, UNSUPPORTED, "", "Capacidad opcional ausente; el agente sigue siendo válido"))

    # Acceso no es autorización: lo que el runtime ofrece y el contrato no
    # autoriza se marca y jamás entra en el conjunto ejecutable.
    for item in denied_capabilities(agent):
        if item in provides:
            outcomes.append(CapabilityOutcome(item, BLOCKED, provides[item], "El runtime la ofrece, pero el contrato del agente no la autoriza"))
            blocked.append(item)

    faltan_modalidades = [item for item in input_modalities(agent) if item not in modalities]
    if faltan_modalidades:
        missing.extend(f"modality:{item}" for item in faltan_modalidades)
        notes.append("Modalidades de entrada no soportadas: " + ", ".join(faltan_modalidades))

    sin_mapear = unmapped_tools(agent["tools"])
    if sin_mapear:
        notes.append("Tools sin capacidad declarada: " + ", ".join(sin_mapear))
    if blocked:
        notes.append("Capacidades ofrecidas por el runtime y denegadas por contrato: " + ", ".join(blocked))

    if missing:
        status = UNSUPPORTED
    elif degraded:
        status = DEGRADED
    else:
        status = SUPPORTED
    return Resolution(
        agent_id=agent["id"],
        runtime_id=runtime_id,
        status=status,
        outcomes=tuple(outcomes),
        executable=_unique(executable),
        degraded=tuple(degraded),
        missing=tuple(missing),
        blocked=tuple(blocked),
        notes=tuple(notes),
    )


def effect_summary(agent: Mapping[str, Any]) -> dict[str, list[str]]:
    """Efectos autorizados por el contrato, agrupados por tipo.

    Sirve para razonar sobre políticas sin mirar nombres de tools: una
    escritura es una escritura venga de una tool nativa, de MCP o de una API.
    """
    summary: dict[str, list[str]] = {}
    for item in authorized_capabilities(agent):
        for effect in capability(item).effects:
            summary.setdefault(effect, []).append(item)
    return {effect: sorted(set(items)) for effect, items in sorted(summary.items())}


def approval_required_capabilities(agent: Mapping[str, Any]) -> tuple[str, ...]:
    """Capacidades autorizadas que, por su efecto, exigen decisión humana."""
    return tuple(item for item in authorized_capabilities(agent) if capability(item).requires_approval)
