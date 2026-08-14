# Roadmap

> De «el contrato está implementado» a «el agente se usa y se observa». Cada escalón exige evidencia, no más Markdown.

[Repositorio](README.md) · [Modelo de madurez](docs/MATURITY_MODEL.md) · [Changelog](CHANGELOG.md)

---

## v0.1 — base implementada ✅

- [x] Doce agentes transversales con contrato completo.
- [x] Catálogo como fuente única de verdad, con vistas generadas y sin drift.
- [x] Exportación a Claude Code que preserva los agentes del usuario.
- [x] Planificador determinista, panel local, validación y evaluaciones.
- [x] Políticas de seguridad verificadas por pruebas y modelo de madurez honesto.
- [x] CI multiplataforma, CodeQL y landing page publicada.

## v0.2 — uso real y evidencia

El salto que de verdad importa: hoy ningún agente ha demostrado resolver una misión real.

- [ ] Ejecutar cada agente sobre una tarea real controlada.
- [ ] Incorporar casos sanitizados y promover a `OPERATIONAL_LOCAL` **solo** los que cumplan los criterios.
- [ ] Registrar métricas de éxito, duración, costo, intervención humana y retrabajo.
- [ ] Evaluaciones model-graded versionadas por runtime y modelo.

> [!NOTE]
> Este hito no se cierra escribiendo documentación. Se cierra con casos revisados en `evidence/case-studies/`, uno por agente promovido.

## v0.3 — integraciones

- [ ] Adaptador para OpenAI Agents SDK.
- [ ] Adaptador local con Ollama, declarando capacidades y degradación.
- [ ] Integraciones MCP declarativas con allowlist por agente.
- [ ] Exportador de plugin de Claude Code.
- [ ] Sink de evidencia opcional vía OpenTelemetry.

## v1.0 — operación observada

- [ ] Contratos estables con migraciones documentadas.
- [ ] Tres o más agentes con uso recurrente y evidencia.
- [ ] Matriz de compatibilidad entre runtimes.
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
