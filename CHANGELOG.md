# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y [versionado semántico](https://semver.org/lang/es/).

## [0.3.0] - 2026-08-17

El contrato deja de estar atado a un único ejecutor. Un agente ya podía describir su
misión sin nombrar proveedor; ahora también puede ejecutarse sin nombrarlo, porque
quién lo ejecuta pasó a ser un adaptador intercambiable y qué está autorizado a hacer
pasó a ser una capacidad resuelta, no un nombre de herramienta. Ninguna modalidad
anterior cambió: los trece agentes, los trece comandos previos, la exportación a
Claude Code y el funcionamiento offline siguen exactamente igual.

### Añadido

- **Capa de runtime** (`src/operational_agents/runtimes/`). `AgentRuntime` define el
  contrato común —declarar capacidades, detectar disponibilidad, preparar y ejecutar—
  y `run()` es un método plantilla cerrado: detecta, prepara, resuelve capacidades y
  solo entonces ejecuta. Un adaptador no decide el orden, así que no puede saltarse la
  resolución. El registro es extensible y admite adaptadores de terceros por entry
  point; un plugin roto se anota y se ignora en vez de tumbar la CLI.
- **Runtime `manual` de ejecución humana asistida.** El agente analiza, propone y
  entrega el paquete portable; la persona ejecuta. Cierra en `NOT_EXECUTED`, que no es
  un fallo sino la descripción honesta de lo que pasó. Es la modalidad correcta para
  producción, infraestructura crítica, datos regulados o rotación de credenciales — y
  además la prueba de que la abstracción sirve: recorre el mismo contrato, la misma
  resolución y la misma evidencia que Claude Code sin proveedor, sin clave y sin red.
- **Modelo de capacidades y efectos** (`capabilities.py`). Un agente pide
  `filesystem.search`, no `Grep`. Las capacidades se derivan de las `tools` de cada
  contrato, así que **ningún agente del catálogo tuvo que cambiar**; declararlas de
  forma explícita queda como opción. La política razona sobre efectos —leer, escribir,
  ejecutar, red— y por eso vale igual para una tool nativa, un servidor MCP o una API.
- **Resolución con cuatro estados.** `SUPPORTED`, `DEGRADED`, `UNSUPPORTED` y
  `BLOCKED`. Este último es el que importa: la allowlist del contrato es exhaustiva, de
  modo que una capacidad que el runtime ofrece y el agente no tiene autorizada se marca
  y **nunca** entra en el conjunto ejecutable. Acceso no es autorización, ahora también
  en el código.
- **`docs/COMPATIBILITY_MATRIX.md`, generada.** Se calcula resolviendo cada contrato
  contra las capacidades *declaradas* por cada adaptador, sin consultar el entorno: da
  el mismo resultado en cualquier máquina y `sync --check` la vigila. Dice que el
  contrato encaja; no dice que la ejecución cumpla la misión.
- **Sobre de evidencia portable** (`--evidence`). Misma forma venga del runtime que
  venga: agente, runtime, ejecución, capacidades resueltas, aprobaciones, resultado,
  verificación y riesgo residual. Sin credenciales, sin rutas absolutas del ejecutable
  y sin el prompt completo. Ninguna aprobación se marca como concedida por la CLI.
- **Tres comandos nuevos**: `runtimes`, `runtime inspect <id>` y `capabilities`, este
  último con la matriz completa si no se le pasa agente.
- `run` acepta `--target`, `--dry-run` y `--evidence`, y su `--runtime` sale del
  registro en lugar de una lista fija. `--runtime claude` sigue siendo válido y produce
  exactamente la misma invocación de antes.
- `doctor` diagnostica ahora cada runtime registrado, las integraciones opcionales
  (`git`, `gh`, `docker`, `ollama`) y los plugins que no cargaron, con estados
  `AVAILABLE` · `MISSING` · `OPTIONAL` · `UNSUPPORTED` y salida `--json`.
- **44 pruebas nuevas** (78 en total) para la capa de portabilidad: compatibilidad
  hacia atrás de la invocación de Claude, ausencia de bypass de permisos en cualquier
  adaptador, negativa a ejecutar cuando falta una capacidad requerida, error —nunca
  fallback silencioso— ante un runtime desconocido, resolución independiente del
  entorno, opcionalidad real de los skills, una que verifica por AST que el núcleo no
  importa nada fuera de la biblioteca estándar, y tres que levantan el control center
  en loopback para comprobar sus endpoints de verdad.
- `GET /api/runtimes` en el control center, y una tira en el panel que muestra qué
  runtimes hay registrados y cuáles están disponibles. El panel sigue sin ejecutar nada.
- `docs/RUNTIME_CONTRACT.md` y `docs/CAPABILITY_MODEL.md`.

- **`scenarios`: tres casos trabajados por agente**, en el catálogo y por tanto
  en todas las vistas generadas. Cada uno lleva el contexto concreto con nombres
  y cifras (`context`), el mensaje literal (`ask`), los pasos anclados a fases
  reales (`walkthrough`), la forma exacta de la salida (`returns`) y cómo cierra
  (`status`). Sustituye al campo `examples`, que solo llevaba frases sueltas.
  El validador rechaza un contexto de menos de 90 caracteres: un ejemplo que
  vale para cualquier repositorio no enseña cuándo delegarle este.
