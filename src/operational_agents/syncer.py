
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .catalog import load_catalog
from .compatibility import render_compatibility_matrix
from .render import render_agent_readme, render_claude, render_instructions
from .site import render_landing, site_stats


def generated_files(root: Path, agent: dict[str, Any]) -> dict[Path, str]:
    base = root / "agents" / agent["id"]
    return {
        base / "agent.yaml": json.dumps(agent, indent=2, ensure_ascii=False) + "\n",
        base / "instructions.md": render_instructions(agent),
        base / "AGENT.md": render_claude(agent, preload_skills=False),
        base / "README.md": render_agent_readme(agent),
    }


def generated_site_files(root: Path, catalog: dict[str, Any]) -> dict[Path, str]:
    """Vistas del repositorio completo, no de un agente concreto."""
    site = root / "site"
    return {
        site / "index.html": render_landing(catalog, site_stats(root, catalog)),
        # Sin este archivo, GitHub Pages pasaría el sitio por Jekyll y
        # descartaría cualquier ruta que empiece por guion bajo.
        site / ".nojekyll": "",
    }


def generated_doc_files(root: Path, catalog: dict[str, Any]) -> dict[Path, str]:
    """Documentación cuya verdad vive en el código, no en la redacción.

    La matriz de compatibilidad se calcula con los adaptadores del repositorio
    y sin consultar el entorno: así el documento no puede afirmar una
    compatibilidad que el código no sostenga, ni cambiar según la máquina.
    """
    return {root / "docs" / "COMPATIBILITY_MATRIX.md": render_compatibility_matrix(catalog)}


def sync(root: Path, check: bool = False) -> list[str]:
    catalog = load_catalog(root)
    targets: dict[Path, str] = {}
    for agent in catalog["agents"]:
        targets.update(generated_files(root, agent))
    targets.update(generated_site_files(root, catalog))
    targets.update(generated_doc_files(root, catalog))
    changed: list[str] = []
    for path, expected in targets.items():
        actual = path.read_text(encoding="utf-8") if path.exists() else None
        if actual != expected:
            changed.append(str(path.relative_to(root)))
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(expected, encoding="utf-8", newline="\n")
    return changed
