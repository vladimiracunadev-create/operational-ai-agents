# Roadmap

> De «el contrato está implementado» a «el agente se usa y se observa». Cada escalón exige evidencia, no más Markdown.

[Repositorio](README.md) · [Modelo de madurez](docs/MATURITY_MODEL.md) · [Changelog](CHANGELOG.md)

---

## v0.1 — base implementada ✅

- [x] Diez agentes transversales con contrato completo en v0.1.0.
- [x] Catálogo como fuente única de verdad, con vistas generadas y sin drift.
- [x] Exportación a Claude Code que preserva los agentes del usuario.
- [x] Planificador determinista, panel local, validación y evaluaciones.
- [x] Políticas de seguridad verificadas por pruebas y modelo de madurez honesto.
- [x] CI multiplataforma, CodeQL y landing page publicada.

## v0.3 — portabilidad ✅

El contrato deja de estar atado a un único ejecutor, sin que ninguna modalidad anterior deje de funcionar.

- [x] Interfaz `AgentRuntime` y registro extensible, con entry point para plugins de terceros.
- [x] Adaptador `claude` con la misma invocación de siempre, ahora detrás del contrato común.
- [x] Runtime `manual` de ejecución humana asistida: sin proveedor, sin clave API y sin red.
- [x] Modelo de capacidades y efectos, con resolución `SUPPORTED` · `DEGRADED` · `UNSUPPORTED` · `BLOCKED`.
- [x] Matriz de compatibilidad generada desde el código y verificada por `sync --check`.
- [x] Sobre de evidencia portable, comparable entre runtimes.

> [!NOTE]
> La matriz demuestra que **el contrato encaja**, no que la ejecución cumpla la misión. Eso pertenece al hito siguiente y exige evidencia.

## v0.4 — uso real y evidencia

El salto que de verdad importa: hoy ningún agente ha demostrado resolver una misión real.

- [ ] Ejecutar cada agente sobre una tarea real controlada.
- [ ] Incorporar casos sanitizados y promover a `OPERATIONAL_LOCAL` **solo** los que cumplan los criterios.
- [ ] Registrar métricas de éxito, duración, costo, intervención humana y retrabajo.
- [ ] Evaluaciones model-graded versionadas por runtime y modelo.

> [!NOTE]
> Este hito no se cierra escribiendo documentación. Se cierra con casos revisados en `evidence/case-studies/`, uno por agente promovido.

## v0.5 — integraciones

- [ ] Segundo runtime autónomo real (Codex CLI o Gemini CLI) con sus evaluaciones por runtime.
- [ ] Adaptador local con Ollama, declarando capacidades y degradación.
- [ ] Adaptador para OpenAI Agents SDK.
- [ ] Integraciones MCP declarativas como proveedores de capacidad, con allowlist por agente.
- [ ] Exportador de plugin de Claude Code.
- [ ] Sink de evidencia opcional vía OpenTelemetry.

## v1.0 — operación observada

- [ ] Contratos estables con migraciones documentadas.
- [ ] Tres o más agentes con uso recurrente y evidencia.
- [ ] Compatibilidad demostrada con ejecuciones reales por runtime, no solo resuelta.
- [ ] Auditoría de seguridad y prueba de recuperación de extremo a extremo.

## No objetivos

Declarados para que el proyecto no crezca por inercia:

| No objetivo | Por qué |
|---|---|
| Sustituir `claude-skills-toolkit` | un skill y un agente resuelven problemas distintos |
| Duplicar los casos de `langgraph-realworld` | ahí viven los procesos sectoriales de referencia |
| Presentar demos como adopción empresarial | contradice el modelo de madurez |
| Incorporar agentes solo para aumentar el catálogo | el tamaño no es una métrica de valor |
| Convertirse en un framework de agentes de propósito general | el núcleo es contractual, no un motor |

---

<div align="center"><sub><a href="README.md">Repositorio</a> · <a href="docs/MATURITY_MODEL.md">Madurez</a> · <a href="CONTRIBUTING.md">Contribuir</a></sub></div>
