# Referencia de CLI

`operational-agents` es la interfaz de línea de comandos del repositorio. Está escrita únicamente con la biblioteca estándar de Python: no requiere dependencias, ni clave API, ni conexión a un modelo salvo en `run`.

```bash
operational-agents [--root RUTA] <comando> [opciones]
```

| Opción global | Efecto |
|---|---|
| `--root RUTA` | usa otra raíz de repositorio en lugar de la detectada |

La raíz se resuelve en este orden: `--root` → variable de entorno `OPERATIONAL_AGENTS_ROOT` → búsqueda ascendente de `catalog/agents.yaml` desde el directorio actual.

## Códigos de retorno

| Código | Significado |
|:-:|---|
| `0` | la operación terminó correctamente |
| `1` | la operación se ejecutó pero el resultado es negativo: hay drift, errores de validación o evals fallidas |
| `2` | error de uso: agente desconocido, ruta inexistente, archivo ilegible o argumentos inválidos |

La separación entre `1` y `2` permite usar la CLI en CI sin confundir «encontré un problema real» con «me invocaste mal».

---

## Inspección

### `list`

Lista los agentes del catálogo.

```bash
operational-agents list
operational-agents list --json
```

| Flag | Efecto |
|---|---|
| `--json` | emite `id`, `name`, `status`, `category` y `risk` como JSON |

### `inspect <agent_id>`

Muestra el contrato de un agente: misión, fases, tools, skills opcionales y gates de aprobación.

```bash
operational-agents inspect repository-evolution-agent
operational-agents inspect release-governance-agent --json
```

`--json` devuelve el registro canónico completo, idéntico al de `catalog/agents.yaml`.

---

## Integridad

### `validate`

Valida el repositorio completo: campos obligatorios, IDs en kebab-case, unicidad, estados declarados en el modelo de madurez, tool allowlists no vacías, mínimo de fases, presencia de gates, coherencia entre permisos y capacidad de mutación, existencia de los ocho archivos de cada paquete, validez de los JSON y mínimo de tres evals por agente.

```bash
operational-agents validate
operational-agents validate --json
```

Devuelve `1` si existe al menos un problema de nivel `error`. Los `warning` se informan sin bloquear.

### `sync [--check]`

Regenera las vistas derivadas del catálogo. Estos archivos se consideran generados y **no deben editarse a mano**:

| Archivo generado | Origen |
|---|---|
| `agents/<id>/agent.yaml` | serialización del registro canónico |
| `agents/<id>/instructions.md` | instrucciones vendor-neutral |
| `agents/<id>/AGENT.md` | definición instalable en Claude Code |
| `agents/<id>/README.md` | ficha humana del contrato |
| `site/index.html` | landing page publicada en GitHub Pages |
| `docs/COMPATIBILITY_MATRIX.md` | resolución de cada agente contra cada runtime registrado |

```bash
operational-agents sync           # escribe los archivos derivados
operational-agents sync --check   # no escribe; devuelve 1 si hay drift
```

`sync --check` corre en CI: si alguien edita una vista generada en lugar del catálogo, la build falla.

---

## Planificación

### `plan <agent_id> --task ...`

Genera un plan determinista **sin invocar ningún modelo**. Sirve para revisar qué haría el agente, con qué fases y qué aprobaciones exigiría, antes de gastar un solo token.

```bash
operational-agents plan repository-evolution-agent \
  --task "Examina este repositorio y propone una evolución verificable"

operational-agents plan release-governance-agent \
  --task "Prepara el release 0.2.0" --target ./mi-repo --format json
```

| Flag | Efecto |
|---|---|
| `--task TEXTO` | **obligatorio**; la misión a planificar |
| `--target RUTA` | objetivo declarado del trabajo |
| `--format markdown\|json` | formato de salida (por defecto `markdown`) |

El plan es determinista en su identidad: la misma pareja agente/tarea produce siempre el mismo `execution_id`. Un plan **no** constituye autorización: enumera los gates que seguirán requiriendo una decisión humana.

