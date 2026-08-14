# Claude Code

> Cómo se proyecta el contrato canónico al primer runtime adaptado, qué significa cada campo del frontmatter y cómo se instala sin pisar tus propios agentes.

[← Documentación](README.md) · [Repositorio](../README.md) · [Instalación](../INSTALL.md)

---

## Por qué Claude Code es el primer adaptador

Porque soporta de forma nativa lo que el contrato necesita: subagentes con **contexto separado**, allowlist de tools, modo de permisos, límite de turnos, memoria, skills e **aislamiento en worktree**. Un runtime que no ofrezca gates ni permisos obligaría a degradar el contrato, y el proyecto prefiere no adaptarse antes que fingir equivalencia.

El núcleo sigue siendo vendor-neutral: el catálogo, las políticas, los schemas y las evaluaciones no dependen de ningún proveedor.

## Cómo se instala

```bash
operational-agents export claude --target ~/.claude/agents     # alcance usuario
operational-agents export claude --target ./.claude/agents     # alcance proyecto
```

> [!IMPORTANT]
> El exportador **nunca sobrescribe un archivo que no administra**. Si en el destino existe un agente con el mismo nombre sin la marca `managed-by: operational-ai-agents`, la operación falla y conserva tu archivo intacto. Lo mismo vale al desinstalar: solo se eliminan los nombres administrados.

## El frontmatter generado

```yaml
---
name: portfolio-publication-agent
description: "Úsalo cuando lo publicado sobre un conjunto de repositorios…"
tools: Read, Glob, Grep, Bash, Edit, Write, Skill, WebSearch, WebFetch
model: inherit
permissionMode: default
maxTurns: 32
memory: project
effort: high
isolation: worktree
color: orange
---
```

| Campo | De dónde sale | Por qué importa |
|---|---|---|
| `name` | `id` | es el nombre con el que lo invocas: `@portfolio-publication-agent` |
| `description` | `delegate_when` | es lo que lee el runtime para decidir si delegar en él |
| `tools` | `tools` | allowlist mínima; lo no listado no está disponible |
| `disallowedTools` | `disallowed_tools` | denegación explícita, no por omisión |
| `model` | fijo `inherit` | el agente no impone modelo: hereda el de tu sesión |
| `permissionMode` | `permission_mode` | `default` mantiene la confirmación del runtime; `plan` impide mutar |
| `maxTurns` | `max_turns` | techo de pasos por misión |
| `memory` | `memory` | alcance de memoria entre sesiones |
| `isolation` | `isolation` | `worktree` en todo agente que escribe |

## Cómo se invoca

```text
> Usa repository-evolution-agent para examinar este repositorio.

> @curriculum-evolution-agent revisa si el temario quedó desactualizado.
```

O abriendo la sesión completa con el agente:

```bash
claude --agent repository-evolution-agent
```

También desde la CLI de este repositorio, que delega en el binario de Claude Code:

```bash
operational-agents run repository-evolution-agent \
  --runtime claude --cwd /ruta/al/repositorio \
  --task "Detecta brechas y prepara un plan; no publiques cambios"
```

> [!WARNING]
> `run` construye la invocación como lista de argumentos, sin `shell=True`, y **no añade ninguna bandera que omita permisos**. Las confirmaciones que pida el runtime siguen apareciendo.

## Skills opcionales

Los agentes funcionan solos. Con `--preload-skills`, el frontmatter declara además los skills de [`claude-skills-toolkit`](https://github.com/vladimiracunadev-create/claude-skills-toolkit) que el agente puede aprovechar si están instalados:

```bash
operational-agents doctor --skills-dir ~/.claude/skills   # ¿cuáles faltan?
operational-agents export claude --preload-skills --target ~/.claude/agents
```

Detalle en [SKILLS_INTEGRATION.md](SKILLS_INTEGRATION.md).

## Qué no hace este adaptador

- No implementa su propio bucle de LLM: el razonamiento corre en el runtime.
- No modifica tu configuración de Claude Code más allá de los archivos de agente.
- No relaja permisos ni introduce credenciales.

---

<div align="center"><sub><a href="README.md">Documentación</a> · <a href="../INSTALL.md">Instalación</a> · <a href="SKILLS_INTEGRATION.md">Skills</a></sub></div>
