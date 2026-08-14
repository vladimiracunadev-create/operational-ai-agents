from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from operational_agents.catalog import agents_by_id, load_catalog
from operational_agents.evaluation import evaluate_agent
from operational_agents.exporter import export_claude, uninstall_claude
from operational_agents.planner import create_plan
from operational_agents.redaction import redact
from operational_agents.render import (
    parse_frontmatter,
    render_agent_readme,
    render_claude,
    valid_agent_id,
)
from operational_agents.syncer import sync
from operational_agents.validator import validate

MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
INDENTED_HEADING = re.compile(r"^\s{4,}#{1,6}\s")
INDENTED_TABLE_RULE = re.compile(r"^\s{4,}\|[\s:-]+\|\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")


def markdown_files() -> list[Path]:
    return sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts and "egg-info" not in str(p))


def outside_code_fences(text: str):
    """Produce (numero_de_linea, linea) solo para el contenido fuera de bloques de código."""
    inside = False
    for number, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            inside = not inside
            continue
        if not inside:
            yield number, line


def heading_text(line: str) -> str:
    """Texto renderizado de un encabezado, sin la sintaxis Markdown."""
    text = re.sub(r"^#{1,6}\s+", "", line).strip()
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.replace("&nbsp;", "\xa0")
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]*)\*\*", r"\1", text)
    return re.sub(r"\*([^*]*)\*", r"\1", text)


def github_slug(text: str) -> str:
    """Ancla que GitHub genera para un encabezado.

    Minúsculas, los espacios pasan a guiones y se descartan puntuación,
    símbolos y separadores. Los emoji desaparecen, pero el variation
    selector U+FE0F NO: es categoría Mn y sobrevive dentro del ancla.
    Ignorarlo es exactamente lo que rompió `#-cli` y `#-arquitectura`.
    """
    out = []
    for char in text.strip().lower():
        if char == " ":
            out.append("-")
        elif char in "-_":
            out.append(char)
        elif unicodedata.category(char)[0] in ("P", "S", "Z", "C"):
            continue
        else:
            out.append(char)
    return "".join(out)


def anchors_of(path: Path) -> set[str]:
    """Anclas destino de un Markdown: encabezados más ids HTML explícitos."""
    text = path.read_text(encoding="utf-8")
    found = {
        github_slug(heading_text(line))
        for _, line in outside_code_fences(text)
        if re.match(r"^#{1,6} ", line)
    }
    found.update(re.findall(r'<a[^>]+(?:id|name)="([^"]+)"', text))
    return found


class RepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog(ROOT)
        cls.agents = agents_by_id(cls.catalog)

    def test_catalog_size_is_declared(self):
        self.assertEqual(12, len(self.catalog["agents"]))

    def test_ids_unique_and_valid(self):
        ids = list(self.agents)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(valid_agent_id(item) for item in ids))

    def test_all_agents_honestly_implemented(self):
        self.assertEqual({"IMPLEMENTED"}, {a["status"] for a in self.catalog["agents"]})

    def test_validator_has_no_issues(self):
        self.assertEqual([], validate(ROOT))

    def test_sync_has_no_drift(self):
        self.assertEqual([], sync(ROOT, check=True))

    def test_packages_are_complete(self):
        required = ["agent.yaml", "instructions.md", "AGENT.md", "README.md", "policies/policy.yaml", "schemas/input.schema.json", "schemas/output.schema.json", "evals/cases.jsonl"]
        for aid in self.agents:
            for relative in required:
                self.assertTrue((ROOT / "agents" / aid / relative).is_file(), f"{aid}/{relative}")

    def test_manifests_match_catalog(self):
        for aid, agent in self.agents.items():
            actual = json.loads((ROOT / "agents" / aid / "agent.yaml").read_text(encoding="utf-8"))
            self.assertEqual(agent, actual)

    def test_claude_frontmatter(self):
        for agent in self.catalog["agents"]:
            data = parse_frontmatter(render_claude(agent))
            self.assertEqual(agent["id"], data["name"])
            self.assertIn("description", data)
            self.assertEqual("inherit", data["model"])

    def test_mutating_agents_do_not_bypass_permissions(self):
        for agent in self.catalog["agents"]:
            if "Write" in agent["tools"] or "Edit" in agent["tools"]:
                self.assertEqual("default", agent["permission_mode"])
                self.assertEqual("worktree", agent["isolation"])

    def test_read_only_agents_deny_writes(self):
        read_only = [a for a in self.catalog["agents"] if "Write" not in a["tools"] and "Edit" not in a["tools"]]
        self.assertGreaterEqual(len(read_only), 3)
        for agent in read_only:
            self.assertIn("Write", agent["disallowed_tools"])
            self.assertIn("Edit", agent["disallowed_tools"])

    def test_every_agent_has_human_gates(self):
        for agent in self.catalog["agents"]:
            self.assertTrue(agent["approval_points"])

    def test_plan_is_deterministic_in_identity(self):
        agent = self.agents["repository-evolution-agent"]
        first = create_plan(agent, "Examina este repositorio de forma segura")
        second = create_plan(agent, "Examina este repositorio de forma segura")
        self.assertEqual(first["execution_id"], second["execution_id"])
        self.assertNotEqual(first["created_at"], "")

    def test_plan_does_not_grant_authorization(self):
        plan = create_plan(self.agents["release-governance-agent"], "Prepara el próximo release")
        self.assertIn("aprobación", plan["notice"])
        self.assertIn("tag_or_release_publish", plan["approval_gates"])

    def test_all_deterministic_evals_pass(self):
        results = [case for agent in self.catalog["agents"] for case in evaluate_agent(ROOT, agent)]
        self.assertEqual(36, len(results))
        self.assertTrue(all(item["passed"] for item in results))

    def test_export_writes_every_agent(self):
        with tempfile.TemporaryDirectory() as temp:
            paths = export_claude(self.catalog["agents"], Path(temp), preload_skills=True)
            self.assertEqual(12, len(paths))
            self.assertTrue(all(path.is_file() for path in paths))
            self.assertIn("skills:", paths[0].read_text(encoding="utf-8"))

    def test_export_preserves_unmanaged_agent(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            conflict = target / "repository-evolution-agent.md"
            conflict.write_text("user-owned", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                export_claude(self.catalog["agents"], target)
            self.assertEqual("user-owned", conflict.read_text(encoding="utf-8"))

    def test_uninstall_preserves_unmanaged_agent(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            conflict = target / "repository-evolution-agent.md"
            conflict.write_text("user-owned", encoding="utf-8")
            removed = uninstall_claude(self.catalog["agents"], target)
            self.assertEqual([], removed)
            self.assertTrue(conflict.exists())

    def test_redaction(self):
        text = "token=abc123 password: supersecret Authorization: Bearer xyz"
        cleaned = redact(text)
        self.assertNotIn("abc123", cleaned)
        self.assertNotIn("supersecret", cleaned)
        self.assertNotIn("Bearer xyz", cleaned)

    def test_json_schemas_are_valid_json(self):
        for path in ROOT.glob("agents/*/schemas/*.json"):
            json.loads(path.read_text(encoding="utf-8"))

    def test_agent_readme_is_generated_from_catalog(self):
        for aid, agent in self.agents.items():
            actual = (ROOT / "agents" / aid / "README.md").read_text(encoding="utf-8")
            self.assertEqual(render_agent_readme(agent), actual, f"{aid}/README.md tiene drift")
            self.assertIn("operational-agents sync", actual.splitlines()[0])

    def test_markdown_headings_and_tables_are_not_indented(self):
        """Una sangría de cuatro espacios convierte el Markdown en un bloque de código."""
        offenders = []
        for path in markdown_files():
            for number, line in outside_code_fences(path.read_text(encoding="utf-8")):
                if INDENTED_HEADING.match(line) or INDENTED_TABLE_RULE.match(line):
                    offenders.append(f"{path.relative_to(ROOT)}:{number}")
        self.assertEqual([], offenders)

    def test_relative_documentation_links_resolve(self):
        broken = []
        for path in markdown_files():
            for target in MARKDOWN_LINK.findall(path.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                relative = target.split("#", 1)[0]
                if not relative:
                    continue
                if not (path.parent / relative).exists():
                    broken.append(f"{path.relative_to(ROOT)} -> {target}")
        self.assertEqual([], broken)

    def test_anchor_links_resolve(self):
        """Un ancla rota no rompe la build, solo lleva al lector a ninguna parte."""
        from urllib.parse import unquote

        broken = []
        cache: dict[Path, set[str]] = {}
        for path in markdown_files():
            for target in MARKDOWN_LINK.findall(path.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "mailto:")) or "#" not in target:
                    continue
                relative, _, anchor = target.partition("#")
                if not anchor:
                    continue
                destination = (path.parent / relative).resolve() if relative else path
                if destination.suffix != ".md" or not destination.is_file():
                    continue
                if destination not in cache:
                    cache[destination] = anchors_of(destination)
                if unquote(anchor) not in cache[destination]:
                    broken.append(f"{path.relative_to(ROOT)} -> {target}")
        self.assertEqual([], broken)

    def test_every_phase_is_explained(self):
        """Una fase sin descripción produce instrucciones que no dicen nada."""
        for agent in self.catalog["agents"]:
            self.assertEqual(list(agent["phases"]), list(agent["phase_details"]), agent["id"])
            for phase, detail in agent["phase_details"].items():
                self.assertGreater(len(detail.strip()), 40, f"{agent['id']}/{phase} apenas se explica")
            rendered = (ROOT / "agents" / agent["id"] / "instructions.md").read_text(encoding="utf-8")
            for detail in agent["phase_details"].values():
                self.assertIn(detail, rendered, agent["id"])

    def test_documented_agent_counts_are_current(self):
        """Cualquier «N agentes» escrito en la documentación debe ser cierto."""
        palabras = {"diez": 10, "once": 11, "doce": 12, "trece": 13}
        total = len(self.catalog["agents"])
        patron = re.compile(r"\b(\d{1,3}|" + "|".join(palabras) + r")\s+agentes\b", re.IGNORECASE)
        wrong = []
        for path in markdown_files():
            for number, line in outside_code_fences(path.read_text(encoding="utf-8")):
                for match in patron.findall(line):
                    value = palabras.get(match.lower())
                    value = int(match) if value is None and match.isdigit() else value
                    if value is not None and value != total:
                        wrong.append(f"{path.relative_to(ROOT)}:{number} dice '{match} agentes'")
        self.assertEqual([], wrong)

    def test_agents_carry_no_personal_data(self):
        """El catálogo es público: nada de rutas del autor ni identidades concretas."""
        blob = json.dumps(self.catalog, ensure_ascii=False)
        for forbidden in ("C:\\\\", "/home/", "vladimiracunadev", "Vladimir", "portfolio-pages"):
            self.assertNotIn(forbidden, blob, f"dato personal en el catálogo: {forbidden}")

    def test_root_readme_covers_every_catalog_agent(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for aid in self.agents:
            self.assertIn(f"agents/{aid}/README.md", readme, f"{aid} ausente del catálogo del README")

    def test_landing_page_is_generated_from_catalog(self):
        from operational_agents.site import render_landing, site_stats

        stats = site_stats(ROOT, self.catalog)
        expected = render_landing(self.catalog, stats)
        actual = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        self.assertEqual(expected, actual, "site/index.html tiene drift; ejecute sync")
        for agent in self.catalog["agents"]:
            self.assertIn(agent["name"], actual, f"{agent['id']} ausente de la landing")
            self.assertIn(f"agents/{agent['id']}/README.md", actual)
        self.assertEqual(len(self.catalog["agents"]), stats["agentes"])
        self.assertEqual(36, stats["evaluaciones"])

    def test_readme_badges_match_reality(self):
        """Los badges numéricos del README son afirmaciones: deben ser ciertas."""
        from operational_agents.site import site_stats

        stats = site_stats(ROOT, self.catalog)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(f"badge/agentes-{stats['agentes']}-", readme)
        self.assertIn(f"badge/tests-{stats['pruebas']}-", readme)
        self.assertIn(f"badge/evals_deterministas-{stats['evaluaciones']}-", readme)

    def test_version_is_coherent_across_sources(self):
        """pyproject, catálogo y badge del README deben declarar la misma versión."""
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        declared = re.search(r'^version = "([^"]+)"', pyproject, re.MULTILINE).group(1)
        self.assertEqual(self.catalog["repository_version"], declared)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(f"badge/version-{declared}-", readme)

    def test_cli_adds_no_permission_bypass(self):
        """Respalda la garantía de seguridad declarada en README y docs/SECURITY_MODEL.md."""
        source = (ROOT / "src" / "operational_agents" / "cli.py").read_text(encoding="utf-8")
        for forbidden in ("shell=True", "--dangerously-skip-permissions", "bypassPermissions", "--allowedTools"):
            self.assertNotIn(forbidden, source)

    def test_server_refuses_non_loopback_bind_without_optin(self):
        from operational_agents.server import serve

        os.environ.pop("OPERATIONAL_AGENTS_ALLOW_REMOTE_BIND", None)
        with self.assertRaises(ValueError):
            serve(ROOT, "0.0.0.0", 0)

    def test_cli_list_and_validate(self):
        env = dict(os.environ, PYTHONPATH=str(ROOT / "src"), OPERATIONAL_AGENTS_ROOT=str(ROOT))
        for args in (["list", "--json"], ["validate", "--json"], ["eval", "--all"]):
            result = subprocess.run([sys.executable, "-m", "operational_agents", *args], cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
