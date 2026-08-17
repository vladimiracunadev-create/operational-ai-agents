
from __future__ import annotations

import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .catalog import agents_by_id, load_catalog
from .planner import create_plan
from .runtimes.registry import default_registry


class ControlHandler(SimpleHTTPRequestHandler):
    root: Path
    web_dir: Path

    def translate_path(self, path: str) -> str:
        clean = urlparse(path).path.lstrip("/") or "index.html"
        candidate = (self.web_dir / clean).resolve()
        if self.web_dir not in candidate.parents and candidate != self.web_dir:
            return str(self.web_dir / "index.html")
        return str(candidate)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/healthz":
            self._json(200, {"status": "ok"})
            return
        if parsed.path == "/api/agents":
            catalog = load_catalog(self.root)
            agents = [{k: a[k] for k in ("id", "name", "description", "status", "category", "risk")} for a in catalog["agents"]]
            self._json(200, {"agents": agents})
            return
        if parsed.path == "/api/runtimes":
            # Solo lectura, como el resto del panel: informa qué runtimes hay
            # registrados y si están disponibles aquí. No ejecuta ninguno.
            registry = default_registry()
            self._json(200, {"runtimes": [
                {**runtime.descriptor.as_dict(), "available": runtime.detect().available}
                for runtime in registry
            ]})
            return
        if parsed.path.startswith("/api/agents/"):
            aid = parsed.path.rsplit("/", 1)[-1]
            agent = agents_by_id(load_catalog(self.root)).get(aid)
            self._json(200 if agent else 404, agent or {"error": "agent_not_found"})
            return
        super().do_GET()

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/plan":
            self._json(404, {"error": "not_found"})
            return
        try:
            length = min(int(self.headers.get("Content-Length", "0")), 131072)
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            agent = agents_by_id(load_catalog(self.root))[payload["agent_id"]]
            self._json(200, create_plan(agent, payload["task"], payload.get("target")))
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            self._json(400, {"error": str(exc)})

    def _json(self, status: int, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        return


def build_server(root: Path, host: str, port: int) -> ThreadingHTTPServer:
    """Servidor configurado y enlazado, sin atender todavía.

    Existe separado de `serve` para poder probar los endpoints sin bloquear:
    la comprobación de loopback ocurre aquí, antes de abrir el socket.
    """
    loopback = host in {"127.0.0.1", "localhost", "::1"}
    if not loopback and os.environ.get("OPERATIONAL_AGENTS_ALLOW_REMOTE_BIND") != "1":
        raise ValueError("Por seguridad use loopback o declare OPERATIONAL_AGENTS_ALLOW_REMOTE_BIND=1")
    handler = type("ConfiguredControlHandler", (ControlHandler,), {"root": root, "web_dir": root / "control-center" / "web"})
    return ThreadingHTTPServer((host, port), handler)


def serve(root: Path, host: str, port: int) -> None:
    server = build_server(root, host, port)
    print(f"Control center: http://{host}:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
