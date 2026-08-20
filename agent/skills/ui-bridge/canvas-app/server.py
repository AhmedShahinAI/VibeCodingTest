#!/usr/bin/env python3
"""
Local dev server for ui-preview/.
Serves static files AND handles POST /save to write canvas-state.json to disk
so the canvas Save button persists layout changes without a file download.

Usage:
  cd ui-preview
  python server.py          # → http://localhost:8765/
  python server.py --port 9000
"""
import argparse, json, os
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, HTTPServer


class CanvasHandler(SimpleHTTPRequestHandler):
    # CORS headers so file:// origins can also POST here
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path == "/save":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body   = self.rfile.read(length)
                data   = json.loads(body)
                out    = Path(__file__).parent / "canvas-state.json"
                out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
                self._json(200, {"ok": True, "bytes": len(body)})
                print(f"  [save] canvas-state.json updated ({len(body):,} bytes)")
            except Exception as exc:
                self._json(500, {"ok": False, "error": str(exc)})
        else:
            self.send_response(404)
            self.end_headers()

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type",   "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        # Suppress successful GETs to keep the terminal clean
        code = args[1] if len(args) > 1 else ""
        if not str(code).startswith("2"):
            super().log_message(fmt, *args)


def main():
    ap = argparse.ArgumentParser(description="Local dev server for ui-preview/")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()

    # Always serve from the directory that contains this script (ui-preview/)
    os.chdir(Path(__file__).parent)

    server = HTTPServer(("", args.port), CanvasHandler)
    print(f"ui-preview server → http://localhost:{args.port}/")
    print(f"POST /save writes canvas-state.json to disk.  Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
