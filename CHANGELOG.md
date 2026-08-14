# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y [versionado semántico](https://semver.org/lang/es/).

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

Primera publicación. Los doce agentes se declaran `IMPLEMENTED`: el contrato y el
paquete están validados localmente, sin afirmar adopción productiva.

### Catálogo y contratos

- Catálogo inicial de doce agentes operativos transversales.
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
