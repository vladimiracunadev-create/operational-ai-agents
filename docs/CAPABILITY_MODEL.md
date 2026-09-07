# Modelo de capacidades

> Una tool es el nombre que un runtime concreto le da a una acción. Una capacidad es la acción. Este documento explica por qué la diferencia importa y cómo se resuelve.

[← Documentación](README.md) · [Contrato de runtime](RUNTIME_CONTRACT.md) · [Matriz de compatibilidad](COMPATIBILITY_MATRIX.md)

---

## El problema

Un agente que declara `Read`, `Grep` y `Bash` está describiendo **cómo** hacer su trabajo con una tecnología concreta. Si mañana lo ejecuta otro runtime con otros nombres, o a través de MCP, o de una API REST, el contrato deja de encajar aunque la misión sea idéntica.

La capa de capacidades separa las dos cosas:

```text
El agente pide            filesystem.search
El runtime decide con qué  →  Grep · ripgrep · MCP filesystem · API de búsqueda
```

## Las capacidades

| Capacidad | Efectos | Riesgo | ¿Gate humano? |
|---|---|:-:|:-:|
| `filesystem.read` | `read` | bajo | no |
| `filesystem.find` | `read` | bajo | no |
| `filesystem.search` | `read` | bajo | no |
| `filesystem.write` | `write` | medio | ✅ |
| `shell.execute` | `execute` | alto | ✅ |
| `network.fetch` | `network`, `read` | medio | ✅ |
| `orchestration.delegate` | `execute` | medio | ✅ |
| `knowledge.skill` *(opcional)* | `read` | bajo | no |

## El modelo de efectos

La política no mira nombres de herramientas, mira **efectos**. Una escritura es una escritura venga de una tool nativa, de un servidor MCP, de un SDK o de una API REST — y por eso las mismas reglas se aplican a las cuatro sin escribirlas cuatro veces.

```bash
operational-agents capabilities repository-evolution-agent --json | python -m json.tool
```

El campo `effects` agrupa lo autorizado por consecuencia: qué puede leer, qué puede escribir, qué puede ejecutar.

## De tools a capacidades

Los 23 agentes del catálogo **no** declaran capacidades: se derivan de sus tools. Eso es deliberado — la capa nueva no obliga a reescribir ningún contrato existente.

| Tool | Capacidad |
|---|---|
| `Read` | `filesystem.read` |
| `Glob` | `filesystem.find` |
| `Grep` | `filesystem.search` |
| `Write`, `Edit`, `NotebookEdit` | `filesystem.write` |
| `Bash` | `shell.execute` |
| `WebFetch`, `WebSearch` | `network.fetch` |
| `Task`, `Agent(...)` | `orchestration.delegate` |
| `Skill` | `knowledge.skill` *(opcional)* |

La forma parametrizada `Agent(uno, dos)` acota **a quién** se delega; la capacidad sigue siendo delegar.

### Declararlas explícitamente

Un agente puede declarar el bloque y entonces manda sobre la derivación:

```yaml
capabilities:
  required:
    - filesystem.read
    - filesystem.search
  optional:
    - knowledge.skill
input_modalities:
  required: [text]
  optional: [image, document]
```

Ambos campos son opcionales y compatibles hacia atrás: un agente sin ellos se comporta exactamente igual que antes.

## Los skills son opcionales, estructuralmente

`knowledge.skill` es la única capacidad marcada como opcional, y eso convierte una promesa de la documentación en una propiedad del sistema:

```text
AGENTE puede usar SKILL
AGENTE no depende obligatoriamente de SKILL
```

Un runtime que no sepa cargar skills —como `manual`— no vuelve inválido a ningún agente. La capacidad se informa como ausente y la ejecución sigue.

## La resolución

```text
Requisitos del agente
        ∩
Capacidades del runtime
        ∩
Autorización del contrato
        =
Conjunto ejecutable
```

| Estado | Cuándo | Qué ocurre |
|---|---|---|
| `SUPPORTED` | todo lo requerido está y es nativo | ejecuta |
| `DEGRADED` | está todo, pero algo es condicional | ejecuta y lo registra |
| `UNSUPPORTED` | falta algo requerido | **no** ejecuta; nombra qué falta |
| `BLOCKED` | el runtime lo ofrece y el contrato no lo autoriza | nunca entra en el conjunto ejecutable |

```bash
operational-agents capabilities                                    # matriz completa
operational-agents capabilities incident-root-cause-agent          # todos los runtimes
operational-agents capabilities incident-root-cause-agent --runtime claude
```

## Acceso no es autorización

Es la regla más importante de este modelo, y la que justifica el estado `BLOCKED`:

> Que el runtime **sepa** hacer algo no autoriza al agente a hacerlo.

La allowlist del contrato es **exhaustiva**: lo que no menciona, queda denegado. Claude Code ofrece `filesystem.write` a todo el mundo; `incident-root-cause-agent` no la tiene autorizada, así que su resolución la marca `BLOCKED` y jamás la incorpora al conjunto ejecutable — aunque el runtime la tenga disponible y encendida.

Esto vale igual para capacidades que llegan por otras vías. Un servidor MCP, una API REST o un SDK amplían lo que el agente **puede alcanzar**; no amplían lo que está **autorizado** a hacer.

## Proveedores de capacidades

Una capacidad puede satisfacerse de varias formas. El agente pide la capacidad; el runtime decide el proveedor:

| Capacidad | Proveedores posibles |
|---|---|
| `filesystem.search` | tool nativa · ripgrep · servidor MCP de filesystem |
| `network.fetch` | tool nativa · cliente HTTP · MCP · SDK del servicio |
| `shell.execute` | proceso local · contenedor · runner remoto |

Por eso un agente no debe acoplarse al nombre físico de un proveedor concreto. `repository-evolution-agent` no es «un agente de GitHub»: es un agente para evolucionar repositorios, y el origen —Git local, GitHub, GitLab, un ZIP— es una decisión del runtime y de la integración disponible.

Las integraciones concretas siguen siendo opt-in y se documentan en [`integrations/`](../integrations/mcp/README.md). Ninguna es un requisito estructural del agente.

## Modalidades

Un agente declara qué modalidades de entrada necesita; un runtime, cuáles acepta. Si falta una requerida, la resolución es `UNSUPPORTED` y lo dice — no se degrada en silencio a texto.

Hoy los 23 agentes trabajan con texto, y los dos runtimes lo soportan. El contrato existe para que incorporar un agente que reciba imágenes, PDF o audio no exija rediseñar nada.

## Presupuestos

`max_turns` sigue siendo el único presupuesto que el catálogo declara y que el adaptador de Claude Code proyecta. Límites de costo, duración o llamadas a herramientas se añadirán cuando exista un runtime que sepa aplicarlos: declarar un presupuesto que nadie hace cumplir es peor que no declararlo.

---

<div align="center"><sub><a href="README.md">Documentación</a> · <a href="RUNTIME_CONTRACT.md">Runtimes</a> · <a href="SECURITY_MODEL.md">Seguridad</a></sub></div>
