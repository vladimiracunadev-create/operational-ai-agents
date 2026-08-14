
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .planner import create_plan


def evaluate_agent(root: Path, agent: dict[str, Any]) -> list[dict[str, Any]]:
    path = root / "agents" / agent["id"] / "evals" / "cases.jsonl"
    results: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        case = json.loads(line)
        plan = create_plan(agent, case["task"])
        phase_ids = {item["id"] for item in plan["phases"]}
        serialized_plan = json.dumps(plan, ensure_ascii=False).lower()
        checks = {
            "phases": set(case["expected_phases"]).issubset(phase_ids),
            "approvals": set(case["expected_approvals"]).issubset(set(plan["approval_gates"])),
            "deliverables": set(case["required_deliverables"]).issubset(set(plan["expected_deliverables"])),
            "forbidden_claims_absent": all(claim.lower() not in serialized_plan for claim in case.get("forbidden_claims", [])),
        }
        results.append({"case_id": case["id"], "passed": all(checks.values()), "checks": checks})
    return results
