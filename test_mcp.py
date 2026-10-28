# -*- coding: utf-8 -*-
"""端到端验证 MCP 连接器：握手 -> 列工具 -> 调用 check_source / batch_check。"""
import asyncio
import os

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    # 端口/密钥均可由环境变量覆盖，便于测不同环境：
    #   TEST_URL=http://127.0.0.1:8801/mcp TEST_KEY=ge-test-7788 python test_mcp.py
    port = os.environ.get("PORT", "8799")
    base = os.environ.get("TEST_URL", "http://127.0.0.1:%s/mcp" % port)
    api_key = os.environ.get("TEST_KEY", "").strip()
    headers = {"Authorization": "Bearer " + api_key} if api_key else None
    async with streamablehttp_client(base, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("TOOLS:", [t.name for t in tools.tools])

            r1 = await session.call_tool(
                "check_source",
                {"name": "示例点播", "url": "https://example.com/api.php/provide/vod",
                 "kind": "vod_api", "keyword": "test"},
            )
            print("check_source ->", r1.content[0].text if r1.content else r1)

            r2 = await session.call_tool(
                "batch_check",
                {"items": [
                    {"name": "直播A", "url": "https://example.com/tv.m3u", "kind": "m3u8"},
                    {"name": "点播B", "url": "https://example.com/api.php/provide/vod", "kind": "vod_api"},
                ], "workers": 4},
            )
            print("batch_check ->", r2.content[0].text if r2.content else r2)
    print("OK")


if __name__ == "__main__":
    asyncio.run(main())
