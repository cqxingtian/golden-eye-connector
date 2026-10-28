# Railway CLI 命令清单（免 GitHub · 直接复制）

> 全部在"命令提示符"(CMD) 里逐条粘贴执行。
> 第一次用先在 https://nodejs.org 装好 Node.js（LTS 版，一路 Next）。

```bat
REM 1) 进入项目目录
cd /d/golden-eye-connector

REM 2) 安装 Railway 命令行（只做一次）
npm install -g railway

REM 3) 登录（弹浏览器，用 GitHub 或邮箱注册/登录 Railway）
railway login

REM 4) 建项目并部署
railway init
railway up

REM 5) 设置访问密码（把等号后面换成你自己的字符串，并记住它）
railway variables:set CONNECTOR_API_KEY=ge-your-strong-key-2026

REM 6) 生成公网域名（记下返回的地址）
railway domain
```

部署成功后：
- 端点 = 上面返回的地址 + `/mcp`，例如：
  `https://golden-eye-connector.up.railway.app/mcp`
- 把这个端点 + 你设的 `CONNECTOR_API_KEY` 填进 WorkBuddy「连接器」发布表单（见 `PUBLISH-CONNECTOR.md`）。

改代码后重新上线：
```bat
cd /d/golden-eye-connector
railway up
```
