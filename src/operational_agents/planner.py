
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any


def create_plan(agent: dict[str, Any], task: str, target: str | None = None) -> dict[str, Any]:
    task = task.strip()
    if len(task) < 8:
        raise ValueError("La tarea debe contener al menos 8 caracteres")
    seed = f"{agent['id']}\0{task}\0{target or ''}"
    execution_id = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
    write_capable = "Edit" in agent["tools"] or "Write" in agent["tools"]
    return {
        "schema_version": "1.0",
        "execution_id": execution_id,
        "created_at": datetime.now(UTC).isoformat(),
        "agent_id": agent["id"],
        "agent_version": agent["version"],
        "task": task,
        "target": target,
        "mode": "read-plan-write-verify" if write_capable else "read-only-analysis",
        "phases": [
            {"index": index, "id": phase, "status": "pending"}
            for index, phase in enumerate(agent["phases"], 1)
        ],
        "tool_allowlist": agent["tools"],
        "tool_denylist": agent.get("disallowed_tools", []),
        "optional_skills": agent.get("skill_dependencies", []),
        "approval_gates": agent["approval_points"],
        "expected_deliverables": agent["deliverables"],
        "non_goals": agent["non_goals"],
        "notice": "Plan determinista: no representa una ejecución del modelo ni concede autorización ni aprobación humana.",
    }


def plan_markdown(plan: dict[str, Any]) -> str:
    phases = "\n".join(f"{item['index']}. `{item['id']}`" for item in plan["phases"])
    approvals = "\n".join(f"- `{item}`" for item in plan["approval_gates"])
    deliverables = "\n".join(f"- `{item}`" for item in plan["expected_deliverables"])
    return f"""# Plan {plan['execution_id']}

- Agente: `{plan['agent_id']}` v{plan['agent_version']}
- Modo: `{plan['mode']}`
- Objetivo: {plan['task']}
- Destino: {plan['target'] or 'no especificado'}

## Fases

{phases}

## Gates de aprobación

{approvals}

## Entregables

{deliverables}

> {plan['notice']}
"""


def packet(agent: dict[str, Any], instructions: str, task: str, target: str | None) -> str:
    payload = {
        "agent": {"id": agent["id"], "version": agent["version"], "mission": agent["mission"]},
        "task": task,
        "target": target,
        "authorization": {"read": True, "write": False, "publish": False},
    }
    return instructions.rstrip() + "\n\n---\n\n## Task envelope\n\n```json\n" + json.dumps(payload, indent=2, ensure_ascii=False) + "\n```\n"
