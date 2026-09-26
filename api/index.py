"""Vercel Function adapter for the Bhu-Aadhaar 3D prototype API.

Vercel Functions have an ephemeral writable filesystem, so this deployment uses
/tmp for the demo registry. Production must replace it with managed durable
storage before registrations can be treated as persistent.
"""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.registry import ProposalRegistry, ProposalValidationError


REGISTRY = ProposalRegistry(
    "/tmp/bhu_aadhaar_3d_registry.sqlite3",
    ROOT / "data" / "generated" / "demo_volumes.geojson",
)


class handler(BaseHTTPRequestHandler):
    def _request_path(self) -> str:
        parsed = urlparse(self.path)
        routed = parse_qs(parsed.query).get("path", [""])[0]
        return f"/api/{unquote(routed).lstrip('/')}" if routed else unquote(parsed.path)

    def _json(self, status: int, value: dict) -> None:
        body = json.dumps(value).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Registry-Storage", "ephemeral-vercel-demo")
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 1_000_000:
            raise ProposalValidationError("invalid request size")
        try:
            value = json.loads(self.rfile.read(length))
        except json.JSONDecodeError as error:
            raise ProposalValidationError("invalid JSON") from error
        if not isinstance(value, dict):
            raise ProposalValidationError("JSON body must be an object")
        return value

    def do_GET(self) -> None:
        path = self._request_path()
        if path in {"/api", "/api/"}:
            self._json(200, {
                "service": "Bhu-Aadhaar 3D prototype API",
                "status": "ok",
                "storage": "ephemeral-vercel-demo",
            })
            return
        if path.startswith("/api/parcels/") and path.endswith("/model"):
            parent_ulpin = path.removeprefix("/api/parcels/").removesuffix("/model")
            try:
                model = REGISTRY.parcel_model(parent_ulpin)
                self._json(200, model) if model else self._json(404, {"error": "ULPIN not found"})
            except ProposalValidationError as error:
                self._json(422, {"error": str(error)})
            return
        if path.startswith("/api/proposals/") and path.endswith("/audit"):
            proposal_id = path.removeprefix("/api/proposals/").removesuffix("/audit")
            if REGISTRY.get(proposal_id) is None:
                self._json(404, {"error": "proposal not found"})
            else:
                self._json(200, REGISTRY.audit(proposal_id))
            return
        if path.startswith("/api/proposals/"):
            record = REGISTRY.get(path.removeprefix("/api/proposals/"))
            self._json(200, record) if record else self._json(404, {"error": "proposal not found"})
            return
        self._json(404, {"error": "API route not found"})

    def do_POST(self) -> None:
        path = self._request_path()
        try:
            if path == "/api/proposals":
                self._json(201, REGISTRY.submit(self._body()))
                return
            if path.startswith("/api/proposals/") and path.endswith("/decision"):
                proposal_id = path.removeprefix("/api/proposals/").removesuffix("/decision")
                body = self._body()
                self._json(200, REGISTRY.decide(
                    proposal_id,
                    body.get("decision", ""),
                    body.get("officer", ""),
                    body.get("override_reason", ""),
                ))
                return
            self._json(404, {"error": "API route not found"})
        except KeyError:
            self._json(404, {"error": "proposal not found"})
        except ProposalValidationError as error:
            self._json(422, {"error": str(error)})
