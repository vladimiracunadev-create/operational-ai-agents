
from __future__ import annotations

import json
import re
from typing import Any


def yaml_scalar(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def phase_title(phase: str) -> str:
    return phase.replace("-", " ").capitalize()


def render_instructions(agent: dict[str, Any]) -> str:
    details = agent["phase_details"]
    phases = "\n\n".join(
        f"{index}. **{phase_title(phase)}** (`{phase}`)\n   {details[phase]}"
        for index, phase in enumerate(agent["phases"], 1)
    )
    checks = "\n".join(f"- {item}" for item in agent["checks"])
    approvals = "\n".join(f"- `{item}`" for item in agent["approval_points"])
    deliverables = "\n".join(f"- `{item}`" for item in agent["deliverables"])
    inputs = "\n".join(f"- `{item}`" for item in agent["required_inputs"])
    non_goals = "\n".join(f"- {item}" for item in agent["non_goals"])
    return f"""# {agent['name']}

Eres un agente especializado y responsable de una misión completa. Tu objetivo es: **{agent['mission']}**

## Cuándo actuar

{agent['delegate_when']}

Si faltan el objetivo, el alcance o el límite de autorización, inspecciona únicamente lo seguro y solicita la decisión antes de modificar. No interpretes acceso técnico como autorización para publicar, desplegar, borrar, rotar credenciales o ampliar el alcance.

## Qué necesitas para empezar

{inputs}

Si falta alguno, pídelo antes de actuar. Puedes avanzar en lo que no dependa del dato ausente, pero deja explícito qué quedó bloqueado y por qué.

## Protocolo operativo

Avanza en este orden. Cada fase produce evidencia antes de habilitar la siguiente, y ninguna fase posterior hereda la autorización de la anterior.

{phases}

## Controles obligatorios

{checks}

## Aprobación humana

Detente y presenta opciones concretas antes de cualquiera de estos eventos:

{approvals}

Una aprobación de otro agente no sustituye la aprobación del usuario. Una aprobación acotada no autoriza fases posteriores.

## Contrato de finalización

No declares la tarea terminada hasta entregar:

{deliverables}

Para cada afirmación de finalización indica la prueba, comando, archivo o fuente que la respalda. Clasifica lo no comprobado como hipótesis, pendiente o limitación.

## Formato de salida

1. Resultado y estado: `COMPLETED`, `PARTIAL`, `BLOCKED` o `NO_CHANGE`.
2. Alcance realmente examinado.
3. Evidencia principal.
4. Cambios o decisiones realizados.
5. Verificaciones ejecutadas y resultados.
6. Riesgos residuales y supuestos.
7. Aprobaciones o siguiente acción, si corresponde.

## Fuera de misión

{non_goals}

Mantén una separación estricta entre hechos observados, inferencias y recomendaciones. La honestidad sobre límites tiene prioridad sobre aparentar completitud.
"""


RISK_COLOR = {"low": "2ea043", "medium": "d29922", "high": "da3633"}
STATUS_COLOR = {
    "DRAFT": "6e7681",
    "IMPLEMENTED": "1f6feb",
    "OPERATIONAL_LOCAL": "8957e5",
    "INTEGRATED": "2ea043",
    "PRODUCTION_OBSERVED": "brightgreen",
}


def _badge(label: str, value: str, color: str, link: str) -> str:
    def safe(text: str) -> str:
        return text.replace("-", "--").replace(" ", "_")

    return f"[![{label}](https://img.shields.io/badge/{safe(label)}-{safe(value)}-{color})]({link})"


def render_agent_readme(agent: dict[str, Any]) -> str:
    """Vista humana del contrato. Generada: editar el catálogo, no este archivo."""
    risk = RISK_COLOR.get(agent["risk"], "6e7681")
    status = STATUS_COLOR.get(agent["status"], "6e7681")
    badges = " ".join([
        _badge("estado", agent["status"], status, "../../docs/MATURITY_MODEL.md"),
        _badge("riesgo", agent["risk"], risk, "../../docs/SECURITY_MODEL.md"),
        _badge("version", agent["version"], "8957e5", "../../CHANGELOG.md"),
        _badge("permisos", agent["permission_mode"], "0969da", "../../docs/SECURITY_MODEL.md"),
    ])
    last = len(agent["phases"])
    labels = "\n".join(
        f"    p{index}[\"{phase.replace('-', ' ')}\"]"
        for index, phase in enumerate(agent["phases"], 1)
    )
    nodes = "\n".join(f"    p{index} --> p{index + 1}" for index in range(1, last))
    phase_table = "\n".join(
        f"| {index} | `{phase}` | {agent['phase_details'][phase]} |"
        for index, phase in enumerate(agent["phases"], 1)
    )
    examples = "\n".join(f"> {item}\n>" for item in agent["examples"]).rstrip(">\n")
    facts = "\n".join([
        "| Propiedad | Valor |",
        "|---|---|",
        f"| Identificador | `{agent['id']}` |",
        f"| Categoría | `{agent['category']}` |",
        f"| Versión | `{agent['version']}` |",
        f"| Estado honesto | `{agent['status']}` |",
        f"| Riesgo | `{agent['risk']}` |",
        f"| Modo de permisos | `{agent['permission_mode']}` |",
        f"| Aislamiento | `{agent.get('isolation') or 'ninguno'}` |",
        f"| Memoria | `{agent['memory']}` |",
        f"| Esfuerzo | `{agent['effort']}` |",
        f"| Turnos máximos | `{agent['max_turns']}` |",
    ])
    tools = " ".join(f"`{item}`" for item in agent["tools"])
    denied = " ".join(f"`{item}`" for item in agent["disallowed_tools"]) or "_ninguna restricción explícita_"
    inputs = "\n".join(f"- `{item}`" for item in agent["required_inputs"])
    deliverables = "\n".join(f"- `{item}`" for item in agent["deliverables"])
    approvals = "\n".join(f"- `{item}`" for item in agent["approval_points"])
    checks = "\n".join(f"- {item}" for item in agent["checks"])
    non_goals = "\n".join(f"- {item}" for item in agent["non_goals"])
    if agent["skill_dependencies"]:
        skills_list = "\n".join(f"- `{item}`" for item in agent["skill_dependencies"])
        skills = (
            "El agente funciona de forma autónoma. Si además instalas "
            "[`claude-skills-toolkit`](https://github.com/vladimiracunadev-create/claude-skills-toolkit), "
            f"puede precargar:\n\n{skills_list}\n\n"
            "```bash\noperational-agents export claude --preload-skills --target ~/.claude/agents\n```"
        )
    else:
        skills = "Este agente no declara skills complementarios: opera únicamente con sus tools."
    return f"""<!-- Generado por `operational-agents sync`. Edita catalog/agents.yaml, no este archivo. -->

# {agent['icon']} {agent['name']}

> {agent['description']}

{badges}

[Ficha](#ficha-técnica) · [Delegación](#cuándo-delegarle-trabajo) · [Flujo](#flujo-operativo) · [Contrato](#contrato-de-entrega) · [Permisos](#permisos-y-aprobaciones) · [Instalación](#instalación)

---

## Misión

{agent['mission']}

## Ficha técnica

{facts}

## Cuándo delegarle trabajo

{agent['delegate_when']}

{examples}

## Flujo operativo

```mermaid
flowchart LR
{labels}
{nodes}
    p{last} --> done(["entrega verificada"])
```

Cada fase deja evidencia antes de habilitar la siguiente. Ninguna fase posterior asume la autorización de la anterior.

| # | Fase | Qué ocurre en ella |
|:-:|---|---|
{phase_table}

## Contrato de entrega

**Entradas requeridas**

{inputs}

**Entregables**

{deliverables}

**Controles obligatorios**

{checks}

**Fuera de misión**

{non_goals}

## Permisos y aprobaciones

| Superficie | Valor |
|---|---|
| Tools permitidas | {tools} |
| Tools denegadas | {denied} |

El agente se detiene y pide una decisión humana explícita antes de:

{approvals}

Una aprobación de otro agente no sustituye la del usuario, y una aprobación acotada no autoriza fases posteriores.

## Skills complementarios

{skills}

## Instalación

```bash
operational-agents inspect {agent['id']}
operational-agents export claude --target ~/.claude/agents
claude --agent {agent['id']}
```

## Archivos del paquete

| Archivo | Contenido |
|---|---|
| `AGENT.md` | definición instalable en Claude Code (generada) |
| `agent.yaml` | vista del contrato canónico (generada) |
| `instructions.md` | instrucciones vendor-neutral (generada) |
| `README.md` | esta ficha humana (generada) |
| `policies/policy.yaml` | límites, gates y política de datos |
| `schemas/input.schema.json` | contrato de entrada |
| `schemas/output.schema.json` | contrato de salida |
| `evals/cases.jsonl` | casos de evaluación determinista |

## Madurez

`{agent['status']}` significa que el paquete y su contrato están implementados y validados localmente. **No** significa uso productivo. La promoción de estado exige evidencia real conforme a [docs/MATURITY_MODEL.md](../../docs/MATURITY_MODEL.md).

---

<div align="center"><sub><a href="../../README.md">← Catálogo completo</a> · <a href="../../docs/AGENT_CONTRACT.md">Contrato canónico</a></sub></div>
"""


def render_claude(agent: dict[str, Any], preload_skills: bool = False) -> str:
    lines = [
        "---",
        f"name: {agent['id']}",
        f"description: {yaml_scalar(agent['delegate_when'])}",
        "tools: " + ", ".join(agent["tools"]),
    ]
    if agent.get("disallowed_tools"):
        lines.append("disallowedTools: " + ", ".join(agent["disallowed_tools"]))
    lines.extend([
        "model: inherit",
        f"permissionMode: {agent['permission_mode']}",
        f"maxTurns: {agent['max_turns']}",
        f"memory: {agent['memory']}",
        f"effort: {agent['effort']}",
    ])
    if agent.get("isolation"):
        lines.append(f"isolation: {agent['isolation']}")
    lines.append(f"color: {agent['color']}")
    if preload_skills and agent.get("skill_dependencies"):
        lines.append("skills:")
        lines.extend(f"  - {skill}" for skill in agent["skill_dependencies"])
    lines.extend(["---", "", "<!-- managed-by: operational-ai-agents -->", "", render_instructions(agent).rstrip(), ""])
    return "\n".join(lines)


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("Falta frontmatter inicial")
    try:
        raw, body = text[4:].split("\n---\n", 1)
    except ValueError as exc:
        raise ValueError("Frontmatter sin cierre") from exc
    if not body.strip():
        raise ValueError("System prompt vacío")
    result: dict[str, str] = {}
    for line in raw.splitlines():
        if line.startswith("  - "):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def valid_agent_id(value: str) -> bool:
    return bool(re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", value))
