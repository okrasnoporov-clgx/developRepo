import json
import os
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


APP_NAME = os.getenv("APP_NAME", "beta-test-app")
APP_VERSION = os.getenv("APP_VERSION", "v.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
SVC = os.getenv("SVC", "alpha-test-app")


class AppHandler(BaseHTTPRequestHandler):
    def send_body(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status: int, data: dict[str, str]) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_body(status, body, "application/json; charset=utf-8")

    def do_GET(self) -> None:
        if self.path == "/v1/info":
            self.send_json(200, {"name": APP_NAME, "version": APP_VERSION})
            return

        if self.path == "/v1/alpha/info":
            try:
                with urlopen(
                    f"http://{SVC}:8000/v1/info", timeout=5
                ) as response:
                    body = response.read()
                    status = response.status
                    content_type = response.headers.get(
                        "Content-Type", "application/json"
                    )
            except (HTTPError, URLError, TimeoutError) as error:
                self.log_error(
                    "Failed to read alpha service info from %s: %s", SVC, error
                )
                self.send_json(502, {"error": "Failed to read alpha service info"})
                return

            self.send_body(status, body, content_type)
            return

        if self.path != "/":
            self.send_error(404)
            return

        page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(APP_NAME)}</title>
  <style>
    body {{ background: #f3f6fa; color: #233044; font: 16px system-ui, sans-serif; }}
    main {{ margin: 12vh auto; max-width: 520px; padding: 24px; }}
    h1 {{ color: #2457a7; font-size: 1.5rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #d5deea; padding: 12px 16px; text-align: left; }}
    th {{ background: #7e57c2; color: white; width: 35%; }}
    tr:nth-child(even) td {{ background: #e7eef8; }}
  </style>
</head>
<body>
  <main>
    <h1>Application info</h1>
    <table>
      <tr><th>Name</th><td>{escape(APP_NAME)}</td></tr>
      <tr><th>Version</th><td>{escape(APP_VERSION)}</td></tr>
      <tr><th>SVC</th><td>{escape(SVC)}</td></tr>
    </table>
  </main>
</body>
</html>
"""
        body = page.encode("utf-8")
        self.send_body(200, body, "text/html; charset=utf-8")


if __name__ == "__main__":
    print(f"Starting {APP_NAME} on port {PORT}", flush=True)
    HTTPServer(("0.0.0.0", PORT), AppHandler).serve_forever()
