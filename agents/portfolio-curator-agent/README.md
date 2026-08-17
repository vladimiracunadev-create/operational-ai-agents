<!-- Generado por `operational-agents sync`. Edita catalog/agents.yaml, no este archivo. -->

# 🗂️ Portfolio Curator Agent

> Clasifica y audita un portafolio de repositorios, detecta solapamientos y produce una narrativa profesional respaldada por evidencia.

[![estado](https://img.shields.io/badge/estado-IMPLEMENTED-1f6feb)](../../docs/MATURITY_MODEL.md) [![riesgo](https://img.shields.io/badge/riesgo-low-2ea043)](../../docs/SECURITY_MODEL.md) [![version](https://img.shields.io/badge/version-0.1.0-8957e5)](../../CHANGELOG.md) [![permisos](https://img.shields.io/badge/permisos-plan-0969da)](../../docs/SECURITY_MODEL.md)

[Ficha](#ficha-técnica) · [Delegación](#cuándo-delegarle-trabajo) · [Ejemplos](#ejemplos-de-uso) · [Flujo](#flujo-operativo) · [Contrato](#contrato-de-entrega) · [Permisos](#permisos-y-aprobaciones) · [Instalación](#instalación)

---

## Misión

Mantener una visión coherente del portafolio distinguiendo aprendizaje, skills, agentes, casos de referencia y productos.

## Ficha técnica

| Propiedad | Valor |
|---|---|
| Identificador | `portfolio-curator-agent` |
| Categoría | `portfolio-governance` |
| Versión | `0.1.0` |
| Estado honesto | `IMPLEMENTED` |
| Riesgo | `low` |
| Modo de permisos | `plan` |
| Aislamiento | `ninguno` |
| Memoria | `project` |
| Esfuerzo | `medium` |
| Turnos máximos | `22` |

## Cuándo delegarle trabajo

Úsalo para revisar varios repositorios, ordenar el portafolio o preparar evidencia para reclutadores y colaboradores.

## Ejemplos de uso

Tres situaciones concretas en las que este agente es la elección correcta. Cada una parte de lo que tienes delante, no de lo que el agente sabe hacer.

### 1 · Veinte repositorios y ninguna historia

**Lo que tienes delante —** Tienes muchos repositorios acumulados y, puestos juntos, no cuentan nada: no se distingue el ejercicio de aprendizaje del producto real.

**Lo que le escribes —**

> Clasifica mis repositorios en aprendizaje, skills, agentes, casos y productos.

**Lo que te devuelve —** Cada repositorio clasificado por su propósito principal, con su madurez honesta y la evidencia que la respalda. No modifica nada: solo lee.

### 2 · Dos repositorios que hacen lo mismo

**Lo que tienes delante —** Sospechas que hay capacidades duplicadas repartidas entre varios repositorios y no sabes cuál debería quedarse con cada una.

**Lo que le escribes —**

> Detecta solapamientos entre mis repositorios y dime cuál es el hogar natural de cada capacidad.

**Lo que te devuelve —** El mapa de duplicación y la recomendación de fusionar, archivar o renombrar, cada una con su justificación.

### 3 · Preparar la conversación con un reclutador

**Lo que tienes delante —** Vas a postular y necesitas explicar tu trabajo en cinco minutos con enlaces que sostengan lo que dices.

**Lo que le escribes —**

> Prepara un mapa de portafolio para reclutadores con evidencia real.

**Lo que te devuelve —** La narrativa que conecta los repositorios sin exagerar adopción, con el enlace concreto que respalda cada afirmación.

## Flujo operativo

```mermaid
flowchart LR
    p1["scope"]
    p2["repository discovery"]
    p3["classification"]
    p4["evidence sampling"]
    p5["overlap analysis"]
    p6["maturity map"]
    p7["narrative"]
    p8["recommendations"]
    p1 --> p2
    p2 --> p3
    p3 --> p4
    p4 --> p5
    p5 --> p6
    p6 --> p7
    p7 --> p8
    p8 --> done(["entrega verificada"])
```

Cada fase deja evidencia antes de habilitar la siguiente. Ninguna fase posterior asume la autorización de la anterior.

| # | Fase | Qué ocurre en ella |
|:-:|---|---|
| 1 | `scope` | Delimita qué repositorios entran en el análisis y con qué propósito se va a usar la narrativa resultante. |
| 2 | `repository-discovery` | Enumera los repositorios del alcance con su actividad real, visibilidad, releases y última señal de vida. |
| 3 | `classification` | Clasifica cada repositorio por su unidad principal: aprendizaje, skill, agente, caso de referencia o producto. |
| 4 | `evidence-sampling` | Abre y comprueba una muestra real de cada repositorio. La descripción corta suele estar más desactualizada que el código. |
| 5 | `overlap-analysis` | Detecta solapamientos y decide cuál es el hogar natural de cada capacidad duplicada. |
| 6 | `maturity-map` | Sitúa cada repositorio en su estado honesto de madurez, con la evidencia que lo respalda. |
| 7 | `narrative` | Redacta la narrativa profesional que conecta los repositorios sin exagerar adopción ni inventar impacto. |
| 8 | `recommendations` | Propone acciones concretas —fusionar, archivar, renombrar, documentar— cada una con su justificación. |

## Contrato de entrega

**Entradas requeridas**

- `owner_or_repository_list`
- `audience`
- `classification_goal`

**Entregables**

- `portfolio_catalog`
- `classification_matrix`
- `maturity_map`
- `evidence_links`
- `recommended_narrative`

**Controles obligatorios**

- Examinar repositorios representativos y no inferir todo desde nombres.
- Clasificar por propósito primario y registrar aristas secundarias sin mezclar promesas.
- Contrastar métricas visibles con archivos, releases y pruebas.
- Detectar duplicación, repositorios puente y especializaciones oficiales.
- Separar madurez técnica de adopción real.
- Proponer una narrativa profesional con enlaces a evidencia verificable.

**Fuera de misión**

- Editar perfiles sin permiso
- Ocultar limitaciones
- Equiparar demo con producción

## Permisos y aprobaciones

| Superficie | Valor |
|---|---|
| Tools permitidas | `Read` `Glob` `Grep` `Bash` `Skill` `WebSearch` `WebFetch` |
| Tools denegadas | `Edit` `Write` |

El agente se detiene y pide una decisión humana explícita antes de:

- `profile_edit`
- `repository_archive`
- `external_publication`

Una aprobación de otro agente no sustituye la del usuario, y una aprobación acotada no autoriza fases posteriores.

## Skills complementarios

El agente funciona de forma autónoma. Si además instalas [`claude-skills-toolkit`](https://github.com/vladimiracunadev-create/claude-skills-toolkit), puede precargar:

- `repo-coherence-audit`
- `web-snap`

```bash
operational-agents export claude --preload-skills --target ~/.claude/agents
```

## Instalación

```bash
operational-agents inspect portfolio-curator-agent
operational-agents export claude --target ~/.claude/agents
claude --agent portfolio-curator-agent
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
