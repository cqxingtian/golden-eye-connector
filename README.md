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

## 上线方式（详见子文档）

### 主路径：打包上传（平台托管）
open.workbuddy.cn「发布管理 → 连接器 → 发布连接器」**要求上传代码压缩包**（.zip，≤20MB），
平台自动解包解析并生成连接器 ID，**由平台托管运行**。

**必须包含 `connector-meta.json` 且在 zip 根目录**（否则报
`解析失败：未找到 connector-meta.json`），本仓库已提供。

打包命令（在本目录执行，直接取已提交的文件，自动排除 .git / __pycache__ / venv）：
```bash
git archive --format=zip --output=D:\golden-eye-connector-package.zip HEAD
```

### 备用：自有公网端点（Render / Railway）
若你需要一个自己掌控、可常驻的公网 MCP 实例（平台托管之外的备份），可自行部署：
- **Render**（连 GitHub 自动部署）👉 见 `RENDER-DEPLOY.md`
- **Railway** 👉 见 `RAILWAY-DEPLOY.md`（其注册功能曾因事故临时关闭）
- **自有云 Docker** 👉 见 `DEPLOY.md`（推荐国内云，探测国内源延迟低）

> 注：与早期判断不同，WorkBuddy 连接器发布**不是**"提交一个远程 URL"，而是上传代码包。
> 自有部署属于可选的补充，不影响平台发布。

### 发布信息填写
见 `PUBLISH-CONNECTOR.md`：名称、简介、工具说明、合规声明均已写好，可直接复制；
若平台表单要求端点，填 `https://你的域名/mcp`，鉴权密钥填与服务器一致的 `CONNECTOR_API_KEY`；
设为付费连接器即可变现。

## 端点说明
- `/mcp` —— **MCP 协议端点**（发布用）。设了 `CONNECTOR_API_KEY` 时，必须带 `Authorization: Bearer <密钥>`，否则返回 401。
- `/health`、`/` —— **健康检查端点**，**免鉴权**，恒定返回 200（供 Render 等平台探活，避免容器被误杀）。
- 未设 `CONNECTOR_API_KEY` 时全程不鉴权，仅建议本地调试使用。

## 变现路径
- 开放平台「收入变现」设为付费连接器（按调用/订阅计费）；
- 或卖给**已拥有合法源**的站长做"源健康监控 + 故障告警 + 冗余调度"运维服务。

## 文件清单
- `probe.py` 通用探测库（输入驱动，仅标准库，零源池）
- `mcp_server.py` MCP Server（发布形态，端点 /mcp）
- `server.py` 零依赖 HTTP REST API（调试备用）
- `test_mcp.py` 端到端验证脚本
- `requirements.txt` / `Dockerfile` 部署用
- `render.yaml` Render Blueprint（连 GitHub 一键部署）
- `RAILWAY-DEPLOY.md` / `RAILWAY-CLI-CHEATSHEET.md` Railway 路线（备选）
- `DEPLOY.md` / `PUBLISH-CONNECTOR.md` / `RENDER-DEPLOY.md` 上线指南
- `PUBLISH-ROADMAP.md` 非技术用户发布全景路线图
- `workbuddy-connector-manifest.json` 注册表单填表参考
