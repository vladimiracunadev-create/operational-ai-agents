# GitHub

> Leer un repositorio no autoriza a escribir en él.

[Repositorio](../../README.md) · [Modelo de seguridad](../../docs/SECURITY_MODEL.md)

---

Los agentes pueden usar las herramientas de GitHub que su runtime les ofrezca. Ahora bien:

| Acción | ¿Basta con acceso de lectura? |
|---|:-:|
| Leer código, issues y releases | ✅ |
| Crear o comentar issues | ❌ gate humano |
| Modificar ramas o hacer push | ❌ gate humano |
| Abrir un pull request | ❌ gate humano |
| Publicar un release o editar el perfil público | ❌ gate humano |

Estas acciones exigen acceso explícito a la herramienta **y** aprobación humana en el momento de ejecutarlas. Ningún agente las deduce de tener credenciales disponibles.

Este repositorio no incluye tokens ni configura credenciales de GitHub.

---

<div align="center"><sub><a href="../../README.md">Repositorio</a> · <a href="../../docs/SECURITY_MODEL.md">Seguridad</a></sub></div>