- **Dos diagramas por ficha**, generados del contrato: el *mapa de la misión*
  —qué necesita, qué entrega y dónde se detiene— y un *flujo operativo* que ya
  no es una línea recta, sino el tramo de solo lectura, el gate humano con su
  vuelta atrás si deniegas, y el tramo de ejecución acotada.
- Las fichas se reordenaron: los ejemplos van primero y la ficha técnica al
  final. Quien llega quiere saber si el agente le sirve, no cuántos turnos gasta.
- **Sección «¿Cuál necesito?» en el README**, con un diagrama de decisión que
  parte del problema del lector y desemboca en uno de los trece agentes.
- La tabla del catálogo muestra ahora las tres situaciones de cada agente, un
  ejemplo literal y el enlace directo a sus ejemplos completos.
- Las tarjetas de la landing abren con un ejemplo visible y despliegan los tres;
  el buscador indexa también los escenarios, así que se puede buscar por el
  problema propio y no solo por la categoría del contrato.
- `test_every_agent_explains_when_it_helps` comprueba que cada agente declara al
  menos dos escenarios completos, sin ejemplos repetidos, y que cada uno aparece
  tanto en la ficha humana como en las instrucciones del agente.

- **`professional-profile-agent`** — audita un perfil profesional público alojado en
  un servicio de terceros, lo contrasta con la evidencia real del portafolio y publica
  solo los textos aprobados. Es el primer agente del catálogo cuya superficie de destino
  es de **autoría humana y sin control de versiones**: no hay `git checkout` que revierta
  un campo sobrescrito, así que el contrato exige comprobar cada sección por su formulario
  de edición antes de declararla vacía, integrar sobre el texto existente mostrando el
  diff, y verificar cada guardado sobre la superficie recargada en vez de sobre la
  ausencia de error.
- Tres evaluaciones deterministas nuevas (39 en total).

### Cambiado

- La invocación de procesos se movió de `cli.py` al adaptador `claude`. La garantía de
  que nadie añade banderas que omitan permisos ahora cubre toda la superficie que
  invoca procesos, no solo la CLI.
- El badge de pruebas cuenta todos los módulos de `tests/`, no solo el primero: contar
  uno cuando hay varios convertía la cifra en falsa por defecto.
- La documentación de evaluación pasa a seis capas, con la resolución de capacidades
  como cuarta capa determinista en CI.
- Hitos renumerados: «uso real y evidencia» a `v0.4` e «integraciones» a `v0.5`, ya que
  `v0.3` la ocupa la portabilidad.
- Conteos de agentes y evaluaciones sincronizados en README, `RECRUITER.md` y
  `evidence/README.md` tras crecer el catálogo a trece.
- `schema_version` del catálogo a `1.3` por el cambio de `examples` a
  `scenarios`. El validador rechaza un escenario incompleto, con campos
  desconocidos, con menos de tres pasos o con un contexto genérico.

### Corregido

- **`__version__` del paquete declaraba `0.1.0`** mientras `pyproject.toml`, el
  catálogo y el badge del README ya iban por `0.2.0`. La prueba de coherencia de
  versión no cubría el módulo, así que el marcador derivó sin que nada fallara;
  ahora lo ancla también a él.
- **Hitos del `ROADMAP.md` renumerados** para coincidir con el README: «uso real
  y evidencia» pasa a `v0.3` e «integraciones» a `v0.4`. El número `v0.2` lo
  ocupó el release del 2026-08-13, que no contenía ninguna de las dos cosas.
- **El inventario del hito `v0.1` afirmaba trece agentes**, que es el catálogo de
  hoy y no lo que aquel release publicó. Ahora dice diez y nombra su versión, que
  es lo que la prueba de conteos distingue: un marcador de estado actual se
  sincroniza, una referencia histórica se conserva.
- **La tabla de madurez del README contaba doce agentes `IMPLEMENTED`** cuando el
  catálogo ya tenía trece. La prueba de conteos no lo veía porque la celda es un número
  suelto, sin la palabra «agentes» al lado.

## [0.2.0] - 2026-08-13

Dos agentes nuevos, fases que por fin explican qué hacen, y una revisión completa
de la documentación. Los doce agentes siguen declarando `IMPLEMENTED`.

### Añadido

- **`curriculum-evolution-agent`** — mantiene un programa formativo al día con su
  campo: investiga novedades, verifica cada fuente con una petición real, distingue
  brecha de contenido de simple cambio de terminología, y acepta «sin cambios
  sustantivos» como resultado legítimo.
- **`portfolio-publication-agent`** — reconcilia una superficie publicada —sitio,
  API, documentos generados y perfiles— con el estado real de los repositorios que
  la alimentan, integrando en vez de sobrescribir y publicando solo tras aprobación.
