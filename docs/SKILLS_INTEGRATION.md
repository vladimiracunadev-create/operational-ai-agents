# Integración con claude-skills-toolkit

Los agentes son autónomos. Los skills agregan detectores y ejecutores especializados:

```text
objetivo → agente → decisión → skill/tool → verificación → resultado
```

Instala primero el toolkit y luego exporta:

```bash
operational-agents doctor --skills-dir ~/.claude/skills
operational-agents export claude --preload-skills --target ~/.claude/agents
```

El campo `skill_dependencies` es una recomendación versionable, no una afirmación de que el skill está instalado. El doctor reporta faltantes sin bloquear la variante autónoma.
