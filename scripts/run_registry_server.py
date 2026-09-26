#!/usr/bin/env python3
"""Serve the prototype apps and the durable registry API on one origin."""

from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.registry import ProposalRegistry, ProposalValidationError

DATABASE = ROOT / "data" / "generated" / "registry.sqlite3"
GEOJSON = ROOT / "data" / "generated" / "demo_volumes.geojson"


class Handler(SimpleHTTPRequestHandler):
    registry: ProposalRegistry

    def _json(self, status: int, value: dict) -> None:
        body = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
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
        path = unquote(urlparse(self.path).path)
        if path.startswith("/api/parcels/") and path.endswith("/model"):
            parent_ulpin = path.removeprefix("/api/parcels/").removesuffix("/model")
            try:
                model = self.registry.parcel_model(parent_ulpin)
                self._json(200, model) if model else self._json(404, {"error": "ULPIN not found"})
            except ProposalValidationError as error:
                self._json(422, {"error": str(error)})
            return
        if path.startswith("/api/proposals/") and path.endswith("/audit"):
            proposal_id = path.removeprefix("/api/proposals/").removesuffix("/audit")
            if self.registry.get(proposal_id) is None:
                self._json(404, {"error": "proposal not found"})
            else:
                self._json(200, self.registry.audit(proposal_id))
            return
        if path.startswith("/api/proposals/"):
            record = self.registry.get(path.removeprefix("/api/proposals/"))
            self._json(200, record) if record else self._json(404, {"error": "proposal not found"})
            return
        super().do_GET()

    def do_POST(self) -> None:
        path = unquote(urlparse(self.path).path)
        try:
            if path == "/api/proposals":
                self._json(201, self.registry.submit(self._body()))
                return
            if path.startswith("/api/proposals/") and path.endswith("/decision"):
                proposal_id = path.removeprefix("/api/proposals/").removesuffix("/decision")
                body = self._body()
                self._json(200, self.registry.decide(
                    proposal_id, body.get("decision", ""), body.get("officer", ""), body.get("override_reason", "")
                ))
                return
            self._json(404, {"error": "API route not found"})
        except KeyError:
            self._json(404, {"error": "proposal not found"})
        except ProposalValidationError as error:
            self._json(422, {"error": str(error)})


def main() -> None:
    if not GEOJSON.exists():
        raise SystemExit("Run `python3 scripts/build_demo.py` first.")
    Handler.registry = ProposalRegistry(DATABASE, GEOJSON)
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("Registry API and apps: http://127.0.0.1:8000/apps/intake/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nRegistry server stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