### `packet <agent_id> --task ...`

Produce un paquete de prompt portable —instrucciones del agente más la misión— para usarlo en un runtime que no sea Claude Code.

```bash
operational-agents packet incident-root-cause-agent \
  --task "Investiga la caída del servicio de checkout" > packet.md
```

---

## Evaluación

### `eval [<agent_id>] [--all]`

Ejecuta las evaluaciones deterministas definidas en `agents/<id>/evals/cases.jsonl`. Cada caso declara `id`, `task`, `expected_phases`, `expected_approvals` y `required_deliverables`.

```bash
operational-agents eval --all
operational-agents eval security-remediation-agent
operational-agents eval --all --json
```

Devuelve `1` si algún caso falla. Estas evals no juzgan la inteligencia del modelo: verifican que el contrato no pierda controles al evolucionar. Ver [EVALUATION.md](EVALUATION.md).

---

## Distribución

### `export claude --target RUTA`

Proyecta el contrato canónico a definiciones compatibles con `.claude/agents/`.

```bash
operational-agents export claude --target ~/.claude/agents
operational-agents export claude --target ./.claude/agents
operational-agents export claude --preload-skills --target ~/.claude/agents
```

| Flag | Efecto |
|---|---|
| `--target RUTA` | **obligatorio**; directorio de destino |
| `--preload-skills` | declara los skills opcionales de cada agente en el frontmatter |

> [!IMPORTANT]
> El exportador **nunca sobrescribe un archivo que no administra**. Si en el destino existe un agente con el mismo nombre sin la marca `managed-by: operational-ai-agents`, la operación falla y conserva tu archivo intacto.

### `uninstall claude --target RUTA`

Elimina únicamente las definiciones administradas por este repositorio. Cualquier agente propio del usuario permanece.

```bash
operational-agents uninstall claude --target ~/.claude/agents
```

---

## Portabilidad

### `runtimes`

Lista los runtimes registrados, su tipo, si ejecutan de forma autónoma, la madurez del adaptador y si están disponibles en esta máquina.

```bash
operational-agents runtimes
operational-agents runtimes --json
```

```text
claude     MISSING    cli     autónomo  IMPLEMENTED  Claude Code
manual     AVAILABLE  human   asistido  IMPLEMENTED  Ejecución humana asistida
```

`MISSING` no es un error: significa que ese runtime no está instalado aquí. Todo lo demás de la CLI sigue funcionando sin él.

### `runtime inspect <runtime_id>`

Capacidades declaradas, modalidades de entrada, disponibilidad y límites de un runtime concreto.

```bash
operational-agents runtime inspect claude
operational-agents runtime inspect manual --json
```

Las capacidades declaradas **no** dependen del entorno: son las mismas en cualquier máquina. Lo que cambia es la disponibilidad, y se informa por separado.

### `capabilities [<agent_id>] [--runtime <runtime_id>]`

Resuelve lo que el agente necesita contra lo que el runtime ofrece y lo que el contrato autoriza.

```bash
operational-agents capabilities                                     # matriz agente × runtime
operational-agents capabilities incident-root-cause-agent           # todos los runtimes
operational-agents capabilities incident-root-cause-agent --runtime claude --json
```

| Estado | Significado |
|---|---|
| `SUPPORTED` | el runtime ofrece de forma nativa todo lo requerido |
| `DEGRADED` | está todo, pero alguna capacidad es condicional |
| `UNSUPPORTED` | falta al menos una capacidad requerida; `run` se negará a ejecutar |
| `BLOCKED` | el runtime la ofrece y el contrato del agente **no** la autoriza |

El modelo completo está en [CAPABILITY_MODEL.md](CAPABILITY_MODEL.md), y la matriz generada en [COMPATIBILITY_MATRIX.md](COMPATIBILITY_MATRIX.md).

---

## Operación

### `doctor [--skills-dir RUTA] [--json]`

Diagnostica el entorno: versión de Python, disponibilidad de cada runtime registrado, integraciones opcionales (`git`, `gh`, `docker`, `ollama`), skills faltantes y plugins que no cargaron.

