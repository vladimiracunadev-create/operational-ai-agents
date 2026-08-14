# Integración con skills

> Los agentes funcionan solos. Los skills son una mejora opcional, nunca un requisito — y esa distinción es deliberada.

[← Documentación](README.md) · [Repositorio](../README.md)

---

## La regla

> Un agente que deja de funcionar porque falta un skill no es autónomo: es un script con dependencias.

Por eso `skill_dependencies` declara capacidades **opcionales**. Si el skill está instalado, el agente lo aprovecha; si no, hace el mismo trabajo con sus tools y lo dice en el reporte.

## Skill y agente no son lo mismo

| | Skill | Agente |
|---|---|---|
| Contexto | el de la sesión actual | separado y propio |
| Alcance | una capacidad concreta | una misión completa |
| Decide | quien lo invoca | el agente, dentro de límites |
| Permisos | heredados | allowlist declarada por contrato |
| Responde por | devolver un resultado | evidencia y riesgos residuales |

Un agente **selecciona** capacidades; un skill **es** una capacidad.

## Cómo se activan

```bash
# 1. ¿Qué skills esperan los agentes y cuáles faltan?
operational-agents doctor --skills-dir ~/.claude/skills

# 2. Generar las definiciones que los declaran
operational-agents export claude --preload-skills --target ~/.claude/agents
```

Sin `--preload-skills`, las definiciones son autónomas y no mencionan ningún skill.

`doctor` compara los skills que declara el catálogo con los presentes en el directorio y lista los ausentes. Informa; no instala nada ni falla por su ausencia.

## Qué skills declara cada agente

La lista canónica vive en `catalog/agents.yaml` y aparece en la ficha de cada agente. Provienen de [`claude-skills-toolkit`](https://github.com/vladimiracunadev-create/claude-skills-toolkit), instalable por separado.

```bash
operational-agents inspect <agent-id>   # incluye "Skills opcionales"
```

## Compatibilidad

`integrations/claude-skills-toolkit/compatibility.yaml` declara qué versiones del toolkit se han contrastado. Si usas una versión distinta, los agentes siguen funcionando: lo que puede cambiar es qué skill se precarga, no el contrato.

## Qué no hace esta integración

- No instala skills automáticamente.
- No convierte un skill en un agente ni al revés.
- No permite que un skill relaje los permisos o los gates del agente que lo usa.

---

<div align="center"><sub><a href="README.md">Documentación</a> · <a href="CLAUDE_CODE.md">Claude Code</a> · <a href="AGENT_CONTRACT.md">Contrato</a></sub></div>
