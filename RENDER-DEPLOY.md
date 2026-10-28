# GOLDEN-EYE 源巡检连接器 · Render 部署手册（纯网页版）

> **这份手册不需要你敲任何命令。** 代码已经推到你的 GitHub 仓库了，
> 你只要在 Render 网页上用 GitHub 登录、点几下，它就会自动把连接器跑起来，
> 给你一个能填进 WorkBuddy 的公网地址。

---

## 开始前：确认代码已在 GitHub

你的仓库（已完成，不用再动）：

```
https://github.com/cqxingtian/golden-eye-connector
```

里面已经包含 Render 需要的全部文件：`Dockerfile`、`requirements.txt`、
`mcp_server.py`、`probe.py`、`render.yaml`。

---

## 第 1 步：注册 / 登录 Render

1. 浏览器打开 👉 **https://render.com**
2. 点右上角 **Get Started**（或 Sign Up）
3. 选择 **Continue with GitHub**（**一定要用 GitHub 登录**，下一步要连仓库）
4. 按提示授权（一路点 Allow / Authorize）

> 免费账号即可，不需要信用卡。

---

## 第 2 步：部署（Blueprint 一键方式）

1. 登录后进入 Dashboard，点右上角 **New +**
2. 选 **Blueprint**
3. 如果第一次用，会让你连 GitHub：点 **Connect account** → 授权
   - 若提示选仓库，选 **Only select repositories** → 勾上 `golden-eye-connector`
4. 仓库列表里会出现 **`cqxingtian/golden-eye-connector`**，点它右边的 **Connect**
5. Render 会读取仓库里的 `render.yaml`，显示服务名 `golden-eye-connector`
6. 点 **Apply**（或 Deploy）

**然后就是等**——首次构建要装 Python 依赖，通常 2～5 分钟。
页面会显示 `Building…` → `Deploying…` → 出现绿色 **Live** 就成功了。

---

## 第 3 步：设置访问密钥（重要）

`render.yaml` 里把密钥设成了 `sync: false`（不写进仓库），
所以部署后必须手动填一次，否则别人能白嫖你的算力。

1. 在服务页面，左侧点 **Environment**
2. 找到 **`CONNECTOR_API_KEY`**，在右边输入一串自定义密钥
   - 建议：随机字符串，例如 `ge-pub-7d2f9c4a1b8e`（自己换一个更保险的）
3. 点 **Save Changes**
4. Render 会自动重启服务（约 1 分钟）

⚠️ **记牢这串密钥**——下一步在 WorkBuddy 注册连接器时要填**一模一样**的。

---

## 第 4 步：拿到公网地址并验证

部署成功后，服务页顶部会显示公网地址，形如：

```
https://golden-eye-connector.onrender.com
```

把它在浏览器地址栏后面加上 `/health` 打开验证：

```
https://golden-eye-connector.onrender.com/health
```

**看到下面这样的返回，就说明成功了：**

```json
{"ok": true, "service": "golden-eye-connector", "mcp_endpoint": "/mcp", "tools": ["check_source", "batch_check"]}
```

---

## 第 5 步：到 WorkBuddy 发布连接器

你的 **MCP 端点地址**就是：

```
https://golden-eye-connector.onrender.com/mcp
```

去 👉 **open.workbuddy.cn → 发布管理 → 连接器**，按 `PUBLISH-CONNECTOR.md`
里写好的文案逐项填写（名称、简介、工具说明、合规声明都现成），
端点填上面这个地址，鉴权密钥填第 3 步那串，设为付费即可上线变现。

---

## ⚠️ 关于免费额度的一个提醒（如实说）

Render **免费档**的 web 服务在 **15 分钟无人访问后会自动休眠**，
再次访问会有 **30～50 秒冷启动**。

- **自用 / 试跑 / 验证流程**：完全够用，免费。
- **正式挂到 WorkBuddy 上收费变现**：建议升级 **Starter 约 $7/月**，
  服务保持常驻在线，用户调用不会遇到冷启动失败。

（付费与否你自己定；先把流程跑通更重要。）

---

## 常见问题

**Q：构建失败怎么办？**
A：点服务页面的 **Logs** 看红色报错。最常见是依赖装不上，
把报错发我，我改 `requirements.txt` 或 `Dockerfile`。

**Q：地址想改个名字？**
A：服务页 **Settings** → `Name` 可改，改完地址跟着变。

**Q：代码以后更新了怎么同步？**
A：`render.yaml` 里已开 `autoDeploy: true`。
以后在这台机器上改完代码、我帮你 push 到 GitHub，
Render 会自动重新部署，不用你管。

**Q：以后还想换回 Railway？**
A：可以，两边配置都在（`railway.json`、`Procfile` 也保留了），
等 Railway 注册恢复后再说，不冲突。
