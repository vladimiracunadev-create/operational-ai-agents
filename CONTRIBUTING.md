# Contribuir

> Cómo se propone un agente nuevo, qué criterios debe cumplir y qué se verifica antes de aceptarlo.

[Repositorio](README.md) · [Documentación](docs/README.md) · [Contrato de agente](docs/AGENT_CONTRACT.md)

---

## Regla principal

Un elemento nuevo debe ser un **agente**: no un prompt largo, no un skill, no un script y no un caso sectorial de referencia.

Para serlo tiene que recibir una misión completa, tomar decisiones acotadas, seleccionar capacidades, respetar aprobaciones y entregar evidencia. Si lo que propones aporta **una** capacidad dentro del contexto actual, su hogar es [`claude-skills-toolkit`](https://github.com/vladimiracunadev-create/claude-skills-toolkit), no este repositorio.

> [!TIP]
> Prueba rápida: si puedes describirlo como «una función que hace X», es un skill. Si tienes que describirlo como «alguien que se encarga de X y responde por el resultado», es un agente.

## Antes de escribir nada

Comprueba que ningún agente del catálogo ya cubra la misión:

```bash
operational-agents list
operational-agents inspect <agent-id>
```

Un solapamiento parcial no descalifica la propuesta, pero el PR debe explicar **qué hace el agente nuevo que ninguno de los existentes hace**. Ampliar el catálogo por ampliarlo es un no-objetivo declarado del proyecto.

## Flujo

1. **Esbozar** — `operational-agents scaffold mi-agente --name "Mi Agente"` crea un borrador no catalogado.
2. **Registrar** — añade la entrada canónica en `catalog/agents.yaml`.
3. **Escribir a mano** lo que no se genera: `policies/policy.yaml`, los dos schemas y al menos tres evaluaciones.
4. **Generar** — `operational-agents sync` produce las vistas derivadas.
5. **Verificar** — `make check` o la secuencia completa de abajo.

> [!IMPORTANT]
> `agent.yaml`, `instructions.md`, `AGENT.md` y `README.md` son **vistas generadas**. No los edites: cambia el catálogo o el renderer en `src/operational_agents/render.py` y vuelve a ejecutar `sync`. CI rechaza cualquier divergencia.

## Criterios de aceptación

### Identidad y alcance

- ID único en kebab-case y `delegate_when` que permita a un runtime elegirlo sin ambigüedad.
- Misión, entradas requeridas, entregables y no-objetivos explícitos.
- **Cada fase con su descripción en `phase_details`.** Una fase sin explicar produce instrucciones que no dicen nada, y el validador la rechaza.

### Permisos

- Tool allowlist **mínima**: lo que no se necesita, no se declara.
- Si declara `Write` o `Edit`: `permission_mode: default` e `isolation: worktree`.
- Si es de solo lectura: `Write` y `Edit` en `disallowed_tools`, denegados explícitamente.
- Gates humanos para publicar, desplegar, borrar, credenciales, servicios de pago y ampliación de alcance.

### Honestidad

- Estado inicial `IMPLEMENTED`. Nunca declares una madurez que no puedas respaldar con evidencia revisada.
- Salida con evidencia, verificaciones, riesgos residuales y estado explícito.
- Al menos tres evaluaciones que prueben **propiedades distintas**; tres copias del mismo caso pasan la cuenta pero no aportan garantía.

### Contenido

- **Sin secretos, sin datos personales, sin rutas del autor.** El catálogo es público y una prueba lo verifica.
- **Genérico, no personal.** Un agente atado a tus repositorios, tus rutas o tu nombre no es reutilizable: parametrízalo por patrón, no por identidad.
- Documentación en español; identificadores y contratos técnicos en inglés estable.

## Calidad

Antes de abrir un PR, ejecuta lo mismo que ejecuta CI:

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

CI además construye el wheel, levanta la imagen Docker y comprueba el panel en vivo, analiza el código con CodeQL y despliega la landing. La referencia completa de comandos está en [docs/CLI.md](docs/CLI.md).

## Qué revisa un mantenedor

| Pregunta | Dónde se ve |
|---|---|
| ¿Es un agente y no un skill disfrazado? | `mission`, `phases`, `approval_points` |
| ¿Se solapa con el catálogo? | comparación con `operational-agents list` |
| ¿Los permisos son los mínimos? | `tools` frente a lo que las fases necesitan |
| ¿Se detiene donde debe? | `approval_points` frente a las acciones irreversibles |
| ¿Se entiende qué hace en cada fase? | `phase_details` |
| ¿Afirma algo que no puede demostrar? | `status` y las evaluaciones |

---

<div align="center"><sub><a href="README.md">Repositorio</a> · <a href="docs/AGENT_CONTRACT.md">Contrato</a> · <a href="CODE_OF_CONDUCT.md">Código de conducta</a></sub></div>
