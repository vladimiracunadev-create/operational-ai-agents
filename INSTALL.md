# Instalación

## Requisitos

- Python 3.11 o superior.
- Git para actualización por repositorio.
- Claude Code solo para ejecución real de los agentes.

## CLI local

```bash
python -m pip install -e .
operational-agents validate
operational-agents list
```

No se requiere API para validar, inspeccionar, evaluar contratos, generar planes o usar el panel.

## Claude Code — usuario

Linux, macOS o Git Bash:

```bash
./scripts/install.sh
```

Windows PowerShell:

```powershell
.\scripts\install.ps1
```

El instalador crea enlaces en `~/.claude/agents/`; en Windows usa copia si el enlace no está permitido. Es idempotente y no elimina agentes ajenos.

## Claude Code — proyecto

```bash
operational-agents export claude --target /ruta/proyecto/.claude/agents
```

Para integrar skills ya instalados desde `claude-skills-toolkit`:

```bash
operational-agents export claude --preload-skills --target ~/.claude/agents
```

Antes de precargar, ejecuta `operational-agents doctor --skills-dir ~/.claude/skills` para detectar faltantes. Los agentes autónomos no requieren esos skills.

## Probar

```bash
claude --agent repository-evolution-agent
```

También puedes mencionarlo en una sesión: `@repository-evolution-agent`.

## Actualizar

```bash
git pull
operational-agents sync
./scripts/install.sh
```

## Desinstalar

```bash
./scripts/uninstall.sh
# Windows:
.\scripts\uninstall.ps1
```

Solo se eliminan los diez nombres administrados por este repositorio. El código clonado y otros agentes permanecen intactos.
