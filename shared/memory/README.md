# Memoria

> La memoria conserva contexto entre sesiones. No es una fuente de verdad ni un sustituto de verificar.

[Repositorio](../../README.md) · [Contrato de agente](../../docs/AGENT_CONTRACT.md)

---

Cada agente declara en su contrato un alcance de memoria — `project` o `local` — que el adaptador de Claude Code traslada a su frontmatter.

## Qué puede conservar

Decisiones tomadas, patrones observados del repositorio y convenciones acordadas con el usuario.

## Qué nunca debe conservar

> [!CAUTION]
> Secretos, credenciales, datos personales y **aprobaciones**.

Una aprobación es puntual y acotada: no se recuerda para la próxima vez. Un agente que «recuerda» que se le autorizó a publicar ha convertido un permiso de una sola vez en uno permanente — exactamente lo que el modelo de seguridad impide.

## Regla operativa

Cada misión vuelve a verificar el estado y los permisos actuales. Si la memoria contradice lo observado, **gana lo observado**.

---

<div align="center"><sub><a href="../../README.md">Repositorio</a> · <a href="../../docs/SECURITY_MODEL.md">Seguridad</a></sub></div>
