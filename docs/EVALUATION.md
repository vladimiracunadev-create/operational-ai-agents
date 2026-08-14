# Evaluación

## Capas

1. **Contrato:** campos, IDs, paths, tools, permisos y schemas.
2. **Plan determinista:** las fases, gates y entregables esperados aparecen para cada caso.
3. **Exportador:** cada definición Claude contiene frontmatter válido y prompt no vacío.
4. **Modelo:** ejecución sobre fixtures o repositorios controlados, aún no incluida en CI por costo y variabilidad.
5. **Operación real:** resultado, intervención humana, retrabajo, costo y efecto; requerido para promover madurez.

```bash
operational-agents eval --all
python -m unittest discover -s tests -v
```

Pasar las capas 1–3 demuestra `IMPLEMENTED`. No demuestra que el agente resolvió una misión real.

## Caso JSONL

Cada línea declara `id`, `task`, `expected_phases`, `expected_approvals` y `required_deliverables`. El evaluador no juzga inteligencia del modelo: verifica que el contrato no pierda controles al evolucionar.
