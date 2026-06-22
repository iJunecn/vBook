# 贝壳易书 · 前端（uni-app / 微信小程序 / PC 网页）

基于 **uni-app (Vue 3 + Vite)** 的前端，**主交付为 H5 网站**（同一套源码可编译为微信小程序）。
UI 组件库为 **wot-design-uni**，状态管理为 **Pinia**，登录支持**邮箱 / 用户名 + 密码**（H5 / 小程序通用），并兼容**微信一键登录**。

## 环境准备
- [Bun](https://bun.sh)（包管理）
- [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)（要跑小程序时再装）

## 安装与运行
```bash
bun install

# H5（当前主交付，可浏览器 + PC 网页访问）
bun run dev:h5
# 浏览器打开 http://localhost:5173

# 微信小程序
bun run dev:mp-weixin
# 然后用「微信开发者工具」导入 dist/dev/mp-weixin

# 构建生产包
bun run build:h5          # dist/build/h5 → Docker 镜像 / 任意静态托管
bun run build:mp-weixin   # dist/build/mp-weixin → 微信开发者工具「上传」
```

## 后端地址（关键）

H5 现在走 **同源代理**，浏览器**永远不会**直接打后端端口。
构建期不再注入 `VITE_API_HOST`，`src/api/config.js` 里默认 `API_BASE = '/api/v1'`。

| 部署方式 | 浏览器看到的后端地址 | 说明 |
| --- | --- | --- |
| Docker H5 容器 | `http://<host>:6628/api/v1`（同源） | nginx 反代，**免 CORS，可从任意 IP 访问** |
| 本地 H5 dev | `http://localhost:5173/api/v1`（同源） | Vite dev server 把 `/api` 转发到后端 |
| 微信小程序 | `http://localhost:6627/api/v1`（直连） | 受小程序「服务器域名」白名单限制 |
| 想直连本机后端 | `VITE_API_HOST=http://localhost:6627` | 仅特殊调试用，写在 `frontend/.env` |

> **生产环境（公网）**：必须把后端放在**已 ICP 备案的 HTTPS 域名**后面，并在小程序后台「服务器域名」加入合法域名。
> H5 本身只要在 6628 上挂个 HTTPS 反代即可，不影响 6627。

## 登录方式

- **邮箱 / 用户名 + 密码**（H5 默认入口）
  - 登录页 → 输入账号（邮箱或用户名）+ 密码 → 登录
  - 「还没账号？立即注册」跳到 `/pages/register/register`
- **微信一键登录**（小程序或后端配了 `WECHAT_APPID`/`WECHAT_SECRET` 时可用）
  - 小程序：`uni.login` → `POST /api/v1/auth/wx-login`
- **注册**：后端 `/api/v1/auth/register` 接 username + email + password（6-64 位），注册成功直接签发 JWT，前端自动登录

## 必要配置
1. **后端地址** — 见上表，**H5 通常不用配**。
2. **AppID** — 填入 [`src/manifest.json`](src/manifest.json) 的 `mp-weixin.appid`（或在开发者工具里填）。
3. **后端微信登录密钥** — 后端 `.env` 配置 `WECHAT_APPID` / `WECHAT_SECRET`（与本小程序一致）。
4. **域名白名单** —
   - 开发：微信开发者工具 → 详情 → 本地设置 → 勾选「不校验合法域名」。
   - 生产：小程序后台 → 开发管理 → 服务器域名，把后端 HTTPS 域名加入 `request` 与 `uploadFile` 合法域名。

## 目录结构
```
src/
├── pages.json          # 路由 + tabBar（首页/卖书/订单/我的）
├── manifest.json       # AppID / 平台配置
├── main.js  App.vue    # 入口（App.vue 含 PC 端顶部导航 + onLaunch 恢复登录态）
├── api/
│   ├── config.js       # 后端地址（默认相对路径，小程序走直连）/ 存储 key
│   ├── request.js      # uni.request + uni.uploadFile 封装（注入 token、401 拦截、网络异常提示）
│   └── index.js        # authApi / bookApi / orderApi
├── store/user.js       # Pinia 用户态（uni.*StorageSync 持久化 + 登录 / 注册 / 微信）
├── components/ListingCard.vue
├── pages/
│   ├── index/index.vue     # 首页：浏览 + 搜索 + 校区筛选 + 分页
│   ├── sell/sell.vue       # 卖书：选图 → AI 识别 → 核对编辑 → 发布
│   ├── listing/detail.vue  # 书单详情：购买 / 卖家管理
│   ├── orders/orders.vue   # 订单：我买的 / 我卖的
│   ├── profile/profile.vue # 我的：资料编辑 + 我的发布
│   ├── login/login.vue     # 邮箱 / 用户名 + 密码登录 + 微信一键登录（小程序）
│   └── register/register.vue   # 邮箱注册
├── utils/format.js     # 价格/时间格式化 + mediaUrl（补全 /uploads 绝对地址）
└── styles/
    ├── theme.scss      # 蓝白主题 CSS 变量
    └── desktop.scss    # PC 端响应式（>= 768px 顶部导航 + 3-4 列网格 + 居中容器）
```

## PC 端适配

打开浏览器宽度 ≥ 768px 时自动启用（详见 `src/styles/desktop.scss`）：

- **顶部 PC 导航**：覆盖 uni-app 自带 navigationBar 与底部 tabBar，导航到 4 个主 tab
- **居中容器**：max-width 1024px / 1200px，内容居中显示
- **多列网格**：首页 / 我的发布 从 2 列变 3 列（≥ 1200px 时变 4 列）
- **字号 / 间距**：核心文本 / 表单 / 按钮统一放大到 PC 比例
- **卡片 hover**：悬浮上浮 + 阴影增强

移动端（< 768px）行为不变，uni-app 自带底部 tabBar 继续生效。

## 登录流程（账号密码 / 微信）

**账号密码**：
1. `login` 页填账号（邮箱或用户名）+ 密码 → `POST /auth/login`。
2. 后端按 `account` 字段自动判别是邮箱还是用户名，查 user 验密 → 签 JWT。
3. 前端存 token + user（`uni.setStorageSync`），后续请求自动带 `Authorization: Bearer`。
4. 「我的」页可编辑昵称/校区/头像（`PATCH /auth/me`）。

**微信一键登录**（仅小程序 / 已配 `WECHAT_APPID` 时可用）：
1. `uni.login` 取临时 `code` → `POST /auth/wechat-login { code }`。
2. 后端用 AppID/Secret 向微信换 `openid`，按 openid 查/建用户并签 JWT。
3. 前端存 token + user，后续请求同账号密码流程。

> 注册接口（`/auth/register`）要求 username + email + password（6-64 位），注册成功直接返回 JWT，前端自动登录。

## 注意
- 上传走 `uni.uploadFile`（`/recognize` 传书脊照片、`/listings/with-image` 传封面 + `books_json`）。
- 后端返回的封面是相对路径 `/uploads/xxx`，前端用 `mediaUrl()` 补全为绝对地址；
  小程序里图片域名同样要满足合法域名要求（生产为 HTTPS）。
- 订单仅创建并标记书已售，**未接入微信支付**（与现有后端一致）。
