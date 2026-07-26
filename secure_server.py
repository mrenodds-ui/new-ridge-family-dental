"""
secure_server.py — Static file server with HTTP Basic Auth for /forms/*

Usage:
    python secure_server.py --port 7119 --root "./dist"

Any request to /forms/* will require HTTP Basic Auth.
All other paths (SPA routes, assets, API) are served without auth.

The username/password is set in AUTH_USERS below.
"""
import argparse
import base64
import hashlib
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote

# ── Auth config ──────────────────────────────────────────────────
# Format: {"username": "password_hash"}  (sha256 hex for storage)
# To generate: python -c "import hashlib; print(hashlib.sha256(b'your_password').hexdigest())"
AUTH_USERS = {
    "staff": "c7b6b5e8e8b8e8f8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8",  # placeholder
}
AUTH_REALM = "New Ridge Staff Portal"
FORMS_PREFIX = "/forms/"

# ── Generate password hash ───────────────────────────────────────
def _hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _check_auth(headers) -> bool:
    auth = headers.get("Authorization", "")
    if not auth.startswith("Basic "):
        return False
    try:
        creds = base64.b64decode(auth[6:]).decode("utf-8")
        user, pw = creds.split(":", 1)
        expected_hash = AUTH_USERS.get(user)
        return expected_hash is not None and _hash_pw(pw) == expected_hash
    except Exception:
        return False


class AuthHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, root_dir=None, **kwargs):
        self.root_dir = root_dir or os.getcwd()
        super().__init__(*args, directory=self.root_dir, **kwargs)

    def do_GET(self):
        if self.path.startswith(FORMS_PREFIX):
            if not _check_auth(self.headers):
                self.send_response(401)
                self.send_header("WWW-Authenticate", f'Basic realm="{AUTH_REALM}"')
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Authorization required.\n")
                return
        # SPA fallback: serve index.html for non-file routes
        target = os.path.join(self.root_dir, unquote(self.path.lstrip("/")))
        if self.path != "/" and not os.path.exists(target) and not self.path.startswith(("/assets/", "/data/", "/forms/", "/radiographs-static/")):
            self.path = "/index.html"
        super().do_GET()

    def do_HEAD(self):
        if self.path.startswith(FORMS_PREFIX):
            if not _check_auth(self.headers):
                self.send_response(401)
                self.send_header("WWW-Authenticate", f'Basic realm="{AUTH_REALM}"')
                self.end_headers()
                return
        super().do_HEAD()

    def log_message(self, format, *args):
        # Log to stderr with auth status
        msg = format % args
        auth_ok = "AUTH" if FORMS_PREFIX in (getattr(self, "path", "")) else "-"
        sys.stderr.write(f"[{auth_ok}] {msg}\n")


def run_server(port, root):
    os.chdir(root)
    server = HTTPServer(("", port), lambda *a, **k: AuthHandler(*a, root_dir=root, **k))
    print(f"Serving {root} on port {port}")
    print(f"Forms protected at {FORMS_PREFIX} — use Basic Auth")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Static file server with auth for /forms/*")
    parser.add_argument("--port", type=int, default=7119)
    parser.add_argument("--root", default=os.getcwd())
    parser.add_argument("--password", default="ridge2026", help="Set the staff password")
    args = parser.parse_args()

    # Set the password dynamically
    AUTH_USERS["staff"] = _hash_pw(args.password)
    print(f"Staff login: staff / {args.password}")
    run_server(args.port, os.path.abspath(args.root))
