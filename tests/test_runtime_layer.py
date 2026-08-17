"""Pruebas de la capa de runtimes y capacidades.

Lo que estas pruebas protegen no es que el código funcione, sino que la
portabilidad no se pague con seguridad: que ningún runtime conceda permisos que
el contrato no da, que una capacidad ausente se declare en lugar de fingirse y
que el núcleo siga funcionando sin proveedor, sin clave y sin red.
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import threading
import unittest
from pathlib import Path
from unittest import mock
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from operational_agents.capabilities import (
    BLOCKED,
    CAPABILITIES,
    DEGRADED,
    SUPPORTED,
    UNSUPPORTED,
    approval_required_capabilities,
    denied_capabilities,
    effect_summary,
    optional_capabilities,
    required_capabilities,
    resolve,
    tool_capabilities,
    unmapped_tools,
)
from operational_agents.catalog import agents_by_id, load_catalog
from operational_agents.compatibility import matrix, render_compatibility_matrix, resolutions
from operational_agents.evidence import execution_envelope
from operational_agents.runtimes import (
    NOT_EXECUTED,
    AgentRuntime,
    ClaudeCodeRuntime,
    Detection,
    ExecutionResult,
    ManualRuntime,
    Preparation,
    RuntimeCapabilities,
    RuntimeDescriptor,
    RuntimeRegistry,
    default_registry,
)
from operational_agents.runtimes import base as runtime_base
from operational_agents.runtimes.registry import ENTRY_POINT_GROUP, load_plugins


class NullRuntime(AgentRuntime):
    """Runtime de laboratorio: no ofrece nada y cuenta cuánto se le pregunta."""

    descriptor = RuntimeDescriptor("null", "Sin capacidades", "test", "No ofrece ninguna capacidad", autonomous=False)

    def __init__(self, provides: dict[str, str] | None = None) -> None:
        self.provides = provides or {}
        self.detect_calls = 0
        self.execute_calls = 0

    def capabilities(self) -> RuntimeCapabilities:
        return RuntimeCapabilities(provides=self.provides)

    def detect(self) -> Detection:
        self.detect_calls += 1
        return Detection(True, "runtime de prueba")

    def execute(self, preparation: Preparation, cwd: Path) -> ExecutionResult:
        self.execute_calls += 1
        return ExecutionResult("COMPLETED", 0, "ejecutado")


class CapabilityModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog(ROOT)
        cls.agents = agents_by_id(cls.catalog)

    def test_tools_map_to_capabilities(self):
        self.assertEqual(("filesystem.read", "filesystem.write"), tool_capabilities(["Read", "Write", "Edit"]))

    def test_parameterized_tool_keeps_its_capability(self):
        """`Agent(a, b)` acota a quién se delega; la capacidad sigue siendo delegar."""
        self.assertEqual(("orchestration.delegate",), tool_capabilities(["Agent(uno, dos)"]))
        self.assertEqual((), unmapped_tools(["Agent(uno, dos)"]))

    def test_every_catalog_tool_has_a_capability(self):
        for agent in self.catalog["agents"]:
            self.assertEqual((), unmapped_tools(agent["tools"]), agent["id"])

    def test_skills_are_optional_capabilities(self):
        """Un agente que declara `Skill` no depende de que el runtime sepa cargarlo."""
        agent = self.agents["repository-evolution-agent"]
        self.assertIn("knowledge.skill", optional_capabilities(agent))
        self.assertNotIn("knowledge.skill", required_capabilities(agent))
        sin_skills = dict.fromkeys(required_capabilities(agent), "full")
        resolution = resolve(agent, sin_skills, runtime_id="sin-skills")
        self.assertEqual(SUPPORTED, resolution.status)
        self.assertNotIn("knowledge.skill", resolution.executable)

    def test_allowlist_is_exhaustive(self):
        """Lo que el contrato no autoriza queda denegado, aunque el runtime lo ofrezca."""
        agent = self.agents["incident-root-cause-agent"]
        self.assertIn("filesystem.write", denied_capabilities(agent))
        self.assertNotIn("filesystem.read", denied_capabilities(agent))

    def test_effects_group_by_consequence_not_by_tool_name(self):
        efectos = effect_summary(self.agents["repository-evolution-agent"])
        self.assertIn("filesystem.write", efectos["write"])
        self.assertIn("shell.execute", efectos["execute"])

    def test_capabilities_with_write_or_execute_require_approval(self):
        for identifier, item in CAPABILITIES.items():
            if {"write", "execute"} & set(item.effects):
                self.assertTrue(item.requires_approval, identifier)

    def test_read_only_agents_require_no_approval_capability_beyond_shell(self):
        agent = self.agents["portfolio-curator-agent"]
        self.assertNotIn("filesystem.write", approval_required_capabilities(agent))

    def test_declared_capabilities_win_over_derivation(self):
        agent = dict(self.agents["repository-evolution-agent"])
        agent["capabilities"] = {"required": ["filesystem.read"], "optional": []}
        self.assertEqual(("filesystem.read",), required_capabilities(agent))
        self.assertEqual((), optional_capabilities(agent))

    def test_missing_capability_is_declared_not_simulated(self):
        agent = self.agents["repository-evolution-agent"]
        resolution = resolve(agent, {"filesystem.read": "full"}, runtime_id="parcial")
        self.assertEqual(UNSUPPORTED, resolution.status)
        self.assertIn("shell.execute", resolution.missing)
        self.assertNotIn("shell.execute", resolution.executable)

    def test_conditional_capability_degrades_instead_of_failing(self):
        agent = self.agents["incident-root-cause-agent"]
        provides = dict.fromkeys(required_capabilities(agent), "conditional")
        resolution = resolve(agent, provides, runtime_id="condicional")
        self.assertEqual(DEGRADED, resolution.status)
        self.assertEqual(set(resolution.degraded), set(required_capabilities(agent)))

    def test_offered_but_unauthorized_capability_is_blocked(self):
        agent = self.agents["incident-root-cause-agent"]
        provides = dict.fromkeys(CAPABILITIES, "full")
        resolution = resolve(agent, provides, runtime_id="todopoderoso")
        self.assertIn("filesystem.write", resolution.blocked)
        self.assertNotIn("filesystem.write", resolution.executable_set)
        self.assertEqual(BLOCKED, next(o.status for o in resolution.outcomes if o.capability == "filesystem.write"))

    def test_unsupported_modality_is_reported(self):
        agent = dict(self.agents["repository-evolution-agent"])
        agent["input_modalities"] = {"required": ["text", "audio"]}
        provides = dict.fromkeys(required_capabilities(agent), "full")
        resolution = resolve(agent, provides, runtime_id="solo-texto", modalities=("text",))
        self.assertEqual(UNSUPPORTED, resolution.status)
        self.assertIn("modality:audio", resolution.missing)


class RuntimeRegistryTests(unittest.TestCase):
    def test_default_registry_exposes_implemented_runtimes(self):
        registry = default_registry(with_plugins=False)
        self.assertEqual(("claude", "manual"), registry.ids())

    def test_unknown_runtime_fails_instead_of_falling_back(self):
        """Un fallback silencioso podría enviar datos a un proveedor no autorizado."""
        registry = default_registry(with_plugins=False)
        with self.assertRaises(KeyError) as ctx:
            registry.get("codex")
        self.assertIn("codex", str(ctx.exception))

    def test_registering_twice_requires_explicit_replace(self):
        registry = RuntimeRegistry()
        registry.register(ManualRuntime())
        with self.assertRaises(ValueError):
            registry.register(ManualRuntime())
        registry.register(ManualRuntime(), replace=True)
        self.assertEqual(1, len(registry))

    def test_broken_plugin_does_not_break_the_core(self):
        class RotoPunto:
            name = "roto"
            group = ENTRY_POINT_GROUP

            def load(self):
                raise RuntimeError("import fallido")

        registry = default_registry(with_plugins=False)
        with mock.patch("importlib.metadata.entry_points", return_value=[RotoPunto()]):
            load_plugins(registry)
        self.assertEqual(("claude", "manual"), registry.ids())
        self.assertEqual(1, len(registry.plugin_errors))
        self.assertIn("roto", registry.plugin_errors[0])


class RuntimeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog(ROOT)
        cls.agents = agents_by_id(cls.catalog)

    def test_claude_command_is_unchanged(self):
        """Compatibilidad hacia atrás: la invocación es la misma que antes de la capa de runtimes."""
        agent = self.agents["repository-evolution-agent"]
        command = ClaudeCodeRuntime().command(agent, "Analiza este repositorio")
        self.assertEqual(("--agent", "repository-evolution-agent", "--print", "Analiza este repositorio"), command[1:])
        self.assertIn("claude", Path(command[0]).name)

    def test_no_runtime_adds_permission_bypass(self):
        """Ningún adaptador puede ampliar permisos por su cuenta.

        La superficie que invoca procesos es la CLI y los adaptadores; ahí es
        donde un flag de más convertiría la garantía en falsa. El resto del
        paquete solo genera texto, y de hecho cita estos nombres al documentar
        la propia garantía.
        """
        superficie = [ROOT / "src" / "operational_agents" / "cli.py", *(ROOT / "src" / "operational_agents" / "runtimes").glob("*.py")]
        for path in superficie:
            source = path.read_text(encoding="utf-8")
            for forbidden in ("shell=True", "--dangerously-skip-permissions", "bypassPermissions", "--allowedTools"):
                self.assertNotIn(forbidden, source, f"{path.name} contiene {forbidden}")

    def test_resolution_does_not_depend_on_the_environment(self):
        """La matriz debe dar lo mismo en cualquier máquina: resolver no detecta."""
        runtime = NullRuntime(dict.fromkeys(CAPABILITIES, "full"))
        runtime.resolve(self.agents["repository-evolution-agent"])
        self.assertEqual(0, runtime.detect_calls)

    def test_run_refuses_when_a_required_capability_is_missing(self):
        runtime = NullRuntime()
        preparation, result = runtime.run(self.agents["repository-evolution-agent"], "Analiza este repositorio", cwd=ROOT)
        self.assertEqual(UNSUPPORTED, preparation.resolution.status)
        self.assertEqual(runtime_base.BLOCKED, result.status)
        self.assertEqual(1, result.exit_code)
        self.assertEqual(0, runtime.execute_calls, "no debe ejecutarse nada sin capacidades")

    def test_run_stops_before_preparing_when_the_runtime_is_absent(self):
        class Ausente(NullRuntime):
            def detect(self) -> Detection:
                return Detection(False, "no instalado")

        with self.assertRaises(FileNotFoundError):
            Ausente().run(self.agents["repository-evolution-agent"], "Analiza este repositorio", cwd=ROOT)

    def test_run_rejects_a_nonexistent_working_directory(self):
        runtime = NullRuntime(dict.fromkeys(CAPABILITIES, "full"))
        with self.assertRaises(ValueError):
            runtime.run(self.agents["repository-evolution-agent"], "Analiza este repositorio", cwd=ROOT / "no-existe")

    def test_preparation_carries_plan_and_portable_packet(self):
        agent = self.agents["release-governance-agent"]
        preparation = ManualRuntime().prepare(agent, "Prepara el próximo release")
        self.assertEqual(agent["id"], preparation.plan["agent_id"])
        self.assertIn("Task envelope", preparation.prompt)
        self.assertIn('"write": false', preparation.prompt)

    def test_manual_runtime_executes_nothing_and_needs_no_provider(self):
        agent = self.agents["security-remediation-agent"]
        runtime = ManualRuntime()
        self.assertTrue(runtime.detect().available)
        preparation, result = runtime.run(agent, "Revisa los hallazgos del último escaneo", cwd=ROOT)
        self.assertEqual(NOT_EXECUTED, result.status)
        self.assertEqual(0, result.exit_code)
        self.assertEqual(DEGRADED, preparation.resolution.status)
        self.assertIn(agent["mission"], result.artifacts["prompt"])

    def test_runtimes_do_not_mutate_the_agent_contract(self):
        agent = self.agents["repository-evolution-agent"]
        antes = json.dumps(agent, sort_keys=True, ensure_ascii=False)
        for runtime in default_registry(with_plugins=False):
            runtime.prepare(agent, "Analiza este repositorio")
        self.assertEqual(antes, json.dumps(agent, sort_keys=True, ensure_ascii=False))

    def test_every_declared_capability_exists_in_the_model(self):
        for runtime in default_registry(with_plugins=False):
            for item in runtime.capabilities().provides:
                self.assertIn(item, CAPABILITIES, f"{runtime.descriptor.id} declara una capacidad inexistente")

    def test_no_runtime_claims_maturity_without_evidence(self):
        """`INTEGRATED` o superior exige casos en `evidence/`; hoy no hay ninguno."""
        casos = list((ROOT / "evidence" / "case-studies").glob("*.md"))
        for runtime in default_registry(with_plugins=False):
            if not casos:
                self.assertIn(runtime.descriptor.maturity, {"DRAFT", "IMPLEMENTED"}, runtime.descriptor.id)


class CompatibilityMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog(ROOT)

    def test_matrix_covers_every_agent_and_runtime(self):
        data = matrix(self.catalog)
        self.assertEqual(len(self.catalog["agents"]), len(data["agents"]))
        for fila in data["agents"]:
            self.assertEqual({"claude", "manual"}, set(fila["results"]))

    def test_claude_supports_every_agent_and_manual_degrades(self):
        resueltas = resolutions(self.catalog)
        for agent_id, por_runtime in resueltas.items():
            self.assertEqual(SUPPORTED, por_runtime["claude"].status, agent_id)
            self.assertEqual(DEGRADED, por_runtime["manual"].status, agent_id)

    def test_generated_document_matches_the_code(self):
        actual = (ROOT / "docs" / "COMPATIBILITY_MATRIX.md").read_text(encoding="utf-8")
        self.assertEqual(render_compatibility_matrix(self.catalog), actual, "ejecute sync")

    def test_document_does_not_claim_observed_execution(self):
        texto = (ROOT / "docs" / "COMPATIBILITY_MATRIX.md").read_text(encoding="utf-8")
        self.assertIn("no que la ejecución cumpla la misión", texto)


class EvidenceEnvelopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.agents = agents_by_id(load_catalog(ROOT))

    def _envelope(self, task: str = "Investiga la degradación del servicio"):
        agent = self.agents["incident-root-cause-agent"]
        runtime = ManualRuntime()
        preparation, result = runtime.run(agent, task, cwd=ROOT)
        return execution_envelope(
            agent,
            preparation,
            runtime.detect(),
            result,
            runtime_descriptor=runtime.descriptor.as_dict(),
        )

    def test_envelope_has_the_portable_shape(self):
        envelope = self._envelope()
        self.assertEqual(
            {
                "schema_version", "agent", "runtime", "execution", "capabilities",
                "approvals", "evidence", "result", "verification", "residual_risk", "notice",
            },
            set(envelope),
        )

    def test_envelope_records_capability_resolution(self):
        envelope = self._envelope()
        self.assertEqual(DEGRADED, envelope["capabilities"]["status"])
        self.assertIn("filesystem.write", envelope["capabilities"]["blocked"])

    def test_envelope_never_marks_an_approval_as_granted(self):
        for approval in self._envelope()["approvals"]:
            self.assertIsNone(approval["granted"])

    def test_envelope_redacts_secrets(self):
        envelope = self._envelope("Revisa el incidente con token=abc123secreto en los logs")
        blob = json.dumps(envelope, ensure_ascii=False)
        self.assertNotIn("abc123secreto", blob)

    def test_envelope_keeps_local_paths_out_of_the_command(self):
        agent = self.agents["repository-evolution-agent"]
        runtime = ClaudeCodeRuntime()
        preparation = runtime.prepare(agent, "Analiza este repositorio")
        envelope = execution_envelope(
            agent,
            preparation,
            Detection(True, "ruta local"),
            ExecutionResult("COMPLETED", 0, "ok"),
            runtime_descriptor=runtime.descriptor.as_dict(),
        )
        command = envelope["execution"]["command"]
        self.assertNotIn("/", command[0])
        self.assertNotIn("\\", command[0])


class ControlCenterTests(unittest.TestCase):
    """El panel informa de los runtimes; sigue sin ejecutar ninguno."""

    @classmethod
    def setUpClass(cls):
        from operational_agents.server import build_server

        cls.server = build_server(ROOT, "127.0.0.1", 0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def _get(self, path: str):
        with urlopen(f"{self.base}{path}", timeout=5) as response:  # URL construida sobre el loopback de esta misma prueba
            return json.loads(response.read().decode("utf-8"))

    def test_healthz_still_answers(self):
        self.assertEqual({"status": "ok"}, self._get("/healthz"))

    def test_agents_endpoint_is_unchanged(self):
        agents = self._get("/api/agents")["agents"]
        self.assertEqual(13, len(agents))
        self.assertEqual({"id", "name", "description", "status", "category", "risk"}, set(agents[0]))

    def test_runtimes_endpoint_reports_availability(self):
        runtimes = self._get("/api/runtimes")["runtimes"]
        self.assertEqual({"claude", "manual"}, {item["id"] for item in runtimes})
        manual = next(item for item in runtimes if item["id"] == "manual")
        self.assertTrue(manual["available"])
        self.assertEqual("IMPLEMENTED", manual["maturity"])


class OfflineCoreTests(unittest.TestCase):
    """El núcleo debe seguir instalándose y funcionando sin SDK de IA."""

    def test_core_imports_only_the_standard_library(self):
        externos: list[str] = []
        for path in (ROOT / "src" / "operational_agents").rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    externos += [alias.name.split(".")[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    externos.append(node.module.split(".")[0])
        prohibidos = sorted({name for name in externos if name not in sys.stdlib_module_names})
        self.assertEqual([], prohibidos, "el núcleo no puede depender de paquetes externos")

    def test_declared_dependencies_stay_empty(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("dependencies = []", pyproject)

    def test_new_commands_run_without_provider_or_network(self):
        env = dict(
            os.environ,
            PYTHONPATH=str(ROOT / "src"),
            OPERATIONAL_AGENTS_ROOT=str(ROOT),
            PYTHONIOENCODING="utf-8",
            PYTHONUTF8="1",
        )
        env.pop("ANTHROPIC_API_KEY", None)
        env.pop("OPENAI_API_KEY", None)
        comandos = [
            ["runtimes", "--json"],
            ["runtime", "inspect", "manual", "--json"],
            ["capabilities", "--json"],
            ["capabilities", "repository-evolution-agent", "--runtime", "manual", "--json"],
            ["doctor", "--json"],
            ["run", "documentation-coherence-agent", "--runtime", "manual", "--task", "Revisa la coherencia", "--dry-run"],
        ]
        for args in comandos:
            result = subprocess.run(
                [sys.executable, "-m", "operational_agents", *args],
                cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8",
            )
            self.assertEqual(0, result.returncode, f"{args}: {result.stderr}")
            json.loads(result.stdout)

    def test_run_with_claude_runtime_is_still_accepted(self):
        """No se rompe la interfaz previa: `--runtime claude` sigue existiendo."""
        from operational_agents.cli import parser

        args = parser(default_registry(with_plugins=False)).parse_args(
            ["run", "repository-evolution-agent", "--runtime", "claude", "--task", "Analiza este repositorio"]
        )
        self.assertEqual("claude", args.runtime)


if __name__ == "__main__":
    unittest.main()
