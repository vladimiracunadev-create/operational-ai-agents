
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .catalog import load_catalog
from .render import (
    parse_frontmatter,
    render_agent_readme,
    render_claude,
    render_instructions,
    valid_agent_id,
)

REQUIRED = {
    "id", "name", "version", "status", "category", "risk", "description",
    "delegate_when", "mission", "tools", "disallowed_tools", "skill_dependencies",
    "permission_mode", "memory", "effort", "max_turns", "phases", "phase_details",
    "required_inputs", "deliverables", "approval_points", "checks", "non_goals", "examples",
}


def validate(root: Path) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    catalog = load_catalog(root)
    ids: set[str] = set()
    allowed_status = set(catalog.get("maturity_model", {}))
    for agent in catalog["agents"]:
        missing = sorted(REQUIRED - set(agent))
        if missing:
            issues.append(_issue("error", agent.get("id", "?"), f"Campos faltantes: {', '.join(missing)}"))
            continue
        aid = agent["id"]
        if aid in ids:
            issues.append(_issue("error", aid, "ID duplicado"))
        ids.add(aid)
        if not valid_agent_id(aid):
            issues.append(_issue("error", aid, "ID inválido; use kebab-case"))
        if agent["status"] not in allowed_status:
            issues.append(_issue("error", aid, f"Estado no definido: {agent['status']}"))
        if not agent["tools"]:
            issues.append(_issue("error", aid, "Tool allowlist vacía"))
        if len(agent["phases"]) < 4:
            issues.append(_issue("error", aid, "El agente necesita al menos cuatro fases"))
        # Una fase sin explicación produce instrucciones que no dicen nada.
        sin_detalle = [p for p in agent["phases"] if not agent["phase_details"].get(p, "").strip()]
        if sin_detalle:
            issues.append(_issue("error", aid, f"Fases sin descripción: {', '.join(sin_detalle)}"))
        huerfanos = [p for p in agent["phase_details"] if p not in agent["phases"]]
        if huerfanos:
            issues.append(_issue("error", aid, f"Descripciones sin fase: {', '.join(huerfanos)}"))
        if not agent["approval_points"]:
            issues.append(_issue("error", aid, "Sin gates de aprobación"))
        write_capable = "Edit" in agent["tools"] or "Write" in agent["tools"]
        if write_capable and agent["permission_mode"] in {"bypassPermissions", "acceptEdits"}:
            issues.append(_issue("error", aid, "Un agente mutante no puede omitir aprobación de permisos"))
        if write_capable and agent.get("isolation") != "worktree":
            issues.append(_issue("warning", aid, "Agente mutante sin aislamiento worktree"))
        base = root / "agents" / aid
        required_paths = [
            "agent.yaml", "instructions.md", "AGENT.md", "README.md",
            "policies/policy.yaml", "schemas/input.schema.json",
            "schemas/output.schema.json", "evals/cases.jsonl",
        ]
        for relative in required_paths:
            if not (base / relative).is_file():
                issues.append(_issue("error", aid, f"Falta agents/{aid}/{relative}"))
        if not base.is_dir():
            continue
        _check_generated(root, agent, issues)
        _check_json_files(base, aid, issues)
        _check_evals(base, aid, issues)
    folders = {p.name for p in (root / "agents").iterdir() if p.is_dir() and not p.name.startswith("_")}
    for orphan in sorted(folders - ids):
        issues.append(_issue("warning", orphan, "Carpeta sin entrada en el catálogo"))
    return issues


def _check_generated(root: Path, agent: dict[str, Any], issues: list[dict[str, str]]) -> None:
    aid = agent["id"]
    base = root / "agents" / aid
    try:
        manifest = json.loads((base / "agent.yaml").read_text(encoding="utf-8"))
        if manifest != agent:
            issues.append(_issue("error", aid, "agent.yaml tiene drift respecto del catálogo"))
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(_issue("error", aid, f"agent.yaml inválido: {exc}"))
    for filename, expected in [
        ("instructions.md", render_instructions(agent)),
        ("AGENT.md", render_claude(agent, preload_skills=False)),
        ("README.md", render_agent_readme(agent)),
    ]:
        try:
            actual = (base / filename).read_text(encoding="utf-8")
            if actual != expected:
                issues.append(_issue("error", aid, f"{filename} tiene drift; ejecute sync"))
        except OSError as exc:
            issues.append(_issue("error", aid, f"No se pudo leer {filename}: {exc}"))
    try:
        frontmatter = parse_frontmatter((base / "AGENT.md").read_text(encoding="utf-8"))
        if frontmatter.get("name") != aid:
            issues.append(_issue("error", aid, "AGENT.md declara otro nombre"))
    except (OSError, ValueError) as exc:
        issues.append(_issue("error", aid, f"AGENT.md inválido: {exc}"))


def _check_json_files(base: Path, aid: str, issues: list[dict[str, str]]) -> None:
    for relative in ["policies/policy.yaml", "schemas/input.schema.json", "schemas/output.schema.json"]:
        try:
            json.loads((base / relative).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(_issue("error", aid, f"{relative} inválido: {exc}"))


def _check_evals(base: Path, aid: str, issues: list[dict[str, str]]) -> None:
    path = base / "evals" / "cases.jsonl"
    count = 0
    try:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            count += 1
            case = json.loads(line)
            for field in ("id", "task", "expected_phases", "expected_approvals", "required_deliverables"):
                if field not in case:
                    issues.append(_issue("error", aid, f"Eval línea {number} sin {field}"))
        if count < 3:
            issues.append(_issue("error", aid, "Se requieren al menos tres evals"))
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(_issue("error", aid, f"Eval JSONL inválido: {exc}"))


def _issue(level: str, agent_id: str, message: str) -> dict[str, str]:
    return {"level": level, "agent_id": agent_id, "message": message}
