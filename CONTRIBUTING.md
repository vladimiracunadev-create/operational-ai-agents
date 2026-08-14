# Contribuir

## Regla principal

Un nuevo elemento debe ser un **agente**, no un prompt largo, un skill, un script ni un caso sectorial de referencia. Debe recibir una misión completa, tomar decisiones acotadas, usar capacidades, respetar aprobaciones y entregar evidencia.

## Flujo

1. Ejecuta `operational-agents scaffold mi-agente --name "Mi Agente"`.
2. Completa el registro canónico en `catalog/agents.yaml`.
3. Redacta políticas, schemas y al menos tres evals.
4. Ejecuta `operational-agents sync`.
5. Ejecuta `operational-agents validate`, `operational-agents eval --all` y las pruebas.

> [!IMPORTANT]
> `agent.yaml`, `instructions.md`, `AGENT.md` y `README.md` son **vistas generadas**.
> No los edites: cambia el catálogo o el renderer en `src/operational_agents/render.py`
> y vuelve a ejecutar `sync`. CI rechaza cualquier drift.

## Criterios de aceptación

- ID único en kebab-case y descripción clara de delegación.
- Misión, entradas, entregables y no-objetivos explícitos.
- Tool allowlist mínima; mutaciones con `permissionMode: default` e idealmente `isolation: worktree`.
- Gates humanos para publicación, despliegue, borrado, credenciales y expansión de alcance.
- Salida con evidencia, verificaciones, riesgos residuales y estado honesto.
- Sin secretos, datos personales, rutas del autor ni afirmaciones de producción no demostradas.
- Documentación en español; identificadores y contratos técnicos en inglés estable.

## Calidad

Antes de abrir un PR, ejecuta la misma secuencia que corre CI:

```bash
make check
```

O paso a paso:

```bash
ruff check .
operational-agents sync --check
operational-agents validate
operational-agents eval --all
python -m unittest discover -s tests -v
```

CI además construye el wheel, levanta la imagen Docker y comprueba el panel, y
analiza el código con CodeQL. La referencia completa de comandos está en
[docs/CLI.md](docs/CLI.md).
