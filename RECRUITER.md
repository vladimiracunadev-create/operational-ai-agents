# Lectura profesional del proyecto

> Qué demuestra este repositorio sobre ingeniería de agentes, y qué deliberadamente no afirma.

[Repositorio](README.md) · [Arquitectura](docs/ARCHITECTURE.md) · [Sitio del proyecto](https://vladimiracunadev-create.github.io/operational-ai-agents/)

---

## Qué demuestra

| Competencia | Dónde se ve |
|---|---|
| Distinguir agente, skill, workflow y caso de negocio | [`docs/AGENT_CONTRACT.md`](docs/AGENT_CONTRACT.md) y la tabla comparativa del README |
| Diseño por contrato con una sola fuente de verdad | `catalog/agents.yaml` y las cinco vistas que se generan de él |
| Modelado de permisos y autorización | tool allowlists, `permission_mode`, `isolation` y gates humanos |
| Human-in-the-loop real | `approval_points` en los doce agentes, con pruebas que verifican que existen |
| Evaluación automatizada de contratos | 36 evaluaciones deterministas que fallan si alguien retira un gate |
| Honestidad de estado | un modelo de madurez de cinco niveles que hoy sitúa todo en `IMPLEMENTED` |
| Ingeniería de entrega | CI multiplataforma, CodeQL, build de wheel, imagen Docker verificada en vivo y Pages |
| Prevención de drift documental | pruebas que verifican enlaces, anclas, conteos y coherencia de versión |

## La decisión de diseño que lo resume

Cuatro archivos por agente y la landing page **se generan** desde el catálogo. Editarlos a mano hace fallar la build.

Eso convierte una promesa habitual —«la documentación está actualizada»— en una propiedad que el sistema garantiza. La documentación no puede contradecir al contrato porque no es una copia: es una proyección.

## Lo que este proyecto NO afirma

Esto es parte del trabajo, no una carencia que ocultar:

- **No afirma uso productivo.** Los doce agentes declaran `IMPLEMENTED`: contrato completo y validado. Ninguno ha registrado todavía una misión real con evidencia.
- **No afirma métricas de adopción**, costo ni retrabajo, porque no existen aún.
- **No afirma equivalencia entre runtimes.** Está adaptado a uno, y la portabilidad del núcleo es un diseño, no una demostración.

El mecanismo para incorporar evidencia real sin exagerar está construido: [`docs/EVIDENCE_GUIDE.md`](docs/EVIDENCE_GUIDE.md) y [`docs/MATURITY_MODEL.md`](docs/MATURITY_MODEL.md).

## Por dónde mirar en cinco minutos

1. **[`catalog/agents.yaml`](catalog/agents.yaml)** — el contrato canónico de los doce agentes.
2. **La ficha de un agente**, por ejemplo [`security-remediation-agent`](agents/security-remediation-agent/README.md) — misión, fase por fase, permisos y gates.
3. **[`docs/SECURITY_MODEL.md`](docs/SECURITY_MODEL.md)** — la tabla de garantías, cada una con el nombre de la prueba que la respalda.
4. **[`tests/test_repository.py`](tests/test_repository.py)** — las pruebas que convierten esas garantías en propiedades verificadas.

```bash
git clone https://github.com/vladimiracunadev-create/operational-ai-agents.git
cd operational-ai-agents && python -m pip install -e .
operational-agents list && operational-agents validate
```

Todo corre offline, sin clave API y sin costo.

---

<div align="center"><sub><a href="README.md">Repositorio</a> · <a href="docs/README.md">Documentación</a> · <a href="ROADMAP.md">Roadmap</a></sub></div>
