<!-- Generado por `operational-agents sync`. Edita el catálogo o el adaptador, no este archivo. -->

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

| Agente | claude | manual |
|---|:-:|:-:|
| [`repository-evolution-agent`](../agents/repository-evolution-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`legacy-modernization-agent`](../agents/legacy-modernization-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`learning-program-architect`](../agents/learning-program-architect/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`product-evolution-agent`](../agents/product-evolution-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`portfolio-curator-agent`](../agents/portfolio-curator-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`release-governance-agent`](../agents/release-governance-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`documentation-coherence-agent`](../agents/documentation-coherence-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`incident-root-cause-agent`](../agents/incident-root-cause-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`security-remediation-agent`](../agents/security-remediation-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`repository-maintenance-coordinator`](../agents/repository-maintenance-coordinator/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`curriculum-evolution-agent`](../agents/curriculum-evolution-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`portfolio-publication-agent`](../agents/portfolio-publication-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`professional-profile-agent`](../agents/professional-profile-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`reconciliation-agent`](../agents/reconciliation-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`iam-audit-agent`](../agents/iam-audit-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`wallet-risk-agent`](../agents/wallet-risk-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`blockchain-monitoring-agent`](../agents/blockchain-monitoring-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`trading-risk-agent`](../agents/trading-risk-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`evidence-agent`](../agents/evidence-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`timeline-agent`](../agents/timeline-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`compliance-evidence-agent`](../agents/compliance-evidence-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`executive-reporting-agent`](../agents/executive-reporting-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |
| [`financial-root-cause-agent`](../agents/financial-root-cause-agent/README.md) | ✅ SUPPORTED | ⚠️ DEGRADED |

## Runtimes

### `claude` — Claude Code

CLI agentic con contexto separado, permisos, gates y aislamiento por worktree.

| Propiedad | Valor |
|---|---|
| Tipo | `cli` |
| Ejecución autónoma | `sí` |
| Madurez del adaptador | `IMPLEMENTED` |
| Modalidades de entrada | `text` `image` `document` |

| Capacidad | Nivel |
|---|---|
| `filesystem.find` | `full` |
| `filesystem.read` | `full` |
| `filesystem.search` | `full` |
| `filesystem.write` | `full` |
| `knowledge.skill` | `full` |
| `network.fetch` | `full` |
| `orchestration.delegate` | `full` |
| `shell.execute` | `full` |

- Cada capacidad se resuelve con una tool nativa del runtime.
- Las tools disponibles siguen filtradas por la allowlist del agente y por el modo de permisos.

### `manual` — Ejecución humana asistida

Prepara el paquete portable y las verificaciones; la ejecución la realiza una persona.

| Propiedad | Valor |
|---|---|
| Tipo | `human` |
| Ejecución autónoma | `no` |
| Madurez del adaptador | `IMPLEMENTED` |
| Modalidades de entrada | `text` `image` `document` `audio` `video` |

| Capacidad | Nivel |
|---|---|
| `filesystem.find` | `conditional` |
| `filesystem.read` | `conditional` |
| `filesystem.search` | `conditional` |
| `filesystem.write` | `conditional` |
| `network.fetch` | `conditional` |
| `orchestration.delegate` | `conditional` |
| `shell.execute` | `conditional` |

- Ninguna capacidad se ejecuta de forma automática: todas las realiza una persona.
- No carga skills: el conocimiento adicional debe aportarlo quien ejecuta.
- El resultado es siempre NOT_EXECUTED; el trabajo lo cierra la persona, no la CLI.

## Degradaciones declaradas

Un `DEGRADED` no es un fallo: es una capacidad disponible con condiciones que el adaptador declara por escrito.

- `manual` — 23 de 23 agentes, por: `filesystem.find`, `filesystem.read`, `filesystem.search`, `filesystem.write`, `network.fetch`, `orchestration.delegate`, `shell.execute`

## Capacidades ofrecidas y denegadas por contrato

Acceso no es autorización: estas capacidades existen en el runtime y el agente **no** puede usarlas. La resolución nunca las incorpora al conjunto ejecutable.

| Agente | `claude` | `manual` |
|---|---|---|
| `repository-evolution-agent` | `network.fetch`, `orchestration.delegate` | `network.fetch`, `orchestration.delegate` |
| `legacy-modernization-agent` | `network.fetch`, `orchestration.delegate` | `network.fetch`, `orchestration.delegate` |
| `learning-program-architect` | `orchestration.delegate` | `orchestration.delegate` |
| `product-evolution-agent` | `orchestration.delegate` | `orchestration.delegate` |
| `portfolio-curator-agent` | `filesystem.write`, `orchestration.delegate` | `filesystem.write`, `orchestration.delegate` |
| `release-governance-agent` | `network.fetch`, `orchestration.delegate` | `network.fetch`, `orchestration.delegate` |
| `documentation-coherence-agent` | `network.fetch`, `orchestration.delegate` | `network.fetch`, `orchestration.delegate` |
| `incident-root-cause-agent` | `filesystem.write`, `network.fetch`, `orchestration.delegate` | `filesystem.write`, `network.fetch`, `orchestration.delegate` |
| `security-remediation-agent` | `network.fetch`, `orchestration.delegate` | `network.fetch`, `orchestration.delegate` |
| `repository-maintenance-coordinator` | `filesystem.write`, `network.fetch` | `filesystem.write`, `network.fetch` |
| `curriculum-evolution-agent` | `orchestration.delegate` | `orchestration.delegate` |
| `portfolio-publication-agent` | `orchestration.delegate` | `orchestration.delegate` |
| `professional-profile-agent` | `orchestration.delegate` | `orchestration.delegate` |
| `reconciliation-agent` | `filesystem.write`, `knowledge.skill`, `orchestration.delegate`, `shell.execute` | `filesystem.write`, `orchestration.delegate`, `shell.execute` |
| `iam-audit-agent` | `filesystem.write`, `knowledge.skill`, `orchestration.delegate`, `shell.execute` | `filesystem.write`, `orchestration.delegate`, `shell.execute` |
| `wallet-risk-agent` | `filesystem.write`, `knowledge.skill`, `orchestration.delegate`, `shell.execute` | `filesystem.write`, `orchestration.delegate`, `shell.execute` |
| `blockchain-monitoring-agent` | `filesystem.write`, `knowledge.skill`, `orchestration.delegate`, `shell.execute` | `filesystem.write`, `orchestration.delegate`, `shell.execute` |
| `trading-risk-agent` | `filesystem.write`, `knowledge.skill`, `orchestration.delegate`, `shell.execute` | `filesystem.write`, `orchestration.delegate`, `shell.execute` |
| `evidence-agent` | `filesystem.write`, `knowledge.skill`, `orchestration.delegate`, `shell.execute` | `filesystem.write`, `orchestration.delegate`, `shell.execute` |
| `timeline-agent` | `filesystem.write`, `knowledge.skill`, `orchestration.delegate`, `shell.execute` | `filesystem.write`, `orchestration.delegate`, `shell.execute` |
| `compliance-evidence-agent` | `filesystem.write`, `knowledge.skill`, `orchestration.delegate`, `shell.execute` | `filesystem.write`, `orchestration.delegate`, `shell.execute` |
| `executive-reporting-agent` | `filesystem.write`, `knowledge.skill`, `orchestration.delegate`, `shell.execute` | `filesystem.write`, `orchestration.delegate`, `shell.execute` |
| `financial-root-cause-agent` | `filesystem.write`, `knowledge.skill`, `orchestration.delegate`, `shell.execute` | `filesystem.write`, `orchestration.delegate`, `shell.execute` |

## Reproducirlo

```bash
operational-agents capabilities                 # esta misma matriz en la terminal
operational-agents capabilities <agent_id> --runtime <runtime_id> --json
```

---

<div align="center"><sub><a href="README.md">Documentación</a> · <a href="RUNTIME_CONTRACT.md">Runtimes</a> · <a href="CAPABILITY_MODEL.md">Capacidades</a></sub></div>
