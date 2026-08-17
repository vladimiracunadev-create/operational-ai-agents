
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from .capabilities import CAPABILITIES, approval_required_capabilities, effect_summary, optional_capabilities, required_capabilities
from .catalog import agents_by_id, find_root, load_catalog
from .compatibility import resolutions
from .evaluation import evaluate_agent
from .evidence import execution_envelope
from .exporter import export_claude, uninstall_claude
from .planner import create_plan, packet, plan_markdown
from .render import render_instructions
from .runtimes import AgentRuntime, default_registry
from .runtimes.registry import RuntimeRegistry
from .server import serve
from .syncer import sync
from .validator import validate


def parser(registry: RuntimeRegistry | None = None) -> argparse.ArgumentParser:
    # Los runtimes disponibles salen del registro: añadir un adaptador no
    # obliga a tocar la CLI, y `--runtime claude` sigue siendo válido siempre.
    runtime_ids = (registry or default_registry()).ids()
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
    doc = sub.add_parser("doctor", help="Diagnostica entorno, runtimes e integraciones")
    doc.add_argument("--skills-dir", type=Path)
    doc.add_argument("--json", action="store_true")
    rts = sub.add_parser("runtimes", help="Lista los runtimes registrados y su disponibilidad")
    rts.add_argument("--json", action="store_true")
    rt = sub.add_parser("runtime", help="Inspecciona un runtime concreto")
    rt_sub = rt.add_subparsers(dest="runtime_command", required=True)
    rt_inspect = rt_sub.add_parser("inspect", help="Capacidades declaradas y disponibilidad de un runtime")
    rt_inspect.add_argument("runtime_id", choices=runtime_ids)
    rt_inspect.add_argument("--json", action="store_true")
    caps = sub.add_parser("capabilities", help="Resuelve capacidades de agente contra runtime")
    caps.add_argument("agent_id", nargs="?", help="Sin agente muestra la matriz completa")
    caps.add_argument("--runtime", choices=runtime_ids)
    caps.add_argument("--json", action="store_true")
    run = sub.add_parser("run", help="Ejecuta mediante un runtime externo")
    run.add_argument("agent_id")
    run.add_argument("--runtime", choices=runtime_ids, required=True)
    run.add_argument("--task", required=True)
    run.add_argument("--target")
    run.add_argument("--cwd", type=Path, default=Path.cwd())
    run.add_argument("--evidence", type=Path, help="Escribe el sobre de evidencia portable en esta ruta")
    run.add_argument("--dry-run", action="store_true", help="Prepara y resuelve capacidades sin ejecutar")
    srv = sub.add_parser("serve", help="Inicia panel local")
    srv.add_argument("--host", default="127.0.0.1")
    srv.add_argument("--port", type=int, default=8765)
    sc = sub.add_parser("scaffold", help="Crea un borrador no catalogado")
    sc.add_argument("agent_id")
    sc.add_argument("--name", required=True)
    return p


def main(argv: list[str] | None = None) -> int:
    registry = default_registry()
    args = parser(registry).parse_args(argv)
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
            return _doctor(catalog["agents"], args.skills_dir, registry, args.json)
        if args.command == "runtimes":
            return _runtimes(registry, args.json)
        if args.command == "runtime":
            return _runtime_inspect(registry, args.runtime_id, args.json)
        if args.command == "capabilities":
            if args.agent_id:
                return _agent_capabilities(agents[args.agent_id], registry, args.runtime, args.json)
            return _capability_matrix(catalog, registry, args.json)
        if args.command == "run":
            return _run(agents[args.agent_id], registry.get(args.runtime), args)
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


# Integraciones que un agente puede aprovechar y ninguna es obligatoria: se
# informan como OPTIONAL para que su ausencia no se lea como un fallo.
OPTIONAL_TOOLING = [
    ("git", "control de versiones local"),
    ("gh", "GitHub CLI"),
    ("docker", "contenedores"),
    ("ollama", "modelos locales"),
]


def _doctor(agents: list[dict], skills_dir: Path | None, registry: RuntimeRegistry, as_json: bool) -> int:
    python_ok = sys.version_info >= (3, 11)
    report: dict[str, Any] = {
        "python": {"version": sys.version.split()[0], "status": "AVAILABLE" if python_ok else "UNSUPPORTED"},
        "runtimes": [],
        "integrations": [],
        "skills": None,
        "plugin_errors": registry.plugin_errors,
    }
    for runtime in registry:
        detection = runtime.detect()
        report["runtimes"].append({
            "id": runtime.descriptor.id,
            "status": "AVAILABLE" if detection.available else "MISSING",
            "kind": runtime.descriptor.kind,
            "maturity": runtime.descriptor.maturity,
            "detail": detection.detail,
        })
    for name, description in OPTIONAL_TOOLING:
        found = shutil.which(name)
        report["integrations"].append({
            "id": name,
            "status": "AVAILABLE" if found else "OPTIONAL",
            "detail": found or f"no encontrado ({description}, opcional)",
        })
    if skills_dir:
        base = skills_dir.expanduser().resolve()
        required = sorted({s for a in agents for s in a["skill_dependencies"]})
        missing = [s for s in required if not (base / s).exists()]
        report["skills"] = {
            "directory": str(base),
            "required": required,
            "missing": missing,
            "status": "AVAILABLE" if not missing else "OPTIONAL",
        }
    if as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if python_ok else 1
    print(f"Python: {report['python']['version']} ({'OK' if python_ok else 'requiere 3.11+'})")
    print("Runtimes:")
    for item in report["runtimes"]:
        print(f"  {item['id']:<10} {item['status']:<10} {item['maturity']:<12} {item['detail']}")
    print("Integraciones opcionales:")
    for item in report["integrations"]:
        print(f"  {item['id']:<10} {item['status']:<10} {item['detail']}")
    if report["skills"]:
        skills = report["skills"]
        print(f"Skills: {len(skills['required']) - len(skills['missing'])}/{len(skills['required'])} disponibles en {skills['directory']}")
        if skills["missing"]:
            print("Faltantes: " + ", ".join(skills["missing"]))
    for error in registry.plugin_errors:
        print(f"Plugin ignorado: {error}", file=sys.stderr)
    return 0 if python_ok else 1


