# GOLDEN-EYE 源巡检连接器 · Railway 部署手册（免 GitHub 版）

> 个人发布连接器需要公网 HTTPS 地址。本手册用 **Railway CLI** 把 `D:\golden-eye-connector` 这个本地文件夹**直接推上去部署**，全程**不需要 GitHub、不需要建仓库、不需要买服务器**。
> 部署完成后你会拿到一个 `https://xxx.up.railway.app/mcp` 的地址，用来在 WorkBuddy 注册变现。

---

## 我已经帮你做完的部分（你不用动）
- ✅ 代码已按 Railway 要求配好：读 `PORT` 环境变量、绑 `0.0.0.0`（`mcp_server.py`）。
- ✅ 已加 Railway 启动声明：`Procfile`、`railway.json`、`.gitignore`（Railway 靠它们知道怎么启动和装依赖）。
- ✅ 已初始化 Git 仓库并提交（本地；用 CLI 路线时这个仓库**用不上**，忽略即可）。

---

## 前置：装一次 Node.js（约 2 分钟，只做一次）
Railway 命令行依赖 Node.js，先装它：
1. 浏览器打开 👉 https://nodejs.org
2. 点 **LTS**（长期支持版，如 20.x 或 22.x）的下载按钮，得到 `.msi` 安装包
3. 双击安装，**一路 Next / 同意**即可（默认会装好 `npm`）
4. 验证：打开"命令提示符"(CMD)，输入以下两条，能看到版本号就成功：
   ```
   node -v
   npm -v
   ```

---

## 主路径：Railway CLI 四步部署（免 GitHub）

> 全部在"命令提示符"(CMD) 里操作。建议先把下面命令复制到记事本，按说明替换后逐条粘贴。

### 第 1 步：进入项目目录
```
cd /d/golden-eye-connector
```

### 第 2 步：安装 Railway 命令行工具（一次性）
```
npm install -g railway
```
> 第一次会下载一会儿，看到 `added ... packages` 之类就成功。

### 第 3 步：登录 Railway
```
railway login
```
> 会自动弹出浏览器 → 用 GitHub 或邮箱注册/登录 Railway（没有就顺手注册一个，免费）。

### 第 4 步：建项目并部署（两条命令，最关键）
```
railway init
railway up
```
- `railway init`：会提示你给项目起名，直接回车用默认或输入 `golden-eye-connector` 都行；它会创建一个新项目并关联到当前文件夹。
- `railway up`：把当前文件夹上传并部署。Railway 会自动读 `requirements.txt` 装依赖、按 `Procfile` 启动 `python mcp_server.py`。
- 看到 **Deployment succeeded / 部署成功** 即完成。

### 第 5 步：设置访问密码（强烈建议，防别人白嫖算力）
```
railway variables:set CONNECTOR_API_KEY=ge-your-strong-key-2026
```
> 把 `ge-your-strong-key-2026` 换成**你自己记得住的一串字符**。设完 Railway 会自动重启。
> ⚠️ 这个密码之后在 WorkBuddy 注册连接器时要填**一模一样**的，记好。

### 第 6 步：生成公网地址
```
railway domain
```
> 会返回形如 `https://golden-eye-connector.up.railway.app` 的地址。
> 你的 **MCP 端点**就是它在后面加 `/mcp`：
> `https://golden-eye-connector.up.railway.app/mcp`

### 第 7 步：验证在线
浏览器打开上面的 `/mcp` 地址 —— 看到一段 JSON 或 "Method Not Allowed" 字样，说明服务已在线（MCP 不走浏览器直接访问，这样是正常的）。

### 第 8 步：发布到 WorkBuddy 变现
打开同目录的 **`PUBLISH-CONNECTOR.md`**，照"逐项填表"把：
- **端点** 填成上面的 `https://xxx.up.railway.app/mcp`
- **鉴权** 填你设的 `CONNECTOR_API_KEY`
- 贴上合规声明
提交即可。设为付费连接器，别人调用就给你分成。

---

## 备用：走 GitHub 仓库部署（如果你更习惯用仓库）
如果你不想用命令行、更想用网页点，可以走 GitHub 路线（需要先建 GitHub 仓库再推代码）。完整步骤见本目录 `GITHUB-DEPLOY.md`（如不存在，沿用旧版步骤：建空仓库 → `git remote add` + `git push` → Railway "Deploy from GitHub repo"）。

---

## 常见问题
- **Railway 要钱吗？** 新账号有约 $5 免费额度，个人低频探测够用；超额才扣费，可随时删项目止损。
- **部署失败？** 命令行会显示日志；最常见是依赖装不上（看 `requirements.txt`）。也可在 railway.com 项目页 **Deployments** 看详细日志。
- **改了代码怎么更新？** 在本地改完，执行 `railway up` 重新部署即可。
- **想关掉/止损？** railway.com 项目里 **Settings → Delete Project** 即可，停止计费。
- **忘记 CONNECTOR_API_KEY？** 在 railway.com 项目 **Variables** 里能看到（值被遮一部分，可改）。

> 想直接复制纯命令版，见同目录 **`RAILWAY-CLI-CHEATSHEET.md`**。
