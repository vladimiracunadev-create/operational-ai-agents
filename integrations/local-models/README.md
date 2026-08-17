# Modelos locales

> No hay adaptador local todavía. Lo que sí hay desde v0.3.0 es el contrato que tendría que cumplir.

[Repositorio](../../README.md) · [Contrato de runtime](../../docs/RUNTIME_CONTRACT.md) · [Roadmap](../../ROADMAP.md)

---

El núcleo no asume que un modelo local soporte tool calling, schemas estructurados ni contexto suficiente para sostener una misión completa. Un adaptador para Ollama, llama.cpp, LM Studio, vLLM o MLX debe implementar `AgentRuntime` y declarar:

- **qué capacidades ofrece y con qué nivel** — `full` si son nativas, `conditional` si dependen del modelo concreto;
- **cómo degrada** cuando falta una: la resolución devuelve `UNSUPPORTED` y la CLI se niega a ejecutar, en lugar de fingir el resultado;
- **qué evaluaciones pasa en ese runtime concreto**, porque «funciona en Claude» no implica «funciona en todos».

La plantilla está en [`docs/RUNTIME_CONTRACT.md`](../../docs/RUNTIME_CONTRACT.md), y el efecto de declarar una capacidad se ve de inmediato en la [matriz de compatibilidad](../../docs/COMPATIBILITY_MATRIX.md), que se regenera con `operational-agents sync`.

Mientras no exista ese adaptador con sus pruebas, afirmar que estos agentes «funcionan con cualquier modelo» sería una afirmación sin evidencia. La [matriz](../../docs/COMPATIBILITY_MATRIX.md) solo lista lo que el repositorio implementa.

---

<div align="center"><sub><a href="../../README.md">Repositorio</a> · <a href="../../docs/RUNTIME_CONTRACT.md">Runtimes</a> · <a href="../../ROADMAP.md">Roadmap</a></sub></div>