def _runtimes(registry: RuntimeRegistry, as_json: bool) -> int:
    data = []
    for runtime in registry:
        detection = runtime.detect()
        declared = runtime.capabilities()
        data.append({
            **runtime.descriptor.as_dict(),
            "available": detection.available,
            "detail": detection.detail,
            "capabilities": declared.provides,
            "modalities": list(declared.modalities),
        })
    if as_json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0
    for item in data:
        estado = "AVAILABLE" if item["available"] else "MISSING"
        autonomo = "autónomo" if item["autonomous"] else "asistido"
        print(f"{item['id']:<10} {estado:<10} {item['kind']:<7} {autonomo:<9} {item['maturity']:<12} {item['name']}")
    return 0


def _runtime_inspect(registry: RuntimeRegistry, runtime_id: str, as_json: bool) -> int:
    runtime = registry.get(runtime_id)
    detection = runtime.detect()
    declared = runtime.capabilities()
    if as_json:
        payload = {**runtime.descriptor.as_dict(), "detection": detection.as_dict(), **declared.as_dict()}
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0
    print(f"{runtime.descriptor.name} ({runtime.descriptor.id})")
    print(f"Tipo: {runtime.descriptor.kind} | Ejecución autónoma: {'sí' if runtime.descriptor.autonomous else 'no'}")
    print(f"Madurez del adaptador: {runtime.descriptor.maturity}")
    print(f"Disponibilidad: {'AVAILABLE' if detection.available else 'MISSING'} — {detection.detail}")
    print(f"Modalidades de entrada: {', '.join(declared.modalities)}")
    print("Capacidades declaradas:")
    for item, nivel in sorted(declared.provides.items()):
        # Un plugin puede declarar una capacidad que este núcleo no conoce: se
        # muestra igualmente, marcada, en vez de romper la inspección.
        conocida = CAPABILITIES.get(item)
        print(f"  {item:<26} {nivel:<12} {conocida.description if conocida else 'capacidad no declarada en el modelo'}")
    for nota in declared.notes:
        print(f"Nota: {nota}")
    return 0


def _agent_capabilities(agent: dict, registry: RuntimeRegistry, runtime_id: str | None, as_json: bool) -> int:
    seleccion = [registry.get(runtime_id)] if runtime_id else list(registry)
    resueltas = [runtime.resolve(agent) for runtime in seleccion]
    if as_json:
        payload = {
            "agent_id": agent["id"],
            "required": list(required_capabilities(agent)),
            "optional": list(optional_capabilities(agent)),
            "requires_approval": list(approval_required_capabilities(agent)),
            "effects": effect_summary(agent),
            "resolutions": [item.as_dict() for item in resueltas],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0
    print(f"{agent['name']} ({agent['id']})")
    print("Capacidades requeridas: " + ", ".join(required_capabilities(agent)))
    print("Capacidades opcionales: " + (", ".join(optional_capabilities(agent)) or "ninguna"))
    print("Efectos autorizados: " + ", ".join(f"{efecto} ({len(items)})" for efecto, items in effect_summary(agent).items()))
    for resolution in resueltas:
        print(f"\nRuntime `{resolution.runtime_id}`: {resolution.status}")
        for outcome in resolution.outcomes:
            print(f"  {outcome.capability:<26} {outcome.status:<12} {outcome.detail}")
        for nota in resolution.notes:
            print(f"  nota: {nota}")
    return 0


def _capability_matrix(catalog: dict, registry: RuntimeRegistry, as_json: bool) -> int:
    resueltas = resolutions(catalog, registry)
    if as_json:
        payload = {aid: {rid: item.as_dict() for rid, item in por_runtime.items()} for aid, por_runtime in resueltas.items()}
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0
    ids = registry.ids()
    print(f"{'agente':<38} " + " ".join(f"{rid:<13}" for rid in ids))
    for agent_id, por_runtime in resueltas.items():
        print(f"{agent_id:<38} " + " ".join(f"{por_runtime[rid].status:<13}" for rid in ids))
    print("\nEstados: SUPPORTED (nativo) · DEGRADED (condicional) · UNSUPPORTED (falta una capacidad requerida)")
    print("La matriz demuestra que el contrato encaja, no que la ejecución cumpla la misión.")
    return 0


def _run(agent: dict, runtime: AgentRuntime, args: argparse.Namespace) -> int:
    if args.dry_run:
        preparation = runtime.prepare(agent, args.task, args.target)
        print(json.dumps(preparation.as_dict(), indent=2, ensure_ascii=False))
        return 0
    preparation, result = runtime.run(agent, args.task, target=args.target, cwd=args.cwd)
    if args.evidence:
        envelope = execution_envelope(
            agent,
            preparation,
            runtime.detect(),
            result,
            runtime_descriptor=runtime.descriptor.as_dict(),
        )
        destino = args.evidence.expanduser().resolve()
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(envelope, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(f"Evidencia: {destino}", file=sys.stderr)
    prompt = result.artifacts.get("prompt")
    if prompt:
        print(prompt)
    if result.status != "COMPLETED":
        print(f"{result.status}: {result.detail}", file=sys.stderr)
    return result.exit_code


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
