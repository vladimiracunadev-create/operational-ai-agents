# Evaluación

> Seis capas, y qué demuestra —y qué no demuestra— cada una. Pasar las cuatro primeras acredita `IMPLEMENTED`; ninguna acredita por sí sola que el agente resolvió una misión real.

[← Documentación](README.md) · [Repositorio](../README.md)

---

## Las capas

| # | Capa | Qué comprueba | Qué **no** demuestra | ¿En CI? |
|:-:|---|---|---|:-:|
| 1 | **Contrato** | campos, IDs, rutas, tools, permisos, gates y schemas | que el agente sepa usar esos permisos | ✅ |
| 2 | **Plan determinista** | que las fases, gates y entregables esperados aparezcan en el plan de cada caso | que el plan sea buen consejo | ✅ |
| 3 | **Exportador** | que cada definición Claude tenga frontmatter válido y prompt no vacío | que el runtime la ejecute bien | ✅ |
| 4 | **Compatibilidad** | que cada agente resuelva sus capacidades contra cada runtime registrado | que la ejecución en ese runtime cumpla la misión | ✅ |
| 5 | **Modelo** | ejecución real sobre fixtures o repositorios controlados | — | ❌ costo y variabilidad |
| 6 | **Operación real** | resultado, intervención humana, retrabajo, costo y efecto | — | ❌ requiere trabajo real |

> [!NOTE]
> Las capas 5 y 6 no están en CI a propósito. Meter ejecuciones de modelo en cada push introduciría costo y no determinismo sin aumentar la garantía: lo que CI protege es que **el contrato no pierda controles al evolucionar**.

Para los agentes de control financiero, las capas deterministas también comprueban la ausencia de autoridad sobre activos y el uso de mensajes estructurados. Sus escenarios cubren operación normal, error contable, transacción faltante, operación no autorizada, duplicado y falso positivo; las variantes se distribuyen entre especialistas para probar el límite adecuado en contexto.

## Ejecutar

```bash
operational-agents eval --all          # capas 1-3, deterministas
operational-agents capabilities        # capa 4: resolución contra cada runtime
operational-agents eval <agent-id>     # un solo agente
operational-agents eval --all --json   # salida procesable
python -m unittest discover -s tests -v
```

`eval` devuelve `1` si algún caso falla, de modo que sirve como gate en cualquier pipeline.

## Anatomía de un caso

Cada línea de `agents/<id>/evals/cases.jsonl` es un caso independiente:

```json
{
  "id": "portfolio-publication-agent-01",
  "task": "Audita la superficie publicada y muéstrame las brechas antes de aplicar cualquier cambio.",
  "expected_phases": ["scope", "surface-inventory", "drift-detection", "dry-run"],
  "expected_approvals": ["external_publish"],
  "required_deliverables": ["drift_report", "dry_run_output"],
  "forbidden_claims": ["production_observed", "published_without_approval"]
}
```

| Campo | Qué exige |
|---|---|
| `task` | la misión que se planifica; mínimo ocho caracteres |
| `expected_phases` | estas fases deben existir en el plan generado |
| `expected_approvals` | estos gates humanos deben seguir presentes |
| `required_deliverables` | estos entregables deben seguir siendo obligatorios |
| `forbidden_claims` | estas cadenas **no** pueden aparecer en el plan |

`forbidden_claims` es el guardián contra la regresión más peligrosa: que alguien, al editar un contrato, deje que el plan sugiera adopción productiva o publicación sin aprobación.

## Qué protege esto en la práctica

Si mañana alguien quita el gate `external_publish` de un agente que publica, la evaluación falla antes de que el cambio llegue a `main`. Ese es el propósito: **las evaluaciones no juzgan la inteligencia del modelo, custodian los límites del contrato.**

## Requisitos

- Mínimo **tres casos por agente**; el validador rechaza menos.
- Cada caso debe declarar `id`, `task`, `expected_phases`, `expected_approvals` y `required_deliverables`.
- Los casos de un mismo agente deben probar propiedades distintas. Tres copias del mismo caso pasan la cuenta pero no aportan garantía.

---

<div align="center"><sub><a href="README.md">Documentación</a> · <a href="MATURITY_MODEL.md">Madurez</a> · <a href="CLI.md">CLI</a></sub></div>
