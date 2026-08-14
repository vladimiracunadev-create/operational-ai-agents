# Roadmap

## v0.1 — base implementada

- [x] Diez agentes transversales.
- [x] Catálogo como fuente de verdad.
- [x] Exportación Claude Code.
- [x] Planificador, panel, validación y evals deterministas.
- [x] Políticas de seguridad y modelo de madurez.

## v0.2 — uso real y evidencia

- [ ] Ejecutar cada agente sobre una tarea real controlada.
- [ ] Incorporar casos sanitizados y promover solo los que cumplan `OPERATIONAL_LOCAL`.
- [ ] Métricas de éxito, duración, costo, intervención humana y retrabajo.
- [ ] Evaluaciones model-graded versionadas por runtime/modelo.

## v0.3 — integraciones

- [ ] Adaptador OpenAI Agents SDK.
- [ ] Adaptador local Ollama.
- [ ] Integraciones MCP declarativas con allowlists por agente.
- [ ] Exportador de plugin Claude Code.
- [ ] Evidence sink opcional OpenTelemetry.

## v1.0 — operación observada

- [ ] Contratos estables y migraciones documentadas.
- [ ] Tres o más agentes con uso recurrente y evidencia.
- [ ] Matriz de compatibilidad de runtimes.
- [ ] Auditoría de seguridad y recuperación end-to-end.

## No objetivos

- Sustituir `claude-skills-toolkit`.
- Duplicar casos de `langgraph-realworld`.
- Presentar demos como adopción empresarial.
- Incorporar agentes solo para aumentar el catálogo.
