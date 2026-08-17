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
| ejecutar un agente fuera de Claude Code | [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md) |
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

### Portabilidad

| Documento | Contenido |
|---|---|
| [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md) | qué debe cumplir un runtime, cómo se añade uno y por qué no hay fallback automático |
| [CAPABILITY_MODEL.md](CAPABILITY_MODEL.md) | capacidades, efectos, autorización y los cuatro estados de resolución |
| [COMPATIBILITY_MATRIX.md](COMPATIBILITY_MATRIX.md) | qué agente opera bajo qué runtime **(generado)** |

### Operación

| Documento | Contenido |
|---|---|
| [CLI.md](CLI.md) | los dieciséis comandos, sus flags, salidas y códigos de retorno |
| [CLAUDE_CODE.md](CLAUDE_CODE.md) | cómo se proyecta el contrato al runtime de Claude Code |
| [SKILLS_INTEGRATION.md](SKILLS_INTEGRATION.md) | integración opcional con `claude-skills-toolkit` |

### Garantías

| Documento | Contenido |
|---|---|
| [SECURITY_MODEL.md](SECURITY_MODEL.md) | amenazas, controles, permisos y gates humanos |
| [EVALUATION.md](EVALUATION.md) | las seis capas de evaluación y qué demuestra cada una |
| [EVIDENCE_GUIDE.md](EVIDENCE_GUIDE.md) | qué evidencia se registra, cómo se sanitiza y qué nunca se guarda |

---

## Tres ideas que atraviesan todo el proyecto

**Acceso no es autorización.** Que un agente pueda leer un repositorio no le permite publicar, desplegar, borrar ni rotar credenciales. Cada una de esas acciones tiene un gate humano explícito y una aprobación acotada no habilita las fases siguientes.

**Evidencia sobre apariencia.** Una afirmación sin comando, archivo o fuente que la respalde es una hipótesis, y se etiqueta como tal. Por eso ningún agente se declara productivo por tener un Markdown válido.

**Una sola fuente de verdad.** `catalog/agents.yaml` manda. Los manifiestos, las instrucciones, las definiciones de Claude Code, las fichas de cada agente, la landing page y la matriz de compatibilidad se generan desde ahí, y CI rechaza cualquier divergencia.

**Agente ≠ runtime.** El contrato describe una misión; ejecutarla es problema de un adaptador. Por eso el mismo agente funciona con Claude Code o preparado para que lo ejecute una persona, sin cambiar una línea de su contrato.

---

<div align="center"><sub><a href="../README.md">Repositorio</a> · <a href="../CONTRIBUTING.md">Contribuir</a> · <a href="../CHANGELOG.md">Changelog</a></sub></div>
