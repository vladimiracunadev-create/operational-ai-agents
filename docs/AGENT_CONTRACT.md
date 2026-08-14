# Contrato de agente

Cada agente declara:

| Campo | Responsabilidad |
|---|---|
| `id`, `name`, `version` | identidad estable |
| `delegate_when` | criterio para seleccionar el agente |
| `mission` | resultado integral del que responde |
| `tools`, `disallowed_tools` | capacidad técnica mínima |
| `skill_dependencies` | capacidades opcionales precargables |
| `permission_mode`, `isolation` | frontera operativa |
| `phases` | ciclo de decisión observable |
| `required_inputs`, `deliverables` | contrato entrada/salida |
| `approval_points` | decisiones reservadas al usuario |
| `checks`, `non_goals` | calidad y límites |
| `status` | madurez respaldada por evidencia |

## Invariantes

1. Nunca convertir acceso en autorización.
2. Nunca declarar evidencia inexistente.
3. Nunca autopublicar ni autopromover madurez.
4. Distinguir observado, inferido y recomendado.
5. Mantener una salida útil incluso cuando el estado sea `BLOCKED`.
6. No modificar antes de comprender alcance, fuentes de verdad y rollback.

Los schemas comunes están en `shared/contracts`; cada agente mantiene una copia versionada para portabilidad.
