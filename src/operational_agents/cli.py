
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from .catalog import agents_by_id, find_root, load_catalog
from .evaluation import evaluate_agent
from .exporter import export_claude, uninstall_claude
from .planner import create_plan, packet, plan_markdown
from .render import render_instructions
from .server import serve
from .syncer import sync
from .validator import validate


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="operational-agents", description="Catálogo y adaptadores para agentes operativos")
    p.add_argument("--root", type=Path, help="Raíz del repositorio")
    sub = p.add_subparsers(dest="command", required=True)
    list_p = sub.add_parser("list", help="Lista agentes")
    list_p.add_argument("--json", action="store_true")
    inspect = sub.add_parser("inspect", help="Muestra un contrato")
    inspect.add_argument("agent_id")
    inspect.add_argument("--json", action="store_true")
    val = sub.add_parser("validate", help="Valida el repositorio")
    val.add_argument("--json", action="store_true")
    plan = sub.add_parser("plan", help="Genera un plan determinista")
    plan.add_argument("agent_id")
    plan.add_argument("--task", required=True)
    plan.add_argument("--target")
    plan.add_argument("--format", choices=("markdown", "json"), default="markdown")
    pack = sub.add_parser("packet", help="Genera un paquete de prompt portable")
    pack.add_argument("agent_id")
    pack.add_argument("--task", required=True)
    pack.add_argument("--target")
    exp = sub.add_parser("export", help="Exporta adaptadores")
    exp.add_argument("runtime", choices=("claude",))
    exp.add_argument("--target", type=Path, required=True)
    exp.add_argument("--preload-skills", action="store_true")
    un = sub.add_parser("uninstall", help="Elimina solo agentes administrados")
    un.add_argument("runtime", choices=("claude",))
    un.add_argument("--target", type=Path, required=True)
    ev = sub.add_parser("eval", help="Ejecuta evals deterministas")
    ev.add_argument("agent_id", nargs="?")
    ev.add_argument("--all", action="store_true")
    ev.add_argument("--json", action="store_true")
    sy = sub.add_parser("sync", help="Sincroniza vistas generadas")
    sy.add_argument("--check", action="store_true")
    doc = sub.add_parser("doctor", help="Diagnostica entorno e integración de skills")
    doc.add_argument("--skills-dir", type=Path)
    run = sub.add_parser("run", help="Ejecuta mediante un runtime externo")
    run.add_argument("agent_id")
    run.add_argument("--runtime", choices=("claude",), required=True)
    run.add_argument("--task", required=True)
    run.add_argument("--cwd", type=Path, default=Path.cwd())
    srv = sub.add_parser("serve", help="Inicia panel local")
    srv.add_argument("--host", default="127.0.0.1")
    srv.add_argument("--port", type=int, default=8765)
    sc = sub.add_parser("scaffold", help="Crea un borrador no catalogado")
    sc.add_argument("agent_id")
    sc.add_argument("--name", required=True)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = (args.root.resolve() if args.root else find_root())
    catalog = load_catalog(root)
    agents = agents_by_id(catalog)
    try:
        if args.command == "list":
            data = [{k: a[k] for k in ("id", "name", "status", "category", "risk")} for a in catalog["agents"]]
            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                for a in data:
                    print(f"{a['id']:<38} {a['status']:<12} {a['risk']:<6} {a['name']}")
            return 0
        if args.command == "inspect":
            agent = agents[args.agent_id]
            print(json.dumps(agent, indent=2, ensure_ascii=False) if args.json else _inspect_text(agent))
            return 0
        if args.command == "validate":
            issues = validate(root)
            if args.json:
                print(json.dumps(issues, indent=2, ensure_ascii=False))
            else:
                for item in issues:
                    print(f"{item['level'].upper():<7} {item['agent_id']}: {item['message']}")
                if not issues:
                    print(f"OK: {len(catalog['agents'])} agentes válidos")
            return 1 if any(i["level"] == "error" for i in issues) else 0
        if args.command == "plan":
            result = create_plan(agents[args.agent_id], args.task, args.target)
            print(json.dumps(result, indent=2, ensure_ascii=False) if args.format == "json" else plan_markdown(result))
            return 0
        if args.command == "packet":
            agent = agents[args.agent_id]
            print(packet(agent, render_instructions(agent), args.task, args.target))
            return 0
        if args.command == "export":
            paths = export_claude(catalog["agents"], args.target, args.preload_skills)
            print(f"Exportados {len(paths)} agentes en {args.target.expanduser().resolve()}")
            return 0
        if args.command == "uninstall":
            paths = uninstall_claude(catalog["agents"], args.target)
            print(f"Eliminados {len(paths)} agentes administrados")
            return 0
        if args.command == "eval":
            selected = catalog["agents"] if args.all else [agents[args.agent_id]] if args.agent_id else []
            if not selected:
                raise ValueError("Indique agent_id o --all")
            results = [{"agent_id": a["id"], "cases": evaluate_agent(root, a)} for a in selected]
            passed = sum(case["passed"] for item in results for case in item["cases"])
            total = sum(len(item["cases"]) for item in results)
            if args.json:
                print(json.dumps(results, indent=2, ensure_ascii=False))
            else:
                for item in results:
                    ok = sum(c["passed"] for c in item["cases"])
                    print(f"{item['agent_id']}: {ok}/{len(item['cases'])}")
                print(f"TOTAL: {passed}/{total}")
            return 0 if passed == total else 1
        if args.command == "sync":
            changed = sync(root, check=args.check)
            if changed:
                print(("Drift: " if args.check else "Sincronizados: ") + ", ".join(changed))
            else:
                print("OK: no hay drift")
            return 1 if args.check and changed else 0
        if args.command == "doctor":
            return _doctor(catalog["agents"], args.skills_dir)
        if args.command == "run":
            return _run_claude(agents[args.agent_id], args.task, args.cwd)
        if args.command == "serve":
            serve(root, args.host, args.port)
            return 0
        if args.command == "scaffold":
            return _scaffold(root, args.agent_id, args.name)
    except KeyError as exc:
        print(f"ERROR: agente desconocido: {exc.args[0]}", file=sys.stderr)
        return 2
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


