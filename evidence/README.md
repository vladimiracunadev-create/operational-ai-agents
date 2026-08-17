# Evidencia

> Esta carpeta empieza vacía a propósito. Sin casos reales revisados, ningún agente sube de estado.

[Repositorio](../README.md) · [Guía de evidencia](../docs/EVIDENCE_GUIDE.md) · [Modelo de madurez](../docs/MATURITY_MODEL.md)

---

## Estructura

| Ruta | Contenido | ¿Se versiona? |
|---|---|:-:|
| `executions/` | artefactos locales de ejecuciones | ❌ ignorado por git |
| `evaluations/` | resultados de evaluaciones conservados | ✅ si están sanitizados |
| `case-studies/` | casos revisados que respaldan una promoción de madurez | ✅ tras revisión humana |
| `templates/` | plantilla de caso de uso | ✅ |

## Estado actual

Ningún caso registrado. Los trece agentes declaran `IMPLEMENTED`, que significa **contrato completo y validado**, no adopción productiva.

Pasar las pruebas mantiene ese estado; no lo sube.

## Antes de añadir un caso

> [!CAUTION]
> Nunca guardes tokens, credenciales, cookies, datos personales, prompts privados de terceros, URLs firmadas ni rutas locales que identifiquen a una persona. Léelo entero antes de moverlo a `case-studies/`: la redacción automática es una primera barrera, no una revisión.

Usa [`templates/case-study.md`](templates/case-study.md) y sigue los criterios de [`docs/EVIDENCE_GUIDE.md`](../docs/EVIDENCE_GUIDE.md).

---

<div align="center"><sub><a href="../README.md">Repositorio</a> · <a href="../docs/EVIDENCE_GUIDE.md">Guía de evidencia</a></sub></div>
