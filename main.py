import json
import mimetypes
import os
import urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).parent
STORAGE_FILE = BASE_DIR / "storage" / "data.json"
TEMPLATES_DIR = BASE_DIR / "templates"

jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


def read_messages() -> dict:
    if not STORAGE_FILE.exists():
        return {}
    with open(STORAGE_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_message(username: str, message: str) -> None:
    messages = read_messages()
    key = str(datetime.now())
    messages[key] = {"username": username, "message": message}
    STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=4, ensure_ascii=False)


class HttpHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self._send_html("index.html")
        elif path == "/message.html":
            self._send_html("message.html")
        elif path == "/style.css":
            self._send_static("style.css", "text/css")
        elif path == "/logo.png":
            self._send_static("logo.png", "image/png")
        elif path == "/read":
            self._send_read_page()
        else:
            self._send_html("error.html", status=404)

    def do_POST(self):
        if self.path == "/message":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = urllib.parse.parse_qs(body)
            username = data.get("username", [""])[0]
            message = data.get("message", [""])[0]
            save_message(username, message)
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self._send_html("error.html", status=404)

    def _send_html(self, filename: str, status: int = 200) -> None:
        filepath = BASE_DIR / filename
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self._send_not_found()

    def _send_static(self, filename: str, content_type: str) -> None:
        filepath = BASE_DIR / filename
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self._send_not_found()

    def _send_read_page(self) -> None:
        messages = read_messages()
        template = jinja_env.get_template("read.html")
        html = template.render(messages=messages)
        content = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_not_found(self) -> None:
        filepath = BASE_DIR / "error.html"
        with open(filepath, "rb") as f:
            content = f.read()
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


if __name__ == "__main__":
    server = HTTPServer(("", 3000), HttpHandler)
    print("Server started at http://localhost:3000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()
