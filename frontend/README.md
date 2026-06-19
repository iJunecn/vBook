# 贝壳易书 · 前端（uni-app / 微信小程序）

基于 **uni-app (Vue 3 + Vite)** 重构的前端，主投放**微信小程序**，同一套代码可编译 H5。
UI 组件库为 **wot-design-uni**，状态管理为 **Pinia**，登录采用**微信一键登录**。

## 环境准备
- [Bun](https://bun.sh)（包管理）
- [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
- 一个微信小程序 **AppID**（[公众平台](https://mp.weixin.qq.com) 注册）

## 安装与运行
```bash
bun install

# 微信小程序：产物在 dist/dev/mp-weixin
bun run dev:mp-weixin
# 然后用「微信开发者工具」导入该目录，AppID 填你的小程序 AppID

# H5（浏览器快速联调，可选）
bun run dev:h5
```

构建生产包：
```bash
bun run build:mp-weixin   # dist/build/mp-weixin → 微信开发者工具「上传」
bun run build:h5          # dist/build/h5 → 任意静态托管
```

## 必要配置
1. **后端地址** — [`src/api/config.js`](src/api/config.js) 的 `HOST`，默认 `http://localhost:8000`。
   - 模拟器：可用 `localhost`；真机：改成电脑局域网 IP（如 `http://192.168.x.x:8000`）。
   - 生产：必须是**已 ICP 备案的 HTTPS 域名**。
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
├── main.js  App.vue    # 入口（App.vue onLaunch 恢复登录态）
├── api/
│   ├── config.js       # 后端地址 / 存储 key
│   ├── request.js      # uni.request + uni.uploadFile 封装（注入 token、401 拦截）
│   └── index.js        # authApi / bookApi / orderApi
├── store/user.js       # Pinia 用户态（uni.*StorageSync 持久化 + 微信登录）
├── components/ListingCard.vue
├── pages/
│   ├── index/index.vue     # 首页：浏览 + 搜索 + 校区筛选 + 分页
│   ├── sell/sell.vue       # 卖书：选图 → AI 识别 → 核对编辑 → 发布
│   ├── listing/detail.vue  # 书单详情：购买 / 卖家管理
│   ├── orders/orders.vue   # 订单：我买的 / 我卖的
│   ├── profile/profile.vue # 我的：资料编辑 + 我的发布
│   └── login/login.vue     # 微信一键登录
├── utils/format.js     # 价格/时间格式化 + mediaUrl（补全 /uploads 绝对地址）
└── styles/theme.scss   # 蓝白主题 CSS 变量
```

## 登录流程（微信一键登录）
1. `login` 页点按钮 → `uni.login` 取临时 `code`。
2. 调 `POST /auth/wechat-login { code }`，后端用 AppID/Secret 向微信换 `openid`，
   按 openid 查/建用户并签发 JWT。
3. 前端存 token + user（`uni.setStorageSync`），后续请求自动带 `Authorization: Bearer`。
4. 昵称/头像可在「我的」页编辑（`PATCH /auth/me`）。

> 账号密码登录接口（`/auth/login`、`/auth/register`）后端保留作调试，小程序端不暴露。

## 注意
- 上传走 `uni.uploadFile`（`/recognize` 传书脊照片、`/listings/with-image` 传封面 + `books_json`）。
- 后端返回的封面是相对路径 `/uploads/xxx`，前端用 `mediaUrl()` 补全为绝对地址；
  小程序里图片域名同样要满足合法域名要求（生产为 HTTPS）。
- 订单仅创建并标记书已售，**未接入微信支付**（与现有后端一致）。
