<!-- Generado por `operational-agents sync`. Edita catalog/agents.yaml, no este archivo. -->

# 📚 Documentation Coherence Agent

> Reconcilia documentación, arquitectura, ejemplos y métricas con las fuentes de verdad del repositorio.

[![estado](https://img.shields.io/badge/estado-IMPLEMENTED-1f6feb)](../../docs/MATURITY_MODEL.md) [![riesgo](https://img.shields.io/badge/riesgo-medium-d29922)](../../docs/SECURITY_MODEL.md) [![version](https://img.shields.io/badge/version-0.1.0-8957e5)](../../CHANGELOG.md) [![permisos](https://img.shields.io/badge/permisos-default-0969da)](../../docs/SECURITY_MODEL.md)

[Ejemplos](#ejemplos-de-uso) · [Mapa](#mapa-de-la-misión) · [Flujo](#flujo-operativo) · [Ficha](#ficha-técnica) · [Contrato](#contrato-de-entrega) · [Permisos](#permisos-y-aprobaciones) · [Instalación](#instalación)

---

## Qué hace por ti

Hacer que la documentación sea una interfaz fiable del sistema, preservando el contexto histórico y explicitando incertidumbres.

> [!NOTE]
> Trabaja en un worktree aislado y se detiene ante 3 gates humanos. Inspecciona primero; muta solo lo aprobado.

## Cuándo delegarle trabajo

Úsalo cuando README, docs, conteos, diagramas o ejemplos pueden haberse desalineado del código.

## Ejemplos de uso

3 casos trabajados: el contexto real, el mensaje que le escribes, lo que hace paso a paso y la forma exacta de lo que te devuelve.

> [!NOTE]
> Son **ejemplos ilustrativos del contrato**, no transcripciones de ejecuciones registradas. Ningún agente del catálogo declara todavía evidencia de uso real — ver [Madurez](#madurez).

### 1 · Números que dejaron de ser ciertos

**El caso.** El README dice «49 tests» y la suite tiene 62. La guía de instalación pide Node 20 y el CI usa Node 24. La tabla de SHAs de las acciones muestra los pines de hace tres meses.

**Le escribes:**

```text
Audita si la documentación coincide con el repositorio y corrige el drift.
```

**Qué hace, paso a paso:**

1. `claim-extraction` — extrae todas las afirmaciones numéricas y de versión de los 14 archivos Markdown.
2. `source-resolution` — resuelve cada una contra su fuente ejecutable: la suite, el workflow, los `uses:` reales.
3. `drift-classification` — clasifica cada desvío y descarta 6 coincidencias que ya eran correctas.

**Lo que te devuelve:**

| Afirmación | Dice | Es | Fuente |
|---|---|---|---|
| conteo de pruebas | 49 | 62 | recuento de la suite |
| versión de Node | 20+ | 24 | `setup-node` del workflow |
| pines de acciones | 3 SHAs viejos | 5 actuales | los `uses:` reales |
| cobertura | 71% | 71% | correcto, no se toca |

**Cómo cierra —** `COMPLETED` — 3 corregidos, 6 verificados y dejados como estaban. Corregir lo que ya era cierto es la otra forma de romper la documentación.

### 2 · Corregir el presente sin reescribir el pasado

**El caso.** El número de agentes aparece en 9 sitios: badges, texto del README, roadmap y varias entradas del changelog. Un reemplazo global lo dejaría todo «coherente» y falsificaría el registro histórico.

**Le escribes:**

```text
Actualiza los conteos del README desde la fuente de verdad sin tocar el historial.
```

**Qué hace, paso a paso:**

1. `claim-extraction` — recoge las 9 apariciones sin decidir todavía nada sobre ellas.
2. `drift-classification` — clasifica cada una: marcador de estado actual o referencia histórica. «v0.1.0 publicó diez agentes» era cierto cuando se escribió.
3. `documentation-update` — sincroniza solo las 4 del primer grupo y deja las 5 restantes intactas.

**Lo que te devuelve:**

- **Sincronizadas (4)** — badge, párrafo de apertura del catálogo, salida de ejemplo del comando y nota de madurez.
- **Conservadas (5)** — tres entradas de changelog y dos hitos del roadmap que describen releases pasados.
- **Criterio aplicado** — ¿la línea afirma cómo está el repositorio ahora, o narra qué pasó en una versión concreta?

**Cómo cierra —** `COMPLETED` — la prueba de fuego, buscar el valor viejo junto a un marcador de estado actual, sale vacía.

### 3 · Un diagrama que ya no representa el sistema

**El caso.** La arquitectura cambió en marzo: se retiró un cache y se partió un servicio en dos. El diagrama del README sigue mostrando el sistema de antes, y tres ejemplos de código usan una función renombrada.

**Le escribes:**

```text
Revisa si los diagramas y los ejemplos de la documentación siguen siendo ciertos.
```

**Qué hace, paso a paso:**

1. `source-resolution` — contrasta cada componente del diagrama contra el código que debería implementarlo.
2. `link-and-example-verification` — ejecuta los ejemplos en vez de leerlos: 3 de 11 fallan por una función que se renombró.
3. `report` — declara lo que no pudo resolver en vez de inventarlo.

**Lo que te devuelve:**

- **Diagrama** — 1 componente que ya no existe y 1 servicio que aparece como uno cuando son dos. Corregido.
- **Ejemplos** — 11 ejecutados, 3 fallaban, 3 corregidos y vueltos a ejecutar.
- **Sin resolver** — el diagrama muestra una cola de mensajes que no aparece en el código ni en la infraestructura declarada. No se borra sin preguntar: puede vivir fuera de este repositorio.

**Cómo cierra —** `PARTIAL` — 2 de 3 frentes cerrados y 1 afirmación pendiente, marcada como tal en vez de resuelta a la ligera.

## Mapa de la misión

```mermaid
flowchart LR
    IN["📥 Necesita de ti<br/>· repository_path<br/>· documentation_scope<br/>· edit_authorization"]
    AG(["📚 documentation-coherence-agent"])
    OUT["📦 Te entrega<br/>· claim_evidence_matrix<br/>· drift_report<br/>· updated_documentation<br/>· unresolved_claims"]
    GATE["🚦 Se detiene y pregunta antes de<br/>· historical_rewrite<br/>· public_claim_change<br/>· generated_docs_overwrite"]
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
        p2["2 · claim extraction"]
        p3["3 · source resolution"]
        p4["4 · drift classification"]
        p5["5 · repair plan"]
        p1 --> p2
        p2 --> p3
        p3 --> p4
        p4 --> p5
    end
    G{{"🚦 approval<br/>decisión humana"}}
    subgraph B["⚙️ Ejecución acotada y verificación"]
        direction TB
        p7["7 · documentation update"]
        p8["8 · link and example verification"]
        p9["9 · report"]
        p7 --> p8
        p8 --> p9
    end
    A --> G --> B --> FIN(["📋 entrega verificada"])
    G -.->|"si deniegas"| A
    style G fill:#bf8700,color:#fff
    style FIN fill:#2da44e,color:#fff
```

Cada fase deja evidencia antes de habilitar la siguiente. Ninguna fase posterior asume la autorización de la anterior.

| # | Fase | Qué ocurre en ella |
|:-:|---|---|
| 1 | `scope` | Delimita qué documentación se audita y contra qué fuentes de verdad se va a contrastar. |
| 2 | `claim-extraction` | Extrae cada afirmación comprobable: cifras, versiones, comandos, rutas, enlaces y capacidades declaradas. |
| 3 | `source-resolution` | Localiza para cada afirmación su fuente de verdad en el código, la configuración o el historial. |
| 4 | `drift-classification` | Clasifica cada divergencia y distingue siempre el marcador de estado actual —que se sincroniza— de la referencia histórica —que se conserva—. |
| 5 | `repair-plan` | Propone la corrección de cada divergencia indicando explícitamente qué se reescribe y qué se preserva. |
| 6 | `approval` | Presenta el plan de reparación y espera una decisión humana antes de reescribir documentación ajena. |
| 7 | `documentation-update` | Aplica las correcciones aprobadas sin reescribir el historial ni rellenar huecos con contexto inventado. |
| 8 | `link-and-example-verification` | Resuelve cada enlace y ejecuta cada ejemplo. Un enlace roto es documentación falsa, no un detalle estético. |
| 9 | `report` | Entrega qué se corrigió, qué se conservó a propósito y qué afirmaciones quedaron sin fuente verificable. |

## Ficha técnica

| Propiedad | Valor |
|---|---|
| Identificador | `documentation-coherence-agent` |
| Categoría | `documentation-engineering` |
| Versión | `0.1.0` |
| Estado honesto | `IMPLEMENTED` |
| Riesgo | `medium` |
| Modo de permisos | `default` |
| Aislamiento | `worktree` |
| Memoria | `project` |
| Esfuerzo | `medium` |
| Turnos máximos | `22` |

## Contrato de entrega

**Entradas requeridas**

- `repository_path`
- `documentation_scope`
- `edit_authorization`

**Entregables**

- `claim_evidence_matrix`
- `drift_report`
- `updated_documentation`
- `unresolved_claims`

**Controles obligatorios**

- Extraer afirmaciones comprobables sobre versiones, conteos, estados y compatibilidad.
- Asignar una fuente de verdad o marcar la afirmación como no verificable.
- Distinguir dato actual, referencia histórica y objetivo futuro.
- Actualizar tablas y diagramas sin alterar hechos históricos.
- Verificar enlaces internos, comandos y ejemplos ejecutables.
- Reportar toda discrepancia que requiera una decisión del propietario.

**Fuera de misión**

- Embellecer ocultando límites
- Cambiar cifras a mano sin fuente
- Borrar historia

**Limitaciones**

- Depende de la cobertura y actualidad de las fuentes autorizadas.
- No sustituye la revisión humana experta ni amplía el alcance aprobado.

**Modos de fallo controlados**

- Si falta una fuente obligatoria, entrega PARTIAL o BLOCKED con la brecha explícita.
- Si la evidencia se contradice, conserva ambas versiones y reduce la confianza.

**Eventos de auditoría**

- `analysis_started`
- `tool_completed`
- `evidence_linked`
- `human_decision_recorded`
- `analysis_completed`

## Permisos y aprobaciones

| Superficie | Valor |
|---|---|
| Tools permitidas | `Read` `Glob` `Grep` `Bash` `Edit` `Write` `Skill` |
| Tools denegadas | _ninguna restricción explícita_ |

El agente se detiene y pide una decisión humana explícita antes de:

- `historical_rewrite`
- `public_claim_change`
- `generated_docs_overwrite`

Una aprobación de otro agente no sustituye la del usuario, y una aprobación acotada no autoriza fases posteriores.

## Skills complementarios

El agente funciona de forma autónoma. Si además instalas [`claude-skills-toolkit`](https://github.com/vladimiracunadev-create/claude-skills-toolkit), puede precargar:

- `repo-coherence-audit`
- `md-lint-fix`
- `md-to-doc`
- `yaml-control`

```bash
operational-agents export claude --preload-skills --target ~/.claude/agents
```

## Instalación

```bash
operational-agents inspect documentation-coherence-agent
operational-agents export claude --target ~/.claude/agents
claude --agent documentation-coherence-agent
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
