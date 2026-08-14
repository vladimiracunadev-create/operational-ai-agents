# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y [versionado semántico](https://semver.org/lang/es/).

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

### Documentación

- README con catálogo, arquitectura, referencia de CLI, garantías de seguridad
  verificadas y modelo de madurez explícito.
- `docs/CLI.md` con la referencia completa de comandos, flags y códigos de retorno.
- Documentos de arquitectura, contrato de agente, modelo de seguridad,
  evaluación, madurez, evidencia, integración con Claude Code y con skills.
- 27 pruebas deterministas, incluidas la validación de enlaces relativos en los
  archivos Markdown, la coherencia de versión entre `pyproject.toml`, el
  catálogo y el README, y un guardián contra Markdown sangrado que GitHub
  renderizaría como bloque de código.
