# GOLDEN-EYE 源巡检连接器（Plan A · 可发布形态）

把 GOLDEN-EYE 的"源健康巡检"能力，包装成一个**标准 MCP Server（Streamable HTTP）**，
可直接注册到 WorkBuddy 开放平台作为**连接器**发布变现。

它只做一件事：**探测你提供的源是否可用**（点播采集接口能否搜到、直播 m3u8 是否可达）。
不存储、不预置任何内容源——被探测的 URL 全部由调用方传入。

> 个人账号在 WorkBuddy 开放平台**只能发布 专家 / 技能 / 连接器**三类；
> 应用（Buddy 应用）需要企业开发者资质，个人无法上架。本连接器（连接器类）个人可直接发布。

## 为什么合规
- 探测是**中立技术动作**（发一个 HTTP 请求看通不通），与所探测内容是否授权无关。
- 不内置任何源池；所有 URL 来自调用方的请求体。
- 对"有合法源"的站长做监控运维完全合规，也不会帮任何人分发未授权内容。

## 两种运行形态
- **`mcp_server.py`（主 · 发布形态）**：MCP Server，端点 `http://<host>:<port>/mcp`。开放平台连接器即接入此端点。
- **`server.py`（备用 · 调试/健康检查）**：零依赖 HTTP REST API（`/health`、`/api/check`、`/api/batch`），便于本地排错。

## 快速运行（MCP 形态）
```bash
cd D:\golden-eye-connector
pip install -r requirements.txt
python mcp_server.py                 # 默认 http://0.0.0.0:8787，端点 /mcp
# 指定端口 / 加 Bearer 鉴权：
PORT=9000 CONNECTOR_API_KEY=sk-xxx python mcp_server.py
```
本地验证（需先装依赖）：`python test_mcp.py`（会自动连 `http://127.0.0.1:8799/mcp` 跑握手+列工具+实际调用）。

## 工具（MCP 暴露）
- `check_source(name, url, kind="auto", keyword="test")` → 单源探测，返回 `status/ms/m3u8/detail`
  - `status`：`GOOD` | `NO_M3U8` | `EMPTY` | `BAD_JSON` | `ERR` | `NOT_PLAYLIST` | `NO_URL`
- `batch_check(items, workers=8)` → 批量探测，返回 `{total, results}`

## 上线两步（详见子文档）
1. **部署**：推荐走 **Railway 零服务器部署** 👉 见 `RAILWAY-DEPLOY.md`（已配好 `Procfile`/`railway.json`，代码已初始化为 Git 仓库，按手册推到 GitHub 即可自动部署拿 HTTPS 域名）。
   也有 Docker 自有云方案 👉 见 `DEPLOY.md`（推荐国内云，探测国内源延迟低）。
2. **发布**：见 `PUBLISH-CONNECTOR.md` —— 在 open.workbuddy.cn「发布管理 → 连接器」逐项填表，
   端点填 `https://你的域名/mcp`、鉴权填对应 `CONNECTOR_API_KEY`，并贴上合规声明；设为付费连接器即可变现。

## 变现路径
- 开放平台「收入变现」设为付费连接器（按调用/订阅计费）；
- 或卖给**已拥有合法源**的站长做"源健康监控 + 故障告警 + 冗余调度"运维服务。

## 文件清单
- `probe.py` 通用探测库（输入驱动，仅标准库，零源池）
- `mcp_server.py` MCP Server（发布形态，端点 /mcp）
- `server.py` 零依赖 HTTP REST API（调试备用）
- `test_mcp.py` 端到端验证脚本
- `requirements.txt` / `Dockerfile` 部署用
- `DEPLOY.md` / `PUBLISH-CONNECTOR.md` 上线指南
- `workbuddy-connector-manifest.json` 注册表单填表参考
