# Adaptador de Claude Code

> Proyecta el contrato canónico a archivos compatibles con `.claude/agents/`.

[Repositorio](../../README.md) · [Guía completa](../../docs/CLAUDE_CODE.md)

---

```bash
operational-agents export claude --target ~/.claude/agents
operational-agents export claude --preload-skills --target ~/.claude/agents
```

Las definiciones generadas declaran `model: inherit`, límite de turnos, memoria explícita, tool allowlist, modo de permisos y aislamiento en worktree para los agentes que escriben.

Por defecto se usa la variante **autónoma**, que no menciona ningún skill. Con `--preload-skills` se añaden las dependencias opcionales del toolkit.

> [!IMPORTANT]
> El exportador nunca sobrescribe un archivo que no lleve la marca `managed-by: operational-ai-agents`. Si existe un agente tuyo con el mismo nombre, la operación falla y tu archivo queda intacto.

El detalle campo por campo está en [`docs/CLAUDE_CODE.md`](../../docs/CLAUDE_CODE.md).

---

<div align="center"><sub><a href="../../README.md">Repositorio</a> · <a href="../../docs/CLAUDE_CODE.md">Claude Code</a></sub></div>
