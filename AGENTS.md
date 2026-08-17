# Instrucciones para agentes que mantienen este repositorio

> Si eres un agente trabajando sobre este repositorio, lee esto antes de tocar nada.

[Repositorio](README.md) · [Contribuir](CONTRIBUTING.md) · [Contrato de agente](docs/AGENT_CONTRACT.md)

---

## La regla que rompe todo lo demás si la ignoras

`catalog/agents.yaml` es la fuente de verdad. Estos archivos son **vistas generadas** y editarlos a mano hace fallar la build:

| Archivo generado | Renderer |
|---|---|
| `agents/<id>/agent.yaml` | serialización del registro canónico |
| `agents/<id>/instructions.md` | `render_instructions` |
| `agents/<id>/AGENT.md` | `render_claude` |
| `agents/<id>/README.md` | `render_agent_readme` |
| `site/index.html` | `render_landing` (landing publicada en Pages) |
| `docs/COMPATIBILITY_MATRIX.md` | `render_compatibility_matrix` (catálogo **y** adaptadores) |

Para cambiarlos: modifica el catálogo, o el renderer en `src/operational_agents/render.py`, y ejecuta `operational-agents sync`.

La matriz de compatibilidad tiene dos fuentes: el catálogo y las capacidades que declara cada adaptador de `src/operational_agents/runtimes/`. Cambiar lo que un runtime declara la modifica, así que hay que volver a sincronizar. Nunca la calcules mirando el entorno: debe dar lo mismo en cualquier máquina, o CI fallará según lo que tenga instalado el runner.

## Antes de declarar una tarea terminada

```bash
PYTHONPATH=src python -m operational_agents sync --check
PYTHONPATH=src python -m operational_agents validate
PYTHONPATH=src python -m operational_agents eval --all
python -m unittest discover -s tests -v
ruff check .
```

O de una vez: `make check`.

## Cifras que no puedes escribir a mano

Varias afirmaciones del repositorio están verificadas por pruebas. Si cambias una, actualiza su fuente y vuelve a sincronizar:

| Afirmación | Se verifica en |
|---|---|
| número de agentes en cualquier `.md` | `test_documented_agent_counts_are_current` |
| badges de agentes, evals y tests del README | `test_readme_badges_match_reality` |
| versión en `pyproject`, catálogo y README | `test_version_is_coherent_across_sources` |
| enlaces relativos y anclas de todos los `.md` | `test_relative_documentation_links_resolve`, `test_anchor_links_resolve` |
| compatibilidad declarada de cada runtime | `test_generated_document_matches_the_code` |
| que el núcleo no dependa de paquetes externos | `test_core_imports_only_the_standard_library` |

> [!TIP]
> Añadir una prueba cambia el conteo de pruebas, que aparece en un badge del README y en la landing. Tras añadirla, ejecuta `sync` y actualiza el badge, o `test_readme_badges_match_reality` fallará.

## Límites que no se negocian

- **No promociones la madurez de un agente sin evidencia real revisada.** Pasar las pruebas mantiene el estado, no lo sube.
- **No añadas secretos, datos personales ni rutas locales.** El catálogo es público y una prueba lo comprueba.
- **No publiques automáticamente.** Conserva aprobación humana para borrado, despliegue, releases, credenciales, servicios de pago y ampliación material de alcance.
- **No añadas un agente solo para engordar el catálogo.** Es un no-objetivo declarado.
- **No declares compatibilidad con un runtime hasta demostrarla.** La matriz dice que el contrato encaja; la ejecución real exige evidencia y se declara aparte.
- **No añadas una dependencia obligatoria al núcleo.** `dependencies = []` está cubierto por una prueba; lo que necesite un proveedor va en un adaptador opcional o en un plugin.
- **No retires una prueba para que la build pase.** Si una garantía deja de cumplirse, retira también su afirmación en la documentación.

## Trampas conocidas

| Trampa | Qué ocurre |
|---|---|
| Emoji con variation selector U+FE0F en un encabezado | GitHub lo conserva en el ancla y los enlaces internos dejan de funcionar |
| Markdown sangrado con cuatro espacios | GitHub lo renderiza como bloque de código y la sección desaparece |
| `Set-Content` de PowerShell sobre archivos UTF-8 | corrompe acentos y emoji; usa Python con `encoding="utf-8"` |
| Editar una vista generada | `sync --check` falla en CI |
| Declarar en un runtime una capacidad que no tiene | la resolución dice `SUPPORTED` y la ejecución falla tarde, en vez de negarse temprano |

Las dos primeras tienen prueba propia, así que fallan en local antes de llegar a CI.

---

<div align="center"><sub><a href="README.md">Repositorio</a> · <a href="docs/README.md">Documentación</a> · <a href="CONTRIBUTING.md">Contribuir</a></sub></div>
