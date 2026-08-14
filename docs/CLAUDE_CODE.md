# Claude Code

Claude Code carga subagentes desde `~/.claude/agents/` o `.claude/agents/`. Cada Markdown contiene frontmatter y un system prompt independiente.

Este proyecto exporta `name`, `description`, tools, restricciones, modelo heredado, permisos, `maxTurns`, memoria, esfuerzo, aislamiento y color. La variante `--preload-skills` agrega la lista de skills al contexto inicial.

```bash
operational-agents export claude --target .claude/agents
claude --agent product-evolution-agent
```

Referencia oficial: <https://code.claude.com/docs/en/sub-agents>

## Diseño seguro

- `model: inherit` evita acoplarse a un ID que se vuelve obsoleto.
- Agentes mutantes usan `permissionMode: default` e `isolation: worktree`.
- Agentes de diagnóstico usan `permissionMode: plan` y niegan Edit/Write.
- `maxTurns` limita bucles sin control.
- El coordinador permite solo especialistas nombrados.

Plugin agents ignora algunos campos sensibles; por eso el instalador usa alcance user/project y no empaqueta por defecto como plugin.
