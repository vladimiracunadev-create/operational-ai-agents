# Instrucciones para agentes que mantienen este repositorio

`catalog/agents.yaml` es la fuente de verdad. Estos archivos son **vistas generadas** y no deben editarse a mano:

| Archivo generado | Renderer |
|---|---|
| `agents/<id>/agent.yaml` | serialización del registro canónico |
| `agents/<id>/instructions.md` | `render_instructions` |
| `agents/<id>/AGENT.md` | `render_claude` |
| `agents/<id>/README.md` | `render_agent_readme` |
| `site/index.html` | `render_landing` (landing page publicada en Pages) |

Para cambiarlos, modifica el catálogo o el renderer en `src/operational_agents/render.py` y ejecuta `operational-agents sync`. `sync --check` corre en CI y falla ante cualquier drift.

Antes de declarar una tarea terminada ejecuta:

```bash
PYTHONPATH=src python -m operational_agents sync --check
PYTHONPATH=src python -m operational_agents validate
PYTHONPATH=src python -m operational_agents eval --all
python -m unittest discover -s tests -v
```

No promociones la madurez de un agente sin evidencia real revisada. No agregues secretos, datos personales, rutas locales del autor ni publicación automática. Conserva aprobación humana para borrado, despliegue, releases, credenciales, servicios pagados y expansión material de alcance.