```bash
operational-agents doctor
operational-agents doctor --skills-dir ~/.claude/skills
operational-agents doctor --json
```

| Estado | Significado |
|---|---|
| `AVAILABLE` | está instalado y se encontró |
| `MISSING` | el runtime está registrado pero no se encuentra aquí |
| `OPTIONAL` | herramienta complementaria ausente; nada del núcleo la necesita |
| `UNSUPPORTED` | requisito incumplido (hoy solo Python < 3.11) |

Devuelve `1` si la versión de Python es inferior a 3.11. Nada más hace fallar el diagnóstico: validar, planificar y evaluar no necesitan ningún runtime.

### `run <agent_id> --runtime <runtime_id> --task ...`

Ejecuta el agente mediante un runtime ya disponible.

```bash
operational-agents run repository-evolution-agent \
  --runtime claude \
  --cwd /ruta/al/repositorio \
  --task "Detecta brechas y prepara un plan; no publiques cambios"

operational-agents run incident-root-cause-agent \
  --runtime manual \
  --task "Investiga la caída del checkout de anoche" \
  --evidence evidence/executions/checkout.json
```

| Flag | Efecto |
|---|---|
| `--runtime ID` | **obligatorio**; `claude` o `manual` (más los que aporte un plugin) |
| `--task TEXTO` | **obligatorio**; la misión |
| `--target TEXTO` | destino declarado de la tarea, si aplica |
| `--cwd RUTA` | directorio de trabajo (por defecto, el actual) |
| `--dry-run` | prepara, resuelve capacidades y muestra el plan **sin ejecutar** |
| `--evidence RUTA` | escribe el sobre de evidencia portable |

Antes de ejecutar nada, `run` resuelve capacidades. Si falta una requerida devuelve `1` y nombra cuál: no se inventa la capacidad ni se declara un éxito que no ocurrió. Con `--runtime manual` el resultado es siempre `NOT_EXECUTED` y la salida es el paquete que ejecuta una persona.

> [!WARNING]
> `run` construye la invocación como una lista de argumentos, sin `shell=True`, y **no añade ninguna bandera que omita permisos**. Las acciones destructivas, la publicación, el despliegue y las credenciales siguen sujetas a la aprobación que el propio runtime solicita.

### `serve [--host] [--port]`

Levanta el panel local para explorar contratos y generar planes deterministas desde el navegador.

```bash
operational-agents serve
operational-agents serve --host 127.0.0.1 --port 8765
```

| Endpoint | Respuesta |
|---|---|
| `GET /healthz` | estado del servicio |
| `GET /api/agents` | catálogo completo |
| `GET /api/agents/<id>` | contrato de un agente |
| `GET /api/runtimes` | runtimes registrados y su disponibilidad |
| `POST /api/plan` | plan determinista para una tarea |

> [!CAUTION]
> El servidor **no implementa autenticación**. Escucha en loopback por defecto; enlazarlo a una interfaz externa exige declarar `OPERATIONAL_AGENTS_ALLOW_REMOTE_BIND=1` de forma explícita y no debe exponerse a Internet.

---

## Autoría

### `scaffold <agent_id> --name "Nombre"`

Crea un borrador **no catalogado** en `agents/_<id>-draft/`. El agente no es instalable hasta que se registre en `catalog/agents.yaml` y se ejecute `sync`.

```bash
operational-agents scaffold mi-agente --name "Mi Agente"
```

El flujo completo para incorporar un agente está en [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## Uso en CI

La secuencia que ejecuta este repositorio en cada push:

```bash
operational-agents sync --check     # sin drift respecto del catálogo
operational-agents validate         # integridad de los paquetes
operational-agents eval --all       # evaluaciones deterministas
python -m unittest discover -s tests -v
```

Los cuatro comandos son deterministas, offline y sin coste. `sync --check` cubre también la matriz de compatibilidad, así que un adaptador que cambie sus capacidades sin regenerarla hace fallar la build.