def _inspect_text(agent: dict) -> str:
    return "\n".join([
        f"{agent['name']} ({agent['id']})",
        f"Estado: {agent['status']} | Riesgo: {agent['risk']} | Categoría: {agent['category']}",
        f"Misión: {agent['mission']}",
        "Fases: " + " -> ".join(agent["phases"]),
        "Tools: " + ", ".join(agent["tools"]),
        "Skills opcionales: " + ", ".join(agent["skill_dependencies"]),
        "Gates: " + ", ".join(agent["approval_points"]),
    ])


def _doctor(agents: list[dict], skills_dir: Path | None) -> int:
    print(f"Python: {sys.version.split()[0]} ({'OK' if sys.version_info >= (3, 11) else 'requiere 3.11+'})")
    print(f"Claude CLI: {shutil.which('claude') or 'no encontrado (opcional)'}")
    if skills_dir:
        base = skills_dir.expanduser().resolve()
        required = sorted({s for a in agents for s in a["skill_dependencies"]})
        missing = [s for s in required if not (base / s).exists()]
        print(f"Skills: {len(required) - len(missing)}/{len(required)} disponibles en {base}")
        if missing:
            print("Faltantes: " + ", ".join(missing))
    return 0 if sys.version_info >= (3, 11) else 1


def _run_claude(agent: dict, task: str, cwd: Path) -> int:
    executable = shutil.which("claude")
    if not executable:
        raise FileNotFoundError("No se encontró Claude Code; use export o instálelo antes de run")
    workdir = cwd.expanduser().resolve()
    if not workdir.is_dir():
        raise ValueError(f"Directorio inexistente: {workdir}")
    command = [executable, "--agent", agent["id"], "--print", task]
    completed = subprocess.run(command, cwd=workdir, check=False)
    return completed.returncode


def _scaffold(root: Path, agent_id: str, name: str) -> int:
    from .render import valid_agent_id
    if not valid_agent_id(agent_id):
        raise ValueError("agent_id debe estar en kebab-case")
    path = root / "agents" / f"_{agent_id}-draft"
    if path.exists():
        raise ValueError(f"Ya existe {path}")
    path.mkdir(parents=True)
    (path / "README.md").write_text(
        f"# {name}\n\nBorrador no instalable. Agréguelo al catálogo y ejecute sync.\n",
        encoding="utf-8",
    )
    print(f"Creado borrador: {path.relative_to(root)}")
    return 0
