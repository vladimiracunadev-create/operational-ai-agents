
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def find_root(start: Path | None = None) -> Path:
    configured = os.environ.get("OPERATIONAL_AGENTS_ROOT")
    if configured:
        root = Path(configured).expanduser().resolve()
        if (root / "catalog" / "agents.yaml").is_file():
            return root
        raise FileNotFoundError(f"OPERATIONAL_AGENTS_ROOT no contiene catalog/agents.yaml: {root}")
    candidates = [start or Path.cwd(), Path(__file__).resolve()]
    for candidate in candidates:
        current = candidate.resolve()
        if current.is_file():
            current = current.parent
        for parent in (current, *current.parents):
            if (parent / "catalog" / "agents.yaml").is_file():
                return parent
    raise FileNotFoundError("No se encontró la raíz de operational-ai-agents")


def load_catalog(root: Path | None = None) -> dict[str, Any]:
    path = (root or find_root()) / "catalog" / "agents.yaml"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Catálogo inválido en {path}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("agents"), list):
        raise ValueError("El catálogo debe ser un objeto con una lista agents")
    return data


def agents_by_id(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {agent["id"]: agent for agent in catalog["agents"]}


def get_agent(agent_id: str, root: Path | None = None) -> dict[str, Any]:
    agents = agents_by_id(load_catalog(root))
    try:
        return agents[agent_id]
    except KeyError as exc:
        choices = ", ".join(sorted(agents))
        raise KeyError(f"Agente desconocido: {agent_id}. Disponibles: {choices}") from exc
