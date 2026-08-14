# Modelos locales

> Planificado para v0.3. No se presentará equivalencia sin evaluaciones por runtime.

[Repositorio](../../README.md) · [Roadmap](../../ROADMAP.md)

---

El núcleo no asume que un modelo local soporte tool calling, schemas estructurados ni contexto suficiente para sostener una misión completa. Un adaptador local deberá declarar:

- qué capacidades del contrato soporta y cuáles no;
- cómo **degrada** cuando falta una — fallar es preferible a fingir;
- qué evaluaciones pasa en ese runtime concreto.

Hasta entonces, afirmar que estos agentes «funcionan con cualquier modelo» sería una afirmación sin evidencia.

---

<div align="center"><sub><a href="../../README.md">Repositorio</a> · <a href="../../ROADMAP.md">Roadmap</a></sub></div>
