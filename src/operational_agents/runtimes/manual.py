
"""Runtime de ejecución humana asistida.

El agente analiza, propone y entrega instrucciones; una persona ejecuta. Es la
modalidad correcta cuando el entorno es producción, infraestructura crítica,
datos sensibles o cualquier sistema regulado donde ninguna herramienta debería
actuar sola.

También es la prueba de que la abstracción sirve: no necesita proveedor, ni
clave API, ni conexión, ni tokens, y aun así recorre el mismo contrato, la
misma resolución de capacidades y la misma evidencia que Claude Code.
"""

from __future__ import annotations

from pathlib import Path

from .base import NOT_EXECUTED, AgentRuntime, Detection, ExecutionResult, Preparation, RuntimeCapabilities, RuntimeDescriptor


class ManualRuntime(AgentRuntime):
    descriptor = RuntimeDescriptor(
        id="manual",
        name="Ejecución humana asistida",
        kind="human",
        summary="Prepara el paquete portable y las verificaciones; la ejecución la realiza una persona.",
        autonomous=False,
        maturity="IMPLEMENTED",
        docs="docs/RUNTIME_CONTRACT.md",
    )

    def capabilities(self) -> RuntimeCapabilities:
        # Todas condicionales: la capacidad existe porque la persona la tiene,
        # no porque el runtime la ejecute. Declararlas `full` sería mentir.
        return RuntimeCapabilities(
            provides={
                "filesystem.read": "conditional",
                "filesystem.find": "conditional",
                "filesystem.search": "conditional",
                "filesystem.write": "conditional",
                "shell.execute": "conditional",
                "network.fetch": "conditional",
                "orchestration.delegate": "conditional",
            },
            modalities=("text", "image", "document", "audio", "video"),
            notes=(
                "Ninguna capacidad se ejecuta de forma automática: todas las realiza una persona.",
                "No carga skills: el conocimiento adicional debe aportarlo quien ejecuta.",
                "El resultado es siempre NOT_EXECUTED; el trabajo lo cierra la persona, no la CLI.",
            ),
        )

    def detect(self) -> Detection:
        return Detection(True, "Disponible siempre: no requiere proveedor, clave ni conexión")

    def execute(self, preparation: Preparation, cwd: Path) -> ExecutionResult:  # noqa: ARG002 - el directorio lo elige quien ejecuta; anotarlo solo filtraría una ruta local a la evidencia
        return ExecutionResult(
            status=NOT_EXECUTED,
            exit_code=0,
            detail="Paquete preparado para ejecución humana; la persona ejecuta, verifica y cierra",
            artifacts={"prompt": preparation.prompt},
        )
