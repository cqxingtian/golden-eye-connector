# GOLDEN-EYE 源巡检连接器 · Railway 部署手册（个人零服务器）

> 这是「路线图」里的 **路线 B**。目标：不用买服务器、不用管运维，让 Railway 自动把代码部署成一个公网 HTTPS 的 MCP 连接器。
> 你只需：① 在 GitHub 网页建个空仓库；② 跑两条命令把代码推上去；③ 在 Railway 网页点几下连仓库。

---

## 我已经帮你做完的部分（你不用动）
- ✅ 代码已按 Railway 要求配好：读取 `PORT` 环境变量、绑 `0.0.0.0`（`mcp_server.py`）。
- ✅ 已加 Railway 启动声明：`Procfile`、`railway.json`、`.gitignore`。
- ✅ 已初始化 Git 仓库并提交（本地，位置 `D:\golden-eye-connector`）。
- ⏳ 你只需把它**推到 GitHub** 再**接 Railway** 即可上线。

---

## 第 1 步：在 GitHub 建一个空仓库（网页操作，纯点击）
1. 浏览器打开 👉 https://github.com/new
2. **Repository name** 填：`golden-eye-connector`（英文名，随便起）
3. 选 **Public**（免费最顺；私有也行但免费额度受限）
4. **不要**勾任何 "Add a README / .gitignore / license"（我们已有文件，避免冲突）
5. 点绿色 **Create repository**
6. 创建后的页面会显示一行地址，形如：
   `https://github.com/你的用户名/golden-eye-connector.git`
   👉 **复制这行地址**（下一步要用）。

---

## 第 2 步：把代码推上去（在你电脑的项目文件夹里执行）
打开"命令提示符"(CMD) 或"终端"，逐行粘贴执行（**把最后一行地址换成你刚复制的**）：

```
cd /d/golden-eye-connector
git remote add origin https://github.com/你的用户名/golden-eye-connector.git
git branch -M main
git push -u origin main
```

> 💡 第一次 `git push` 会**自动弹出浏览器让你登录 GitHub** → 用你的账号登录即可，登录后推送自动完成。
> （这是 Git 自带的登录窗口，不是钓鱼，放心登录。）
>
> 如果没弹窗、提示输入用户名密码：密码处要填 **GitHub 个人访问令牌(PAT)** 而不是账号密码——
> 去 https://github.com/settings/tokens 点 "Generate new token (classic)"，勾 `repo` 权限，生成后粘贴进去。

推送成功后，刷新 GitHub 页面就能看到所有文件。

---

## 第 3 步：Railway 一键部署（网页操作）
1. 浏览器打开 👉 https://railway.com → 点 **Login** 用 **GitHub** 登录
2. 点 **New Project** → 选 **Deploy from GitHub repo**
3. 弹窗里点 **Authorize Railway**（授权它读你的 GitHub 仓库）
4. 在仓库列表里选中 `golden-eye-connector` → 点 **Deploy**
5. Railway 会自动：装依赖 → 启动 `python mcp_server.py` → 显示 **Deployment succeeded**

### 设置访问密码（强烈建议，防别人白嫖你的算力）
部署完成后：
1. 在 Railway 项目里点 **Variables**（变量）
2. 新增一行：`CONNECTOR_API_KEY` = 随便一串你记得住的字符，例如 `ge-yOUR-strong-KEY-2026`
3. 保存，Railway 会自动重启
> ⚠️ 这个密码之后在 WorkBuddy 注册连接器时**要填一模一样的**，记好。

---

## 第 4 步：拿到公网地址
1. 在 Railway 项目里点 **Settings** → **Networking** → **Generate Domain**
   （有的版本在 Project 页直接就有 **Generate Domain** 按钮）
2. 会生成形如：
   `https://golden-eye-connector.up.railway.app`
3. 你的 **MCP 端点**就是：
   `https://golden-eye-connector.up.railway.app/mcp`

✅ 验证在线：浏览器打开上面的 `/mcp` 地址——
看到一段 JSON 或 "Method Not Allowed" 字样就说明服务已起（MCP 不走浏览器直接访问，这样是正常的）。

---

## 第 5 步：发布到 WorkBuddy 变现
打开同目录的 **`PUBLISH-CONNECTOR.md`**，照"逐项填表"把：
- **端点** 填成上面的 `https://xxx.up.railway.app/mcp`
- **鉴权** 填你设的 `CONNECTOR_API_KEY`
- 贴上合规声明
提交即可。设为付费连接器，别人调用就给你分成。

---

## 备用：不想用 GitHub？（Railway CLI 直推，无需 GitHub）
如果你嫌 GitHub 麻烦，也能不用它——直接用 Railway 官方命令行：
1. 安装 Node.js（含 npm）后，命令行执行：`npm install -g railway`
2. 在项目文件夹里执行：
   ```
   railway login
   railway init
   railway up
   ```
   首次 `railway login` 会弹浏览器登录；`railway up` 直接把当前文件夹部署上去，同样给 HTTPS 域名。
（这条路更短，但需要你会装 Node.js / 敲命令，按你喜好选。）

---

## 常见问题
- **Railway 要钱吗？** 新账号有约 $5 免费额度，个人低频探测够用；超额才扣费，可随时删项目止损。
- **部署失败怎么办？** 在 Railway 项目点 **Deployments** → 点某次部署看日志。最常见是依赖装不上（看 `requirements.txt` 是否完整）。
- **改了代码怎么更新？** 本地改完，执行：
  ```
  git add . && git commit -m "update" && git push
  ```
  Railway 会自动重新部署。
- **域名会变吗？** Generate Domain 后一般稳定；删除 Domain 再生成才会变。
- **想关掉/止损？** Railway 项目里 **Settings → Delete Project** 即可，停止计费。
