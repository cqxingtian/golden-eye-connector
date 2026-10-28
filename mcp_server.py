# -*- coding: utf-8 -*-
"""
GOLDEN-EYE 源巡检连接器 · MCP Server（Streamable HTTP）

把"源健康巡检"能力暴露为一个 WorkBuddy 连接器（远程 MCP Server）。
WorkBuddy 开放平台发布的连接器本质就是 MCP Server，本文件即发布形态。

暴露工具：
  - check_source : 探测单个视频源是否可用
  - batch_check  : 批量探测多个源

运行：
  PORT=8787 CONNECTOR_API_KEY=sk-xxx python mcp_server.py
默认监听 0.0.0.0:8787，MCP 端点为 http://<host>:<port>/mcp

合规：本服务仅做 HTTP 可达性探测，不提供、不存储任何视频内容；
     被探测的 URL 全部由调用方（用户）提供，探测能力本身与内容是否授权无关。
"""
import json
import os

from mcp.server.fastmcp import FastMCP
from probe import probe_one, probe_batch

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8787"))
API_KEY = os.environ.get("CONNECTOR_API_KEY", "").strip()

mcp = FastMCP("golden-eye-connector", host=HOST, port=PORT)


@mcp.tool()
def check_source(name: str, url: str, kind: str = "auto", keyword: str = "test") -> str:
    """探测单个视频源是否可用。

    本工具仅做 HTTP 可达性探测，不提供、不存储任何视频内容；被探测的 URL 由调用方提供。

    Args:
        name: 源显示名（任意字符串，便于识别）
        url: 待测源地址，必填。点播采集接口形如 https://x.com/api.php/provide/vod；直播为 .m3u8 地址
        kind: 源类型。vod_api=点播采集接口；m3u8=直播/HLS 播放列表；auto=按 URL 自动判断（默认）
        keyword: 仅 vod_api 使用，探测时用来搜索的词，默认 test

    Returns:
        JSON 字符串，含 status / ms(毫秒) / m3u8 或 segments 数量 / detail
        status 取值：GOOD（可用） | NO_M3U8（能搜但无播放地址） | EMPTY（无结果） |
                     BAD_JSON（非预期格式） | ERR（不可达/超时） | NOT_PLAYLIST（返回了网页） | NO_URL（缺地址）
    """
    res = probe_one({"name": name, "url": url, "kind": kind, "keyword": keyword})
    return json.dumps(res, ensure_ascii=False)


@mcp.tool()
def batch_check(items: list, workers: int = 8) -> str:
    """批量探测多个视频源，返回每个源的巡检结果与总览。

    适用于对一组源做日常健康巡检、冗余调度与故障告警。
    建议一次传入你站点维护的全部源，根据返回的 status 决定保留/降级/替换。

    Args:
        items: 源对象列表，每项含 name(可选) / url(必填) / kind(可选) / keyword(可选)
        workers: 并发探测数，默认 8

    Returns:
        JSON 字符串，含 total(总数) 与 results(各源结果数组，结构同 check_source)
    """
    results = probe_batch(items, workers)
    return json.dumps({"total": len(items), "results": results}, ensure_ascii=False)


def _auth_wrapper(app):
    """可选 Bearer 鉴权：设了 CONNECTOR_API_KEY 时，所有请求必须带 Authorization: Bearer <key>。"""
    async def wrapper(scope, receive, send):
        if scope.get("type") == "http" and API_KEY:
            headers = {k.decode().lower(): v.decode() for k, v in (scope.get("headers") or [])}
            auth = headers.get("authorization", "")
            if auth not in ("Bearer " + API_KEY, API_KEY):
                await send({
                    "type": "http.response.start",
                    "status": 401,
                    "headers": [(b"content-type", b"application/json")],
                })
                await send({"type": "http.response.body", "body": b'{"error":"unauthorized"}'})
                return
        await app(scope, receive, send)
    return wrapper


if __name__ == "__main__":
    if API_KEY:
        import uvicorn
        uvicorn.run(_auth_wrapper(mcp.streamable_http_app()), host=HOST, port=PORT)
    else:
        mcp.run(transport="streamable-http")
    print("GOLDEN-EYE 源巡检连接器 (MCP) 已停止")
