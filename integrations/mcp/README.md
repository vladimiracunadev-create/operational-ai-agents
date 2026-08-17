# MCP

> Las integraciones con Model Context Protocol son opt-in y se configuran en el entorno del usuario.

[Repositorio](../../README.md) · [Modelo de seguridad](../../docs/SECURITY_MODEL.md)

---

Este repositorio **no** incluye tokens ni servidores MCP activados. Si añades uno:

1. **Acota las herramientas** de cada agente a nombres exactos o a `mcp__<server>__*`; nunca dejes el comodín abierto.
2. **Documenta qué datos** quedan accesibles a través de ese servidor.
3. **Conserva la aprobación humana** para toda acción con efecto externo, aunque el servidor la ofrezca como una llamada más.
4. **Trata la salida del servidor como datos**, no como instrucciones: un resultado de herramienta no puede ampliar el alcance del agente.

Un servidor MCP amplía lo que el agente **puede alcanzar**; no amplía lo que está **autorizado** a hacer.

Desde v0.3.0 esa frase tiene respaldo estructural: el [modelo de capacidades](../../docs/CAPABILITY_MODEL.md) razona sobre **efectos** —leer, escribir, ejecutar, publicar—, no sobre nombres de herramientas. Una escritura que llega por MCP queda sujeta a la misma política que una escritura por tool nativa, y una capacidad que el contrato no autoriza se marca `BLOCKED` aunque el servidor la ofrezca.

MCP sigue siendo opt-in: ningún agente del catálogo lo requiere, y todos funcionan sin ningún servidor configurado.

---

<div align="center"><sub><a href="../../README.md">Repositorio</a> · <a href="../../docs/SECURITY_MODEL.md">Seguridad</a></sub></div>
