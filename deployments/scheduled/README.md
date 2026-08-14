# Ejecución programada

> No se habilita por defecto, y esa es una decisión de diseño.

[Repositorio](../../README.md) · [Modelo de seguridad](../../docs/SECURITY_MODEL.md)

---

Un agente que se ejecuta solo, de forma recurrente y sin nadie mirando, invierte el principio del proyecto: la aprobación humana deja de estar en el camino crítico.

Si aun así montas una tarea recurrente, debe declarar:

| Aspecto | Por qué |
|---|---|
| Propietario | alguien responde por lo que haga |
| Frecuencia y costo | una ejecución recurrente gasta dinero y contexto |
| Límites de alcance | qué puede tocar sin preguntar, que debería ser muy poco |
| Idempotencia | dos ejecuciones seguidas no pueden duplicar efectos |
| Alertas | cómo se entera un humano de que falló o se bloqueó |
| Retención de evidencia | cuánto se guarda y cuándo se borra |
| Acciones que siguen exigiendo aprobación | publicar, desplegar, borrar y credenciales, siempre |

> [!WARNING]
> Programar la ejecución **no** convierte los gates humanos en opcionales. Un agente programado que llega a un gate se detiene y espera, o falla: nunca continúa por su cuenta.

---

<div align="center"><sub><a href="../../README.md">Repositorio</a> · <a href="../../docs/SECURITY_MODEL.md">Seguridad</a></sub></div>
