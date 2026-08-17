
from __future__ import annotations

import json
import re
from itertools import pairwise
from typing import Any


def yaml_scalar(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def phase_title(phase: str) -> str:
    return phase.replace("-", " ").capitalize()


def render_scenarios_brief(agent: dict[str, Any]) -> str:
    """Escenarios en formato compacto, para el prompt del agente."""
    return "\n\n".join(
        f"{index}. **{item['title']}** — {item['context']}\n"
        f"   - Te lo pedirán más o menos así: «{item['ask']}»\n"
        f"   - Cómo se resuelve: {' '.join(item['walkthrough'])}\n"
        f"   - Cierre esperado: {item['status']}"
        for index, item in enumerate(agent["scenarios"], 1)
    )


def render_scenarios_full(agent: dict[str, Any]) -> str:
    """Cada escenario como un caso trabajado: contexto, prompt, pasos y salida."""
    bloques = []
    for index, item in enumerate(agent["scenarios"], 1):
        pasos = "\n".join(f"{n}. {paso}" for n, paso in enumerate(item["walkthrough"], 1))
        bloques.append("\n".join([
            f"### {index} · {item['title']}",
            "",
            f"**El caso.** {item['context']}",
            "",
            "**Le escribes:**",
            "",
            "```text",
            item["ask"],
            "```",
            "",
            "**Qué hace, paso a paso:**",
            "",
            pasos,
            "",
            "**Lo que te devuelve:**",
            "",
            item["returns"],
            "",
            f"**Cómo cierra —** {item['status']}",
        ]))
    return "\n\n".join(bloques)


def _gate_phase(agent: dict[str, Any]) -> int | None:
    """Índice de la fase que separa diagnosticar de ejecutar, si existe."""
    for index, phase in enumerate(agent["phases"]):
        if "approval" in phase:
            return index
    return None


def render_mission_map(agent: dict[str, Any]) -> str:
    """Qué necesita, qué entrega y dónde se detiene, de un vistazo."""
    def lista(items: list[str], limite: int = 6) -> str:
        visibles = [f"· {item}" for item in items[:limite]]
        if len(items) > limite:
            visibles.append(f"· … y {len(items) - limite} más")
        return "<br/>".join(visibles)

    return "\n".join([
        "```mermaid",
        "flowchart LR",
        f'    IN["📥 Necesita de ti<br/>{lista(agent["required_inputs"])}"]',
        f'    AG(["{agent["icon"]} {agent["id"]}"])',
        f'    OUT["📦 Te entrega<br/>{lista(agent["deliverables"])}"]',
        f'    GATE["🚦 Se detiene y pregunta antes de<br/>{lista(agent["approval_points"])}"]',
        "    IN --> AG --> OUT",
        '    AG -.->|"sin tu decisión, no avanza"| GATE',
        "    style AG fill:#8957e5,color:#fff",
        "    style GATE fill:#bf8700,color:#fff",
        "    style OUT fill:#2da44e,color:#fff",
        "```",
    ])


def render_phase_flow(agent: dict[str, Any]) -> str:
    """Fases agrupadas por lo que el agente puede hacer en cada tramo."""
    phases = agent["phases"]
    gate = _gate_phase(agent)

    def cadena(indices: list[int]) -> list[str]:
        lineas = [f'        p{i + 1}["{i + 1} · {phases[i].replace("-", " ")}"]' for i in indices]
        lineas += [f"        p{a + 1} --> p{b + 1}" for a, b in pairwise(indices)]
        return lineas

    out = ["```mermaid", "flowchart LR"]
    if gate is None:
        out += ['    subgraph A["🔍 Recorrido completo · sin mutaciones fuera de contrato"]', "        direction TB"]
        out += cadena(list(range(len(phases))))
        out += [
            "    end",
            '    A --> FIN(["📋 entrega verificada"])',
            f'    A -.->|"se detiene y pregunta"| G["🚦 {len(agent["approval_points"])} gates humanos"]',
        ]
    else:
        out += ['    subgraph A["🔍 Diagnóstico · solo lectura"]', "        direction TB"]
        out += cadena(list(range(gate)))
        out += ["    end"]
        out += [f'    G{{{{"🚦 {phases[gate]}<br/>decisión humana"}}}}']
        out += ['    subgraph B["⚙️ Ejecución acotada y verificación"]', "        direction TB"]
        out += cadena(list(range(gate + 1, len(phases))))
        out += [
            "    end",
            '    A --> G --> B --> FIN(["📋 entrega verificada"])',
            '    G -.->|"si deniegas"| A',
            "    style G fill:#bf8700,color:#fff",
        ]
    out += ['    style FIN fill:#2da44e,color:#fff', "```"]
    return "\n".join(out)


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

Estas son las situaciones típicas que llegan a ti. Reconócelas y sitúa la petición en la que corresponda antes de planificar:

{render_scenarios_brief(agent)}

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
    phase_table = "\n".join(
        f"| {index} | `{phase}` | {agent['phase_details'][phase]} |"
        for index, phase in enumerate(agent["phases"], 1)
    )
    scenarios = render_scenarios_full(agent)
    mission_map = render_mission_map(agent)
    phase_flow = render_phase_flow(agent)
    write_capable = "Edit" in agent["tools"] or "Write" in agent["tools"]
    if agent["risk"] == "high":
        aviso = (
            "> [!WARNING]\n"
            f"> **Riesgo alto.** Este agente puede cambiar cosas difíciles de deshacer, así que se detiene "
            f"ante {len(agent['approval_points'])} gates humanos y ninguno se salta con acceso técnico."
        )
    elif not write_capable:
        aviso = (
            "> [!NOTE]\n"
            "> **Solo lectura.** `Write` y `Edit` están denegadas por contrato: analiza y recomienda, "
            "pero no puede modificar un archivo aunque se lo pidas."
        )
    else:
        aviso = (
            "> [!NOTE]\n"
            f"> Trabaja en un worktree aislado y se detiene ante {len(agent['approval_points'])} gates humanos. "
            "Inspecciona primero; muta solo lo aprobado."
            if agent.get("isolation") == "worktree"
            else f"> [!NOTE]\n> Se detiene ante {len(agent['approval_points'])} gates humanos."
        )
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

[Ejemplos](#ejemplos-de-uso) · [Mapa](#mapa-de-la-misión) · [Flujo](#flujo-operativo) · [Ficha](#ficha-técnica) · [Contrato](#contrato-de-entrega) · [Permisos](#permisos-y-aprobaciones) · [Instalación](#instalación)

---

## Qué hace por ti

{agent['mission']}

{aviso}

## Cuándo delegarle trabajo

{agent['delegate_when']}

## Ejemplos de uso

{len(agent['scenarios'])} casos trabajados: el contexto real, el mensaje que le escribes, lo que hace paso a paso y la forma exacta de lo que te devuelve.

> [!NOTE]
> Son **ejemplos ilustrativos del contrato**, no transcripciones de ejecuciones registradas. Ningún agente del catálogo declara todavía evidencia de uso real — ver [Madurez](#madurez).

{scenarios}

## Mapa de la misión

{mission_map}

## Flujo operativo

{phase_flow}

Cada fase deja evidencia antes de habilitar la siguiente. Ninguna fase posterior asume la autorización de la anterior.

| # | Fase | Qué ocurre en ella |
|:-:|---|---|
{phase_table}

## Ficha técnica

{facts}

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
