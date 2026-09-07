# Guía de evidencia

> Qué se registra cuando un agente trabaja, cómo se sanitiza y qué no debe guardarse nunca. La evidencia es la única vía para promover la madurez de un agente.

[← Documentación](README.md) · [Repositorio](../README.md)

---

## Principio

Registra lo mínimo que demuestre una decisión o un resultado. Prefiere **hashes, conteos, comandos y extractos** antes que volcados completos: un log entero rara vez prueba más que la línea que importa, y multiplica el riesgo de filtrar algo.

## Qué debe contener un caso

| Campo | Por qué |
|---|---|
| agente y versión | el contrato cambia; la evidencia caduca con él |
| objetivo y alcance | distingue lo que se pidió de lo que se hizo |
| autorización recibida | qué permitió el usuario y cuándo |
| resultado | `COMPLETED`, `PARTIAL`, `BLOCKED` o `NO_CHANGE` |
| verificaciones | qué comando se ejecutó y qué devolvió |
| intervención humana | dónde hizo falta una persona y por qué |
| limitaciones | qué quedó sin comprobar |
| fecha | absoluta, nunca «hoy» ni «la semana pasada» |

Los eventos operacionales usan [`shared/observability/event.schema.json`](../shared/observability/event.schema.json): además de agente y ejecución, registran herramienta, referencias de entrada, salida acotada, duración, confianza, referencias de evidencia y decisión humana. En control financiero se referencian los originales por hash e identificador; nunca se copian claves privadas, material de firma ni instrucciones ejecutables dentro del hallazgo.

La plantilla está en `evidence/templates/case-study.md`.

## Qué no se guarda nunca

> [!CAUTION]
> Nada de esto debe llegar a `evidence/`, ni siquiera en un extracto:
>
> tokens · cookies · credenciales · claves privadas · datos personales · prompts privados de terceros · código confidencial ajeno · URLs firmadas · rutas locales que identifiquen a una persona · nombres de clientes.

## Cómo se sanitiza

1. **Redacción automática al registrar.** El módulo `redaction` sustituye patrones de token, contraseña y cabecera de autorización. Es una primera barrera heurística.
2. **Revisión humana antes de mover.** Ningún artefacto pasa a `case-studies/` sin que una persona lo lea entero.
3. **Reemplazo, no borrado silencioso.** Si eliminas un valor, deja constancia (`<redactado: motivo>`) para que el caso siga siendo legible.

> [!WARNING]
> La redacción automática **no** sustituye la revisión. Reduce el accidente frecuente; no detecta lo que no coincide con sus patrones.

## Estructura de la carpeta

| Ruta | Contenido | ¿Se versiona? |
|---|---|---|
| `evidence/executions/` | artefactos locales de ejecuciones | ❌ ignorado por git |
| `evidence/evaluations/` | resultados de evaluaciones conservados | ✅ si están sanitizados |
| `evidence/case-studies/` | casos revisados que respaldan la madurez | ✅ tras revisión humana |
| `evidence/templates/` | plantillas | ✅ |

## Relación con la madurez

Un caso sanitizado y revisado es lo que permite promover un agente de `IMPLEMENTED` a `OPERATIONAL_LOCAL`. Sin él, pasar todas las pruebas **mantiene** el estado, pero no lo sube. Los criterios están en [MATURITY_MODEL.md](MATURITY_MODEL.md).

---

<div align="center"><sub><a href="README.md">Documentación</a> · <a href="MATURITY_MODEL.md">Madurez</a> · <a href="SECURITY_MODEL.md">Seguridad</a></sub></div>
