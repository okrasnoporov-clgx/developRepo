import json
import os
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer


APP_NAME = os.getenv("APP_NAME", "xxxxx-test-app")
APP_VERSION = os.getenv("APP_VERSION", "v.x.x.x")
PORT = int(os.getenv("PORT", "8000"))


class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/v1/info":
            body = json.dumps(
                {"name": APP_NAME, "version": APP_VERSION}
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
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
    th {{ background: #2457a7; color: white; width: 35%; }}
    tr:nth-child(even) td {{ background: #e7eef8; }}
  </style>
</head>
<body>
  <main>
    <h1>Application info</h1>
    <table>
      <tr><th>Name</th><td>{escape(APP_NAME)}</td></tr>
      <tr><th>Version</th><td>{escape(APP_VERSION)}</td></tr>
    </table>
  </main>
</body>
</html>
"""
        body = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print(f"Starting {APP_NAME} on port {PORT}", flush=True)
    HTTPServer(("0.0.0.0", PORT), AppHandler).serve_forever()
