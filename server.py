# -*- coding: utf-8 -*-
"""
GOLDEN-EYE 源巡检连接器 · 零依赖 HTTP API 服务。

端点：
  GET  /health           健康检查
  POST /api/check        {"name","url","kind?","keyword?"}  -> 单源探测
  POST /api/batch        {"items":[...], "workers?"}        -> 批量探测

认证：默认无（仅监听 127.0.0.1）。设环境变量 CONNECTOR_API_KEY 后，
      客户端需在 Header 带  Authorization: Bearer <key>。

合规：本服务不存储、不预置任何内容源；被探测的 URL 全部由调用方提供。
      它只是一个"源健康探测"技术工具，与所探测内容是否授权无关。
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from probe import probe_one, probe_batch

PORT = int(os.environ.get("PORT", "8787"))
API_KEY = os.environ.get("CONNECTOR_API_KEY", "").strip()
HOST = os.environ.get("HOST", "127.0.0.1")


def _denied(handler):
    handler.send_response(401)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.end_headers()
    handler.wfile.write(json.dumps({"error": "unauthorized"}).encode("utf-8"))


def _ok(handler, obj, code=200):
    body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
    handler.end_headers()
    handler.wfile.write(body)


class H(BaseHTTPRequestHandler):
    def _body(self):
        length = int(self.headers.get("Content-Length", "0") or "0")
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return {}

    def _auth_ok(self):
        if not API_KEY:
            return True
        auth = self.headers.get("Authorization", "")
        return auth == "Bearer " + API_KEY or auth == API_KEY

    def do_OPTIONS(self):
        _ok(self, {})

    def do_GET(self):
        if not self._auth_ok():
            return _denied(self)
        if self.path.split("?")[0] == "/health":
            return _ok(self, {"ok": True, "service": "golden-eye-connector", "version": "1.0.0"})
        _ok(self, {"error": "not found"}, 404)

    def do_POST(self):
        if not self._auth_ok():
            return _denied(self)
        path = self.path.split("?")[0]
        data = self._body()
        if path == "/api/check":
            _ok(self, probe_one(data))
        elif path == "/api/batch":
            items = data.get("items") or []
            workers = int(data.get("workers", 8))
            _ok(self, {"total": len(items), "results": probe_batch(items, workers)})
        else:
            _ok(self, {"error": "not found"}, 404)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print("GOLDEN-EYE 源巡检连接器监听 http://%s:%d" % (HOST, PORT))
    ThreadingHTTPServer((HOST, PORT), H).serve_forever()
