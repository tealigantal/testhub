from __future__ import annotations

import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from .core import evaluate

STATIC_DIR = Path(__file__).resolve().parent / "static"


class Handler(SimpleHTTPRequestHandler):
    """HTTP handler serving static files and evaluation API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self) -> None:  # pragma: no cover - simple delegation
        if self.path in {"", "/"}:
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:
        if self.path != "/api/evaluate":
            self.send_error(404, "Not Found")
            return
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length))
        expression = data.get("expression", "")
        try:
            result = evaluate(expression)
            response, status = {"result": result}, 200
        except Exception as exc:  # noqa: BLE001 - broad for user errors
            response, status = {"error": str(exc)}, 400
        body = json.dumps(response).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def create_server(host: str = "0.0.0.0", port: int = 8000) -> HTTPServer:
    """Create an HTTP server instance."""
    return HTTPServer((host, port), Handler)


def run(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run the HTTP server."""
    httpd = create_server(host, port)
    print(f"Serving on http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:  # pragma: no cover - manual interruption
        pass


if __name__ == "__main__":
    run()
