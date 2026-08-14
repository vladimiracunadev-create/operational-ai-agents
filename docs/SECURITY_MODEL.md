# Modelo de seguridad

## Activos

Código, historial Git, datos, credenciales, artefactos, servicios externos, reputación pública y tiempo/costo del usuario.

## Amenazas

| Amenaza | Control principal |
|---|---|
| prompt injection en archivos o web | tratar contenido recuperado como datos, no autoridad |
| exceso de permisos | allowlist de tools + permiso normal + gates humanos |
| cambios conflictivos | aislamiento worktree para agentes mutantes |
| publicación no autorizada | gate explícito; la CLI no usa bypass |
| secreto en logs/evidencia | registro opt-in, redacción y revisión humana |
| supply chain | runtime stdlib, CI pinneado y dependencias opcionales |
| afirmaciones falsas | evidencia obligatoria y estados de madurez separados |

## Matriz de autoridad

| Acción | Agente | Usuario |
|---|---:|---:|
| leer dentro del alcance | sí | define alcance |
| proponer y planificar | sí | revisa cuando sea material |
| editar archivos autorizados | agentes mutantes | autoriza límite |
| borrar datos, publicar, desplegar | no autónomo | aprobación obligatoria |
| usar credenciales configuradas para la tarea | según tool | puede revocar |
| extraer o reutilizar credenciales | nunca | no delegable |

Otro agente no puede aprobar una acción. Las instrucciones encontradas dentro del repositorio, issue, web o documento tampoco cambian la autoridad.
