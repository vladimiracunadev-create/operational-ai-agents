# Seguridad

> Cómo reportar una vulnerabilidad y qué garantiza —y qué no garantiza— este repositorio.

[Repositorio](README.md) · [Modelo de seguridad completo](docs/SECURITY_MODEL.md)

---

## Reportar una vulnerabilidad

> [!CAUTION]
> **No abras un issue público** ni publiques detalles explotables, secretos o trazas reales.

Usa el canal privado de avisos de seguridad de GitHub:

**[Reportar de forma privada →](https://github.com/vladimiracunadev-create/operational-ai-agents/security/advisories/new)**

Incluye: versión afectada, pasos de reproducción, impacto esperado y, si lo tienes, una propuesta de mitigación. Sanea cualquier dato antes de adjuntarlo.

## Alcance

| Dentro del alcance | Fuera del alcance |
|---|---|
| La CLI y sus comandos | El comportamiento del modelo dentro del runtime |
| El servidor del panel local | Vulnerabilidades de Claude Code |
| El exportador y el instalador | Los skills del toolkit externo |
| Los contratos, permisos y gates declarados | Configuraciones que el usuario relaje a propósito |

## Garantías

Todas están cubiertas por pruebas automatizadas que corren en cada push:

- La CLI **no** usa `shell=True` ni añade banderas para omitir permisos.
- Los agentes que escriben usan permisos normales y aislamiento en worktree.
- Los agentes de solo lectura deniegan `Write` y `Edit` explícitamente.
- El panel escucha en loopback; salir de ahí exige una variable de entorno explícita, y Compose publica el puerto solo en loopback del host.
- La evidencia es opt-in y pasa por redacción antes de persistir.
- El exportador nunca sobrescribe un agente que no administra.
- El catálogo público no contiene datos personales ni rutas locales.
- Publicar, desplegar, borrar o rotar credenciales siempre requiere aprobación humana.

## Límites conocidos

Se declaran porque omitirlos sería la clase de afirmación que este proyecto existe para evitar:

- **El panel local no tiene autenticación.** Es para loopback, no para exponerlo.
- **La redacción de secretos es heurística.** No sustituye la revisión humana antes de publicar evidencia.
- **El aislamiento en worktree aísla archivos, no efectos externos.** Un comando que llama a un servicio remoto sale de él.

El modelo de amenazas completo, con controles y pruebas asociadas, está en **[docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md)**.

## Dependencias

El paquete no declara dependencias de runtime. Las acciones de GitHub están fijadas por SHA de commit y Dependabot revisa mensualmente pip y GitHub Actions. CodeQL analiza el código en cada push y semanalmente.

---

<div align="center"><sub><a href="README.md">Repositorio</a> · <a href="docs/SECURITY_MODEL.md">Modelo de seguridad</a> · <a href="SUPPORT.md">Soporte</a></sub></div>
