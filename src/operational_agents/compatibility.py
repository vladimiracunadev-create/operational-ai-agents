
"""Matriz de compatibilidad entre agentes y runtimes.

«Funciona en Claude» no significa «funciona en todos». Esta matriz se calcula
resolviendo cada agente contra las capacidades **declaradas** por cada runtime
—nunca contra lo que haya instalado en la máquina— para que el resultado sea el
mismo en cualquier equipo y en CI, y para que el documento generado no pueda
divergir del código que lo produce.

Lo que la matriz demuestra es que el contrato encaja; lo que **no** demuestra
es que la ejecución real cumpla la misión. Eso exige evidencia, y va aparte.
"""

from __future__ import annotations

from typing import Any

from .capabilities import BLOCKED, DEGRADED, SUPPORTED, UNSUPPORTED, Resolution
from .runtimes.registry import RuntimeRegistry, default_registry

STATUS_ICON = {SUPPORTED: "✅ SUPPORTED", DEGRADED: "⚠️ DEGRADED", UNSUPPORTED: "⛔ UNSUPPORTED", BLOCKED: "🚫 BLOCKED"}


def resolutions(catalog: dict[str, Any], registry: RuntimeRegistry | None = None) -> dict[str, dict[str, Resolution]]:
    """`{agent_id: {runtime_id: Resolution}}` para todo el catálogo."""
    registry = registry or default_registry(with_plugins=False)
    return {agent["id"]: {runtime.descriptor.id: runtime.resolve(agent) for runtime in registry} for agent in catalog["agents"]}


def matrix(catalog: dict[str, Any], registry: RuntimeRegistry | None = None) -> dict[str, Any]:
    registry = registry or default_registry(with_plugins=False)
    resueltas = resolutions(catalog, registry)
    return {
        "runtimes": [runtime.descriptor.as_dict() for runtime in registry],
        "agents": [
            {
                "agent_id": agent_id,
                "results": {runtime_id: resolution.as_dict() for runtime_id, resolution in por_runtime.items()},
            }
            for agent_id, por_runtime in resueltas.items()
        ],
    }


def render_compatibility_matrix(catalog: dict[str, Any], registry: RuntimeRegistry | None = None) -> str:
    """Documento generado. Editarlo a mano hace fallar `sync --check`."""
    registry = registry or default_registry(with_plugins=False)
    runtimes = list(registry)
    resueltas = resolutions(catalog, registry)

    cabecera = "| Agente | " + " | ".join(runtime.descriptor.id for runtime in runtimes) + " |"
    separador = "|---|" + "|".join([":-:"] * len(runtimes)) + "|"
    filas = [
        f"| [`{agent_id}`](../agents/{agent_id}/README.md) | "
        + " | ".join(STATUS_ICON[resueltas[agent_id][runtime.descriptor.id].status] for runtime in runtimes)
        + " |"
        for agent_id in resueltas
    ]

    fichas = []
    for runtime in runtimes:
        declared = runtime.capabilities()
        provee = "\n".join(f"| `{item}` | `{nivel}` |" for item, nivel in sorted(declared.provides.items()))
        notas = "\n".join(f"- {nota}" for nota in declared.notes)
        fichas.append(
            "\n".join([
                f"### `{runtime.descriptor.id}` — {runtime.descriptor.name}",
                "",
                runtime.descriptor.summary,
                "",
                f"| Propiedad | Valor |\n|---|---|\n| Tipo | `{runtime.descriptor.kind}` |"
                f"\n| Ejecución autónoma | `{'sí' if runtime.descriptor.autonomous else 'no'}` |"
                f"\n| Madurez del adaptador | `{runtime.descriptor.maturity}` |"
                f"\n| Modalidades de entrada | {' '.join(f'`{item}`' for item in declared.modalities)} |",
                "",
                "| Capacidad | Nivel |",
                "|---|---|",
                provee,
                "",
                notas,
            ])
        )

    # Agrupado por runtime: trece líneas idénticas no informan de nada.
    degradados = []
    for runtime in runtimes:
        rid = runtime.descriptor.id
        afectados = [aid for aid, por_runtime in resueltas.items() if por_runtime[rid].status == DEGRADED]
        if afectados:
            condicionales = sorted({item for aid in afectados for item in resueltas[aid][rid].degraded})
            degradados.append(f"- `{rid}` — {len(afectados)} de {len(resueltas)} agentes, por: {', '.join(f'`{c}`' for c in condicionales)}")

    bloqueadas = [
        "| Agente | " + " | ".join(f"`{runtime.descriptor.id}`" for runtime in runtimes) + " |",
        "|---|" + "|".join(["---"] * len(runtimes)) + "|",
    ]
    for agent_id, por_runtime in resueltas.items():
        celdas = [
            ", ".join(f"`{item}`" for item in por_runtime[runtime.descriptor.id].blocked) or "—"
            for runtime in runtimes
        ]
        bloqueadas.append(f"| `{agent_id}` | " + " | ".join(celdas) + " |")

    return f"""<!-- Generado por `operational-agents sync`. Edita el catálogo o el adaptador, no este archivo. -->

# Matriz de compatibilidad

> Qué agente puede operar bajo qué runtime, y con qué grado. Calculada resolviendo cada contrato contra las capacidades declaradas por cada adaptador.

[← Documentación](README.md) · [Contrato de runtime](RUNTIME_CONTRACT.md) · [Modelo de capacidades](CAPABILITY_MODEL.md)

---

## Qué significa cada estado

| Estado | Significado |
|---|---|
| `SUPPORTED` | el runtime ofrece de forma nativa todas las capacidades requeridas |
| `DEGRADED` | están todas, pero alguna es condicional; el agente opera con límites declarados |
| `UNSUPPORTED` | falta al menos una capacidad requerida; la CLI se niega a ejecutar |
| `BLOCKED` | el runtime ofrece una capacidad que el contrato del agente **no** autoriza |

> [!IMPORTANT]
> Esta matriz demuestra que **el contrato encaja**, no que la ejecución cumpla la misión. Ningún runtime declara todavía evidencia de uso real registrada en `evidence/`; la madurez del adaptador se declara por separado en cada ficha.

## Matriz

{cabecera}
{separador}
{chr(10).join(filas)}

## Runtimes

{(chr(10) * 2).join(fichas)}

## Degradaciones declaradas

Un `DEGRADED` no es un fallo: es una capacidad disponible con condiciones que el adaptador declara por escrito.

{chr(10).join(degradados) or "_Ninguna._"}

## Capacidades ofrecidas y denegadas por contrato

Acceso no es autorización: estas capacidades existen en el runtime y el agente **no** puede usarlas. La resolución nunca las incorpora al conjunto ejecutable.

{chr(10).join(bloqueadas)}

## Reproducirlo

```bash
operational-agents capabilities                 # esta misma matriz en la terminal
operational-agents capabilities <agent_id> --runtime <runtime_id> --json
```

---

<div align="center"><sub><a href="README.md">Documentación</a> · <a href="RUNTIME_CONTRACT.md">Runtimes</a> · <a href="CAPABILITY_MODEL.md">Capacidades</a></sub></div>
"""
