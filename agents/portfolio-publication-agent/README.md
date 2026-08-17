<!-- Generado por `operational-agents sync`. Edita catalog/agents.yaml, no este archivo. -->

# 🌐 Portfolio Publication Agent

> Reconcilia una superficie publicada —sitio, API, documentos generados y perfiles— con el estado real de los repositorios que la alimentan, sin destruir contenido curado a mano.

[![estado](https://img.shields.io/badge/estado-IMPLEMENTED-1f6feb)](../../docs/MATURITY_MODEL.md) [![riesgo](https://img.shields.io/badge/riesgo-high-da3633)](../../docs/SECURITY_MODEL.md) [![version](https://img.shields.io/badge/version-0.1.0-8957e5)](../../CHANGELOG.md) [![permisos](https://img.shields.io/badge/permisos-default-0969da)](../../docs/SECURITY_MODEL.md)

[Ejemplos](#ejemplos-de-uso) · [Mapa](#mapa-de-la-misión) · [Flujo](#flujo-operativo) · [Ficha](#ficha-técnica) · [Contrato](#contrato-de-entrega) · [Permisos](#permisos-y-aprobaciones) · [Instalación](#instalación)

---

## Qué hace por ti

Hacer que todas las superficies publicadas afirmen lo mismo que demuestran los repositorios de origen, integrando en vez de sobrescribir y publicando solo tras aprobación humana.

> [!WARNING]
> **Riesgo alto.** Este agente puede cambiar cosas difíciles de deshacer, así que se detiene ante 4 gates humanos y ninguno se salta con acceso técnico.

## Cuándo delegarle trabajo

Úsalo cuando lo publicado sobre un conjunto de repositorios dejó de coincidir con su estado real y hay que sincronizarlo sin romper lo que se editó a mano.

## Ejemplos de uso

3 casos trabajados: el contexto real, el mensaje que le escribes, lo que hace paso a paso y la forma exacta de lo que te devuelve.

> [!NOTE]
> Son **ejemplos ilustrativos del contrato**, no transcripciones de ejecuciones registradas. Ningún agente del catálogo declara todavía evidencia de uso real — ver [Madurez](#madurez).

### 1 · La web dice una versión y el release otra

**El caso.** Un sitio publicado, una API JSON que lo alimenta y 30 PDFs generados. Cada superficie salió en un momento distinto: la web anuncia la versión 1.2, la API devuelve 1.0 y los PDFs llevan la portada de la 0.9.

**Le escribes:**

```text
Sincroniza el sitio publicado con el estado real de estos repositorios y muéstrame las brechas antes de aplicar.
```

**Qué hace, paso a paso:**

1. `surface-inventory` — enumera cada superficie que afirma algo: web, API, PDFs, descripciones de repositorio. Cada una puede mentir por separado.
2. `source-of-truth-collection` — toma el estado real de los repositorios de origen, nunca de otra superficie publicada.
3. `dry-run` — ejecuta la sincronización completa en modo lectura y presenta el informe antes de modificar nada.

**Lo que te devuelve:**

| Superficie | Afirma | Real | Acción propuesta |
|---|---|---|---|
| web | v1.2 | v1.4 | actualizar |
| API JSON | v1.0 | v1.4 | regenerar |
| 30 PDFs | v0.9 en portada | v1.4 | regenerar con respaldo previo |
| descripción del repo | «en desarrollo» | 3 releases firmados | reescribir |

**Cómo cierra —** `BLOCKED` esperando aprobación — 0 archivos modificados. La pasada en seco es obligatoria antes de tocar una superficie publicada.

### 2 · Hace meses que no actualizas lo publicado

**El caso.** Publicaste cuatro releases nuevos en tres meses y la superficie pública sigue mostrando el estado de antes. No recuerdas qué quedó atrás ni por dónde empezar.

**Le escribes:**

```text
Hace tiempo que no actualizo la superficie publicada: audítala y entrega un plan verificable.
```

**Qué hace, paso a paso:**

1. `drift-detection` — compara superficie contra origen y encuentra que la descripción corta de un repositorio está **más** desactualizada que la web.
2. `apply` — respalda cada artefacto binario antes de sobrescribirlo, sin reutilizar jamás un respaldo anterior.
3. `cross-surface-verification` — mide también lo que pudo romperse, no solo lo que se quería mejorar.

**Lo que te devuelve:**

- **Origen** — 4 releases, 2 productos nuevos y un repositorio archivado.
- **Atrasado** — la web (3 meses), la API (3 meses) y los PDFs (5 meses).
- **Respaldos** — 30 PDFs guardados con marca de tiempo antes de regenerar.
- **Verificación cruzada** — tras aplicar, el conteo de proyectos de la web y el de la API coinciden, y ningún PDF quedó con menos páginas que su respaldo.

**Cómo cierra —** `COMPLETED` — con el trabajo manual pendiente declarado: dos capturas de pantalla del sitio siguen mostrando la interfaz antigua y eso no se automatiza.

### 3 · Sin destruir lo que escribiste a mano

**El caso.** La página de inicio tiene tres párrafos que escribiste con cuidado y que ningún generador sabe reproducir. Regenerar el sitio entero los borraría sin avisar.

**Le escribes:**

```text
Actualiza lo que esté desfasado sin tocar el contenido que escribí a mano.
```

**Qué hace, paso a paso:**

1. `surface-inventory` — distingue lo generado de lo curado a mano antes de tocar nada.
2. `apply` — integra los datos nuevos dentro del esquema existente en vez de anexar secciones sueltas o reemplazar el archivo.
3. `post-publication-checks` — comprueba en vivo que lo publicado sirve el contenido nuevo y no una versión cacheada.

**Lo que te devuelve:**

- **Curado a mano, intacto** — 3 párrafos de la portada, el orden manual de los proyectos destacados y dos textos alternativos de imagen.
- **Actualizado** — versiones, fechas y conteos, dentro de la estructura que ya existía.
- **Comprobación en vivo** — la URL pública devuelve el contenido nuevo, no el de la caché; verificado con una petición real tras el despliegue.

**Cómo cierra —** `COMPLETED` — los repositorios de origen no se tocaron en ningún momento: para este agente son de solo lectura por contrato.

## Mapa de la misión

```mermaid
flowchart LR
    IN["📥 Necesita de ti<br/>· published_surface_path<br/>· source_repositories<br/>· publication_authorization"]
    AG(["🌐 portfolio-publication-agent"])
    OUT["📦 Te entrega<br/>· surface_inventory<br/>· drift_report<br/>· dry_run_output<br/>· applied_changes<br/>· cross_surface_verification<br/>· residual_manual_work"]
    GATE["🚦 Se detiene y pregunta antes de<br/>· scope_expansion<br/>· destructive_change<br/>· external_publish<br/>· profile_or_description_edit"]
    IN --> AG --> OUT
    AG -.->|"sin tu decisión, no avanza"| GATE
    style AG fill:#8957e5,color:#fff
    style GATE fill:#bf8700,color:#fff
    style OUT fill:#2da44e,color:#fff
```

## Flujo operativo

```mermaid
flowchart LR
    subgraph A["🔍 Diagnóstico · solo lectura"]
        direction TB
        p1["1 · scope"]
        p2["2 · surface inventory"]
        p3["3 · source of truth collection"]
        p4["4 · drift detection"]
        p5["5 · dry run"]
        p1 --> p2
        p2 --> p3
        p3 --> p4
        p4 --> p5
    end
    G{{"🚦 approval<br/>decisión humana"}}
    subgraph B["⚙️ Ejecución acotada y verificación"]
        direction TB
        p7["7 · apply"]
        p8["8 · cross surface verification"]
        p9["9 · publication"]
        p10["10 · post publication checks"]
        p7 --> p8
        p8 --> p9
        p9 --> p10
    end
    A --> G --> B --> FIN(["📋 entrega verificada"])
    G -.->|"si deniegas"| A
    style G fill:#bf8700,color:#fff
    style FIN fill:#2da44e,color:#fff
```

Cada fase deja evidencia antes de habilitar la siguiente. Ninguna fase posterior asume la autorización de la anterior.

| # | Fase | Qué ocurre en ella |
|:-:|---|---|
| 1 | `scope` | Delimita qué superficie publicada se sincroniza, qué repositorios la alimentan y hasta dónde llega tu autorización para publicar. |
| 2 | `surface-inventory` | Enumera cada superficie que afirma algo: sitio, API, documentos generados, perfiles y descripciones. Cada una es un lugar donde el proyecto puede mentir por separado. |
| 3 | `source-of-truth-collection` | Recoge el estado real desde los repositorios de origen —releases, versiones, contenido medido— y no desde lo que otra superficie afirma. |
| 4 | `drift-detection` | Compara cada afirmación publicada contra la fuente y clasifica la divergencia. La descripción corta de un repositorio puede estar más desactualizada que el sitio: verifica contra el release antes de «corregir» hacia atrás. |
| 5 | `dry-run` | Ejecuta la sincronización en modo solo lectura y presenta el reporte de brechas completo antes de modificar nada. |
| 6 | `approval` | Presenta el reporte y espera una confirmación humana explícita. Este flujo publica: ninguna aprobación anterior lo cubre. |
| 7 | `apply` | Aplica los cambios aprobados sin publicar todavía, respaldando todo artefacto binario antes de sobrescribirlo y sin tocar jamás los repositorios de origen. |
| 8 | `cross-surface-verification` | Comprueba que todas las superficies quedaron coherentes entre sí, midiendo la dimensión que pudo romperse y no solo la que querías mejorar. Un número que mejora no prueba que algo esté bien. |
| 9 | `publication` | Publica solo tras la aprobación y registra qué superficie cambió y con qué contenido. |
| 10 | `post-publication-checks` | Comprueba en vivo que lo publicado responde y sirve el contenido nuevo, no una versión cacheada. |

## Ficha técnica

| Propiedad | Valor |
|---|---|
| Identificador | `portfolio-publication-agent` |
| Categoría | `portfolio-governance` |
| Versión | `0.1.0` |
| Estado honesto | `IMPLEMENTED` |
| Riesgo | `high` |
| Modo de permisos | `default` |
| Aislamiento | `worktree` |
| Memoria | `project` |
| Esfuerzo | `high` |
| Turnos máximos | `32` |

## Contrato de entrega

**Entradas requeridas**

- `published_surface_path`
- `source_repositories`
- `publication_authorization`

**Entregables**

- `surface_inventory`
- `drift_report`
- `dry_run_output`
- `applied_changes`
- `cross_surface_verification`
- `residual_manual_work`

**Controles obligatorios**

- Inventariar todas las superficies que afirman algo antes de corregir cualquiera de ellas.
- Tomar el estado real de los repositorios de origen y nunca de otra superficie publicada.
- Ejecutar siempre un paso solo lectura y presentar el reporte de brechas antes de modificar nada.
- Respaldar todo artefacto binario antes de sobrescribirlo y no reutilizar jamás un respaldo previo.
- Tratar los repositorios de origen como solo lectura.
- Integrar en el esquema existente en vez de anexar secciones sueltas ni destruir contenido curado.
- Verificar la dimensión que pudo romperse y no solo la que se quería mejorar.
- Declarar explícitamente el trabajo manual que la sincronización automática deja pendiente.

**Fuera de misión**

- Modificar los repositorios de origen
- Sustituir contenido curado a mano por texto generado
- Publicar sin confirmación humana explícita
- Afirmar cifras que no se hayan contado

## Permisos y aprobaciones

| Superficie | Valor |
|---|---|
| Tools permitidas | `Read` `Glob` `Grep` `Bash` `Edit` `Write` `Skill` `WebSearch` `WebFetch` |
| Tools denegadas | _ninguna restricción explícita_ |

El agente se detiene y pide una decisión humana explícita antes de:

- `scope_expansion`
- `destructive_change`
- `external_publish`
- `profile_or_description_edit`

Una aprobación de otro agente no sustituye la del usuario, y una aprobación acotada no autoriza fases posteriores.

## Skills complementarios

El agente funciona de forma autónoma. Si además instalas [`claude-skills-toolkit`](https://github.com/vladimiracunadev-create/claude-skills-toolkit), puede precargar:

- `repo-coherence-audit`
- `md-lint-fix`
- `pre-push-guard`
- `web-snap`

```bash
operational-agents export claude --preload-skills --target ~/.claude/agents
```

## Instalación

```bash
operational-agents inspect portfolio-publication-agent
operational-agents export claude --target ~/.claude/agents
claude --agent portfolio-publication-agent
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

`IMPLEMENTED` significa que el paquete y su contrato están implementados y validados localmente. **No** significa uso productivo. La promoción de estado exige evidencia real conforme a [docs/MATURITY_MODEL.md](../../docs/MATURITY_MODEL.md).

---

<div align="center"><sub><a href="../../README.md">← Catálogo completo</a> · <a href="../../docs/AGENT_CONTRACT.md">Contrato canónico</a></sub></div>
