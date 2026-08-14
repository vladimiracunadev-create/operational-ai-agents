# Despliegue con Docker

> El panel en contenedor, sin privilegios y publicado solo en loopback del host.

[Repositorio](../../README.md) · [Modelo de seguridad](../../docs/SECURITY_MODEL.md)

---

```bash
docker compose up --build
```

## Postura de seguridad

| Control | Valor |
|---|---|
| Usuario | sin privilegios (`uid 10001`) |
| Sistema de archivos | `read_only: true`, con `tmpfs` para `/tmp` |
| Escalada de privilegios | `no-new-privileges:true` |
| Puerto publicado | `127.0.0.1:8765` únicamente |
| Healthcheck | consulta `/healthz` dentro del contenedor |

El contenedor no ejecuta modelos y no debe recibir credenciales. CI construye la imagen en cada push, la levanta y comprueba que el panel responde de verdad.

---

<div align="center"><sub><a href="../../README.md">Repositorio</a> · <a href="../../docs/SECURITY_MODEL.md">Seguridad</a></sub></div>
