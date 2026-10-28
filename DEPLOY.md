# 部署 GOLDEN-EYE 源巡检连接器（拿到公网 MCP 端点）

开放平台发布的连接器需要 **WorkBuddy 服务端能访问到的公网 HTTPS 地址**。
本目录已是一个标准 MCP Server（Streamable HTTP），按下面任一方式部署即可拿到 `https://你的域名/mcp`。

## 方式 A：自有服务器 / 云主机（推荐，国内源延迟最低）

适合你的场景（要探测国内卫视/影视源），把服务放国内云，延迟最低。

1. 在腾讯云轻量应用服务器 / 任意 VPS 上装好 Docker。
2. 把整个 `golden-eye-connector` 目录传上去，构建并运行：
   ```bash
   docker build -t ge-connector .
   docker run -d --restart=always -p 8787:8787 \
     -e CONNECTOR_API_KEY=换成你自己的强随机密钥 \
     --name ge-connector ge-connector
   ```
3. 用 Nginx / Caddy 反代到 `https://你的域名/mcp`，并配置 HTTPS（Let's Encrypt 免费）。
   Caddy 示例（`Caddyfile`）：
   ```
   ge.yourdomain.com {
       reverse_proxy localhost:8787
   }
   ```
   （Caddy 会自动签发 HTTPS 证书。）
4. 验证端点可用：
   ```bash
   curl -i -X POST https://你的域名/mcp \
     -H "Authorization: Bearer 你的密钥" \
     -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
   ```
   返回 `200` 且有 JSON 即正常。

## 方式 B：Railway / Render（海外，零运维，适合先跑通）

1. 把本目录推到 GitHub 仓库（已含 `Dockerfile`、`requirements.txt`）。
2. 在 Railway 或 Render 新建项目 → 连仓库 → 选 Docker 部署。
3. 设置环境变量 `PORT=8787`（平台会自动分配公网 HTTPS 域名）、可选 `CONNECTOR_API_KEY`。
4. 部署完成后得到 `https://xxx.railway.app/mcp` 或 `https://xxx.onrender.com/mcp`。

> 注意：海外节点探测国内源延迟偏高，仅建议用于跑通流程或探测海外源。正式服务用方式 A。

## 重要

- **务必设置 `CONNECTOR_API_KEY`**：否则任何人都能白嫖你的探测服务（探测会对外发请求）。
- 开放平台连接器配置里填写的鉴权密钥，必须和这里的 `CONNECTOR_API_KEY` 一致。
- 服务本身不存任何数据、不内置源池，隐私与合规风险极低。