- **`phase_details`**: cada fase de cada agente declara qué ocurre exactamente en
  ella. El validador rechaza una fase sin explicar y una explicación sin fase.
- `docs/README.md` como índice de la documentación.
- Cuatro pruebas nuevas: anclas de Markdown, coherencia de los conteos de agentes
  escritos en la documentación, explicación de todas las fases y ausencia de datos
  personales en el catálogo público.

### Corregido

- **Dos anclas rotas en el README** (`#-cli` y `#-arquitectura`). Los emoji 🛠️ y 🏛️
  incluyen un variation selector U+FE0F que GitHub **conserva** al generar el ancla,
  de modo que el enlace apuntaba a un destino inexistente. Ahora una prueba valida
  todas las anclas de todos los Markdown con el mismo algoritmo de slug de GitHub.
- Instrucciones de agente que no decían nada: las 111 fases repetían la misma frase
  de relleno. Cada una tiene ahora su descripción propia, en `instructions.md` y en
  una tabla de la ficha.
- Conteos obsoletos de agentes en la documentación tras crecer el catálogo.

### Cambiado

- README rediseñado con el lenguaje visual del toolkit de skills, pero con las
  columnas propias de un agente: cuándo delegarle y dónde se detiene, en vez de
  triggers y dependencias.
- Reescritura completa de la documentación: cada documento abre con su propósito,
  lleva navegación y explicita sus límites conocidos.
- `schema_version` del catálogo a `1.1` por el campo `phase_details`.

## [0.1.0] - 2026-08-13

Primera publicación. Los diez agentes se declaran `IMPLEMENTED`: el contrato y el
paquete están validados localmente, sin afirmar adopción productiva.

### Catálogo y contratos

- Catálogo inicial de diez agentes operativos transversales.
- `catalog/agents.yaml` como fuente única de verdad, con contrato canónico,
  políticas, schemas de entrada/salida y evaluaciones por agente.
- Cuatro vistas generadas por agente —`agent.yaml`, `instructions.md`,
  `AGENT.md` y `README.md`— reconciliadas por `operational-agents sync`.
  `sync --check` falla ante cualquier drift y corre en CI.
- Modelo de madurez de cinco estados con criterios de promoción basados en
  evidencia, no en validez de Markdown.

### CLI

- Trece comandos sobre la biblioteca estándar de Python, sin dependencias
  runtime: `list`, `inspect`, `validate`, `sync`, `plan`, `packet`, `eval`,
  `export`, `uninstall`, `doctor`, `run`, `serve` y `scaffold`.
- Planificador determinista que produce el mismo `execution_id` para la misma
  pareja agente/tarea, sin invocar ningún modelo.
- Adaptador Claude Code autónomo y variante con skills precargados.
  El exportador nunca sobrescribe un agente que no administra.
- Control center local en loopback con `GET /healthz`, `GET /api/agents`,
  `GET /api/agents/<id>` y `POST /api/plan`.

### Seguridad

- La CLI no usa `shell=True` ni añade banderas para omitir permisos; una prueba
  automatizada lo verifica sobre el código fuente.
- Los agentes mutantes exigen `permission_mode: default` e `isolation: worktree`;
  los de solo lectura declaran `Write` y `Edit` como tools denegadas.
- El bind fuera de loopback requiere `OPERATIONAL_AGENTS_ALLOW_REMOTE_BIND=1`.
- La evidencia es opt-in y pasa por redacción de secretos antes de persistir.

### Integración continua

- Pipeline de seis jobs: lint con ruff, verificación de contratos, matriz de
  pruebas de nueve combinaciones (Linux, macOS y Windows × Python 3.11, 3.12
  y 3.13), build de wheel y sdist con instalación limpia, build de la imagen
  Docker con healthcheck real contra el panel, y un check agregado.
- Análisis estático de seguridad con CodeQL en cada push y semanalmente.
- Todas las acciones de GitHub fijadas por SHA.

### Landing page

- Sitio del proyecto publicado en GitHub Pages, generado desde el catálogo por
  `render_landing` y desplegado por el workflow `pages.yml`. La página es un
  único HTML autocontenido, sin dependencias externas ni recursos remotos:
  tema claro/oscuro, filtro de catálogo, diagrama SVG del flujo de decisión y
  las cifras leídas del propio repositorio. `sync --check` corre antes de
  desplegar, así que la página no puede afirmar algo distinto del catálogo.

### Documentación

- README con catálogo, arquitectura, referencia de CLI, garantías de seguridad
  verificadas y modelo de madurez explícito.
- `docs/CLI.md` con la referencia completa de comandos, flags y códigos de retorno.
- Documentos de arquitectura, contrato de agente, modelo de seguridad,
  evaluación, madurez, evidencia, integración con Claude Code y con skills.
- 29 pruebas deterministas, incluidas la validación de enlaces relativos en los
  archivos Markdown, la coherencia de versión entre `pyproject.toml`, el
  catálogo y el README, la correspondencia entre los badges numéricos del README
  y la realidad medida, y un guardián contra Markdown sangrado que GitHub
  renderizaría como bloque de código.
