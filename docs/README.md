# 📖 Documentación

> Todo el proyecto es inspeccionable sin ejecutar nada y sin clave API. Esta carpeta explica cómo está construido y por qué toma las decisiones que toma.

[← Volver al repositorio](../README.md)

---

## Por dónde empezar

| Si quieres… | Lee |
|---|---|
| instalar y usar los agentes | [INSTALL.md](../INSTALL.md) y luego [CLI.md](CLI.md) |
| entender qué es un agente aquí | [AGENT_CONTRACT.md](AGENT_CONTRACT.md) |
| saber cómo encaja todo | [ARCHITECTURE.md](ARCHITECTURE.md) |
| conocer los límites de seguridad | [SECURITY_MODEL.md](SECURITY_MODEL.md) |
| proponer un agente nuevo | [CONTRIBUTING.md](../CONTRIBUTING.md) |
| mantener el repositorio con un agente | [AGENTS.md](../AGENTS.md) |

## Referencia completa

### Fundamentos

| Documento | Contenido |
|---|---|
| [AGENT_CONTRACT.md](AGENT_CONTRACT.md) | qué campos declara un agente, qué invariantes cumple y por qué |
| [ARCHITECTURE.md](ARCHITECTURE.md) | límites del sistema, componentes, fuente de verdad y flujo de mutación |
| [MATURITY_MODEL.md](MATURITY_MODEL.md) | los cinco estados y qué evidencia exige cada promoción |

### Operación

| Documento | Contenido |
|---|---|
| [CLI.md](CLI.md) | los trece comandos, sus flags, salidas y códigos de retorno |
| [CLAUDE_CODE.md](CLAUDE_CODE.md) | cómo se proyecta el contrato al runtime de Claude Code |
| [SKILLS_INTEGRATION.md](SKILLS_INTEGRATION.md) | integración opcional con `claude-skills-toolkit` |

### Garantías

| Documento | Contenido |
|---|---|
| [SECURITY_MODEL.md](SECURITY_MODEL.md) | amenazas, controles, permisos y gates humanos |
| [EVALUATION.md](EVALUATION.md) | las cinco capas de evaluación y qué demuestra cada una |
| [EVIDENCE_GUIDE.md](EVIDENCE_GUIDE.md) | qué evidencia se registra, cómo se sanitiza y qué nunca se guarda |

---

## Tres ideas que atraviesan todo el proyecto

**Acceso no es autorización.** Que un agente pueda leer un repositorio no le permite publicar, desplegar, borrar ni rotar credenciales. Cada una de esas acciones tiene un gate humano explícito y una aprobación acotada no habilita las fases siguientes.

**Evidencia sobre apariencia.** Una afirmación sin comando, archivo o fuente que la respalde es una hipótesis, y se etiqueta como tal. Por eso ningún agente se declara productivo por tener un Markdown válido.

**Una sola fuente de verdad.** `catalog/agents.yaml` manda. Los manifiestos, las instrucciones, las definiciones de Claude Code, las fichas de cada agente y la landing page se generan desde ahí, y CI rechaza cualquier divergencia.

---

<div align="center"><sub><a href="../README.md">Repositorio</a> · <a href="../CONTRIBUTING.md">Contribuir</a> · <a href="../CHANGELOG.md">Changelog</a></sub></div>
