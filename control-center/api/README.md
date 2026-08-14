# API del control center

> Superficie HTTP local que expone `operational-agents serve`. Solo lectura, salvo la generación de planes — que tampoco muta nada.

[Repositorio](../../README.md) · [CLI](../../docs/CLI.md)

---

## Endpoints

| Método | Ruta | Devuelve |
|---|---|---|
| `GET` | `/healthz` | estado del servicio |
| `GET` | `/api/agents` | catálogo con id, nombre, descripción, estado, categoría y riesgo |
| `GET` | `/api/agents/<id>` | contrato completo de un agente; `404` si no existe |
| `POST` | `/api/plan` | plan determinista para `{agent_id, task, target?}` |

Todas las respuestas son JSON UTF-8 con `Cache-Control: no-store`.

## Garantías

- El planificador **no invoca ningún modelo**: la respuesta es determinista y gratuita.
- Un plan **no concede autorización**: enumera los gates que seguirán exigiendo decisión humana.
- El cuerpo de `POST` se limita a 128 KiB.
- Los accesos no se registran.

> [!CAUTION]
> El servidor **no implementa autenticación**. Escucha en loopback por defecto y salir de ahí exige declarar `OPERATIONAL_AGENTS_ALLOW_REMOTE_BIND=1`. No lo expongas a Internet.

---

<div align="center"><sub><a href="../../README.md">Repositorio</a> · <a href="../../docs/SECURITY_MODEL.md">Modelo de seguridad</a></sub></div>
