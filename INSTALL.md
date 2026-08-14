# Instalación

> Instalar, actualizar y desinstalar. Nada de esto necesita clave API: validar contratos, generar planes, evaluar y usar el panel funcionan offline.

[Repositorio](README.md) · [Referencia de CLI](docs/CLI.md) · [Claude Code](docs/CLAUDE_CODE.md)

---

## Requisitos

| Requisito | Para qué | ¿Obligatorio? |
|---|---|:-:|
| Python 3.11+ | CLI, validación, planner, evaluaciones y panel | ✅ |
| Git | actualizar por repositorio | ✅ |
| Claude Code | ejecutar los agentes de verdad | ❌ solo para ejecución real |
| Docker | levantar el panel en contenedor | ❌ opcional |

No hay dependencias de runtime: la CLI usa únicamente la biblioteca estándar.

## 1 · CLI local

```bash
git clone https://github.com/vladimiracunadev-create/operational-ai-agents.git
cd operational-ai-agents
python -m pip install -e .
operational-agents validate
operational-agents list
```

Si `operational-agents` no aparece en el PATH, el equivalente siempre funciona:

```bash
python -m operational_agents list
```

## 2 · Instalar los agentes en Claude Code

### Alcance usuario — disponibles en todos tus proyectos

```bash
./scripts/install.sh        # Linux, macOS, Git Bash
```

```powershell
.\scripts\install.ps1       # Windows PowerShell
```

El instalador crea enlaces en `~/.claude/agents/`; en Windows copia los archivos si el enlace simbólico no está permitido. Es idempotente y no elimina agentes ajenos.

### Alcance proyecto — solo en un repositorio

```bash
operational-agents export claude --target /ruta/proyecto/.claude/agents
```

> [!IMPORTANT]
> El exportador **nunca sobrescribe un archivo que no administra**. Si ya tienes un agente con el mismo nombre sin la marca `managed-by: operational-ai-agents`, la operación falla y tu archivo queda intacto.

### Con skills precargados

```bash
operational-agents doctor --skills-dir ~/.claude/skills      # ¿cuáles faltan?
operational-agents export claude --preload-skills --target ~/.claude/agents
```

Los agentes **no** necesitan esos skills: son una mejora opcional. Detalle en [docs/SKILLS_INTEGRATION.md](docs/SKILLS_INTEGRATION.md).

## 3 · Comprobar que funciona

```bash
operational-agents doctor
claude --agent repository-evolution-agent
```

O menciónalo dentro de una sesión ya abierta:

```text
> @repository-evolution-agent comprueba si README y código coinciden.
```

## 4 · Panel local (opcional)

```bash
operational-agents serve --host 127.0.0.1 --port 8765
```

O en contenedor:

```bash
docker compose up --build
```

> [!CAUTION]
> El panel **no implementa autenticación**. Escucha en loopback por defecto y salir de ahí exige declarar `OPERATIONAL_AGENTS_ALLOW_REMOTE_BIND=1`. No lo expongas a Internet.

## Actualizar

```bash
git pull
python -m pip install -e .
operational-agents sync
./scripts/install.sh
```

`sync` regenera las vistas derivadas del catálogo; `install` refresca las definiciones instaladas.

## Desinstalar

```bash
./scripts/uninstall.sh
```

```powershell
.\scripts\uninstall.ps1
```

Solo se eliminan los nombres administrados por este repositorio. El código clonado y cualquier agente tuyo permanecen intactos.

## Problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `operational-agents: command not found` | el directorio de scripts no está en el PATH | usa `python -m operational_agents` o añade el directorio al PATH |
| `No se encontró Claude Code` al usar `run` | el binario `claude` no está instalado | instálalo, o usa `export` y trabaja desde el propio Claude Code |
| `Se preservó un agente no administrado` | ya existe un agente tuyo con ese nombre | renómbralo o elige otro `--target` |
| `Por seguridad use loopback…` | intentaste enlazar el panel fuera de loopback | declara la variable de opt-in solo si sabes lo que haces |
| Acentos rotos en la salida de Windows | consola en cp1252 | define `PYTHONUTF8=1` |

Más diagnóstico en [SUPPORT.md](SUPPORT.md).

---

<div align="center"><sub><a href="README.md">Repositorio</a> · <a href="docs/CLI.md">CLI</a> · <a href="SUPPORT.md">Soporte</a></sub></div>
