# 贝壳易书 (vBook)

> 校园二手书交易平台 — 拍一张书脊照片，AI 自动识别成书单，一键上架。
> **当前阶段：以 H5 网站为主交付物**；同一套 uni-app 源码稍后可直接编译为微信小程序。

[![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)]()
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)]()
[![uni-app](https://img.shields.io/badge/Frontend-uni--app-42b883)]()
[![License](https://img.shields.io/badge/License-MIT-blue)]()

> 🌐 **默认端口**
> - **后端 API**：`6627`（FastAPI，容器内 6627）
> - **H5 网站（用户访问）**：`6628`（Nginx 静态托管，反代 `/api/` 与 `/uploads/` 到后端）
> - **微信小程序**：通过「微信开发者工具」打开 `dist/dev/mp-weixin` 运行，无需端口
> - **H5 本地开发**：Vite 默认 `5173`

---

## 一、项目简介

大学里每到学期末/学期初，校园里都有一摞一摞的二手书待处理：买家看不到清晰信息，卖家难跟进"哪些卖了哪些没卖"，双方都靠聊天群和朋友圈。

**贝壳易书** 的解决方案：

1. **卖家** 把书摞成一摞，露出所有书脊（即书侧面有书名/作者/出版社的一侧），拍一张照片。
2. **AI 识别** — 平台自动调用 OCR + 大模型，识别出每一本书的书名、作者、出版社、ISBN、版次。
3. **大模型导师纠错** — 二次校对识别结果，纠正缩写（如"高数"→"高等数学"）和错字。
4. **卖家一键上架** — 设定每本价格（默认 ¥5），整摞书出现在首页供学弟学妹搜索购买。
5. **买家按书名/作者/出版社搜索** → 直接下单，卖家端那本书自动变灰下架。

> 设计上为「卖家视角」专门优化，但同时也支持「买家」视角（搜索、购买、个人订单）。
>
> **交付路线**：H5 网站（当前）→ 微信小程序（同一份源码，参见 [Roadmap](#十三roadmap)）。

---

## 二、技术栈

### 后端
- **Python 3.11 + FastAPI** — 高性能异步框架
- **SQLAlchemy 2.0 + SQLite** — 默认 SQLite 零依赖；可通过 `DATABASE_URL` 切换到 PostgreSQL/MySQL
- **Pydantic v2** — 数据校验
- **JWT (python-jose) + bcrypt** — 鉴权
- **httpx** — 异步调用第三方 API
- **PaddleOCR (PP-OCRv6)** — 异步 OCR 服务
- **agnes-2.0-flash (OpenAI 兼容接口)** — 大模型结构化 & 纠错

### 前端（uni-app · 一份代码多端发布）
- **uni-app (Vue 3 + Vite)** — 跨端框架，**当前主交付为 H5 网站**，同一份源码可同步编译为微信小程序
- **wot-design-uni** — 小程序友好的 Vue 3 组件库（蓝白主题）
- **Pinia 2** — 状态管理
- **uni.request / uni.uploadFile** — 网络与文件上传（替代 axios）
- 详见 [`frontend/README.md`](frontend/README.md)

### 部署
- **Docker + Docker Compose** — 一键启动（H5 在 6628，后端在 6627；后续小程序直接复用后端 API）

---

## 三、系统框架

```
                        ┌──────────────────────────────┐
                        │  终端用户                     │
                        │                              │
                        │  H5 网站（uni-app）  当前主交付 │
                        │  ─ Docker 部署：http://6628    │
                        │  ─ 本地 dev：http://5173        │
                        │                              │
                        │  微信小程序（uni-app）   后续   │
                        │  ─ 微信开发者工具导入          │
                        │  ─ 直接复用后端 REST API      │
                        └──────────┬───────────────────┘
                                   │  HTTP/HTTPS
                                   ▼
┌──────────────────────────────────────────────────────────┐
│       Docker 主机：docker compose 同时跑两个容器           │
│                                                          │
│   ┌─────────────────────────┐  ┌──────────────────────┐  │
│   │ frontend (nginx:6628)   │  │  backend (uvicorn:6627)│  │
│   │ uni-app H5 静态资源      │  │  FastAPI REST        │  │
│   │  /api/ →  backend:6627  │  │  /api/v1/...         │  │
│   │  /uploads/ → backend:6627│  │  /docs /health       │  │
│   └────────────┬────────────┘  └──────────┬───────────┘  │
│                │                          │              │
│                └──────── docker network ──┘              │
│                                                          │
│  识别流水线 (services/recognition_service.py):            │
│   1. PaddleOCR (PP-OCRv6)   → 原始文本片段               │
│   2. agnes-2.0-flash        → 结构化 JSON 数组           │
│   3. agnes-2.0-flash        → 导师纠错                   │
└──────────────────────┬───────────────────────────────────┘
                       │  HTTPS
                       ▼
        ┌──────────────────────────────┐
        │  PaddleOCR AIStudio API      │
        │  + agnes-2.0-flash API       │
        └──────────────────────────────┘
```

> 关键设计：**H5 和小程序复用同一套后端 API**。后续做小程序时只需新增 `POST /api/v1/auth/wx-login` 换取 openid 签 JWT，前端直接打 6627（或换成已 ICP 备案的 HTTPS 域名）。

---

## 四、功能特性

### 用户
- [x] 账号 / 密码注册登录（当前主流程）
- [x] JWT 鉴权
- [x] 个人资料编辑（昵称、校区、头像）
- [x] 我的上架 / 我的订单
- [ ] 微信小程序一键登录（接入中：见 [Roadmap](#十三roadmap)）

### 卖书
- [x] 拖拽 / 选择上传书脊照片（JPG / PNG / WEBP）
- [x] AI 自动识别出书单（书名、作者、出版社、ISBN、版次）
- [x] 表格内联编辑识别结果（增、删、改、单独定价）
- [x] 批量设价（默认 ¥5/本，可改为任意价）
- [x] 整摞整摞上下架
- [x] 卖家可标记单本书"已售/重新上架"

### 买书
- [x] 首页按时间倒序展示所有上架
- [x] 按书名 / 作者 / 出版社搜索
- [x] 按校区筛选
- [x] 单本购买，下单后自动下架
- [x] 购买 / 销售两套订单视图

### 系统
- [x] CORS 配置（开发 / 生产可切换）
- [x] 静态资源走 Nginx（30 天缓存）
- [x] OpenAPI 文档（`/docs`）
- [x] 健康检查端点 `/health`
- [x] 体积限制：单图 ≤ 20MB
- [x] Docker 一键部署（同时拉起 H5 + 后端两个容器）
- [x] 数据 / 上传文件挂卷，升级不丢数据

---

## 五、目录结构

```
vBook/
├── backend/                       # FastAPI 后端（容器内 6627）
│   ├── app/
│   │   ├── api/                   # 路由：auth / books / orders / deps
│   │   │   ├── auth.py
│   │   │   ├── books.py
│   │   │   ├── orders.py
│   │   │   └── deps.py
│   │   ├── core/                  # 配置、安全
│   │   │   ├── config.py          #   ↑ BACKEND_PORT 默认 6627
│   │   │   └── security.py
│   │   ├── db/                    # SQLAlchemy
│   │   │   └── session.py
│   │   ├── models/                # ORM 模型
│   │   ├── schemas/               # Pydantic 模型
│   │   ├── services/              # 业务：OCR / LLM / 编排
│   │   │   ├── ocr_service.py
│   │   │   ├── llm_service.py
│   │   │   └── recognition_service.py
│   │   ├── utils/                 # 工具
│   │   └── main.py
│   ├── tests/
│   ├── uploads/                   # 用户上传图片
│   ├── data/                      # SQLite 数据
│   ├── requirements.txt
│   └── Dockerfile                 # EXPOSE 6627
├── frontend/                      # uni-app 前端（H5 容器内 6628）
│   ├── src/
│   │   ├── api/                   #   config.js 默认 http://localhost:6627
│   │   ├── pages/                 #   index / sell / listing / orders / profile / login
│   │   ├── store/                 # Pinia
│   │   ├── styles/                # 蓝白主题
│   │   ├── components/
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── pages.json
│   ├── manifest.json
│   ├── vite.config.js
│   ├── package.json
│   ├── .env.example               # VITE_API_HOST=http://localhost:6627
│   ├── Dockerfile.h5              # 多阶段构建：bun 编译 H5 → nginx 监听 6628
│   └── nginx.conf                 # 反代 /api/ 与 /uploads/ 到 backend:6627
├── docker-compose.yml             # backend(6627) + frontend(6628) 同时拉起
├── .env                           # 实际环境变量（已 gitignore）
├── .env.example                   # 环境变量模板
├── .gitignore
├── LICENSE
└── README.md
```

---

## 六、快速开始（Docker）

### 0. 环境要求
- Docker ≥ 20.10
- Docker Compose v2（`docker compose` 命令）

### 1. 配置环境变量
仓库根目录复制 `.env.example` 为 `.env`，然后填入真实密钥：

```bash
cp .env.example .env
# 编辑 .env，至少需要填：
#   AGNES_API_KEY=sk-xxx
#   PADDLE_OCR_TOKEN=xxx
#   SECRET_KEY=（改成你自己的长随机字符串）
```

`.env` 关键字段（默认值见 `.env.example`）：

| Key | 默认值 | 说明 |
| --- | --- | --- |
| `BACKEND_PORT` | `6627` | 后端容器监听端口 |
| `DATABASE_URL` | `sqlite:////app/data/vbook.db` | 容器内默认；本机开发用 `sqlite:///./data/vbook.db` |
| `CORS_ORIGINS` | `http://localhost:6628,http://127.0.0.1:6628,http://localhost:5173,http://127.0.0.1:5173` | 跨域白名单 |
| `AGNES_BASE_URL` | `https://agnes-ai.com` | OpenAI 兼容 base，可改 |
| `AGNES_MODEL` | `agnes-2.0-flash` | 模型名 |

> ⚠️ 切换为其它大模型服务（OpenAI、DeepSeek、智谱、SiliconFlow 等）只需改 `AGNES_BASE_URL` 和 `AGNES_MODEL`，无需改代码。

### 2. 一键启动（H5 + 后端两个容器）

```bash
docker compose up -d --build
```

启动后两个容器都会就绪：

| 端                          | 地址                                    |
| --------------------------- | --------------------------------------- |
| **H5 网站（用户访问）**     | http://localhost:6628                    |
| **后端 API（直连）**        | http://localhost:6627                    |
| **后端 OpenAPI 文档**       | http://localhost:6627/docs               |
| **后端健康检查**            | http://localhost:6627/health             |
| **H5 内部 → 后端**          | nginx 反代到容器内 `backend:6627`         |

> H5 在 6628 直接对外开放。生产环境建议把 6627/6628 放在 HTTPS 反代之后。

### 3. 停止 / 重启 / 清理

```bash
docker compose down                # 停止并移除容器
docker compose restart             # 重启
docker compose logs -f backend     # 看后端日志
docker compose logs -f frontend    # 看 H5 (nginx) 日志
docker compose down -v             # 警告：会同时删除数据卷
```

---

## 七、本地开发模式

不通过 Docker，直接在主机上跑前后端。

### 后端（端口 6627）
```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 6627
```

### 前端（uni-app · H5 + 小程序）
```bash
cd frontend
bun install

# H5 网站（当前主交付；浏览器打开 http://localhost:5173 ）
bun run dev:h5

# 微信小程序（后续开发）：产物在 dist/dev/mp-weixin
bun run dev:mp-weixin
# 然后用「微信开发者工具」导入该目录，AppID 填你的小程序 AppID
```

后端地址在 [`frontend/src/api/config.js`](frontend/src/api/config.js) 配置（默认 `http://localhost:6627`），也可在 `frontend/.env` 用 `VITE_API_HOST` 覆盖。
H5 本地调试时 Vite 默认 `5173`，但浏览器实际请求会打后端 `6627`（`VITE_API_HOST`）。
微信小程序真机/模拟器调试需在「微信开发者工具 → 详情 → 本地设置」勾选「不校验合法域名」；
正式发布需将后端换成**已 ICP 备案的 HTTPS 域名**并在小程序后台「服务器域名」中配置。
完整说明见 [`frontend/README.md`](frontend/README.md)。

### 测试
```bash
cd backend
pytest tests/    # 包含基本冒烟测试，不依赖外部 API
```

---

## 八、API 概览

完整文档见启动后访问 `/docs`（Swagger UI）。

| 方法   | 路径                                | 鉴权 | 说明 |
| ------ | ----------------------------------- | ---- | ---- |
| POST   | `/api/v1/auth/register`             | 无   | 注册（H5 当前主流程） |
| POST   | `/api/v1/auth/login`                | 无   | 账号密码登录（H5 当前主流程） |
| POST   | `/api/v1/auth/wx-login`             | 无   | 微信小程序 `code` 换 JWT（小程序上线时启用） |
| GET    | `/api/v1/auth/me`                   | 是   | 当前用户 |
| PATCH  | `/api/v1/auth/me`                   | 是   | 更新资料 |
| POST   | `/api/v1/recognize`                 | 是   | 上传书脊照片 → 识别书单（不落库） |
| POST   | `/api/v1/listings/with-image`       | 是   | 一次性提交封面 + 书单 → 上架 |
| GET    | `/api/v1/listings`                  | 无   | 列表（支持 `q` / `campus` / `page` / `page_size`） |
| GET    | `/api/v1/listings/{id}`             | 无   | 详情 |
| DELETE | `/api/v1/listings/{id}`             | 是   | 下架（仅卖家） |
| PATCH  | `/api/v1/books/{id}`                | 是   | 修改某本书（价格、状态等） |
| DELETE | `/api/v1/books/{id}`                | 是   | 删除某本书 |
| GET    | `/api/v1/users/{id}/listings`       | 无   | 某用户的所有上架 |
| POST   | `/api/v1/orders`                    | 是   | 下单购买 |
| GET    | `/api/v1/orders/mine`               | 是   | 我买 + 我卖的 |
| GET    | `/api/v1/orders/sales`              | 是   | 仅我卖的 |

> 所有路径都以 `/api/v1` 开头；H5 部署时直接访问 `http://localhost:6628/api/v1`，后端直连 `http://localhost:6627/api/v1`。

### 识别请求示例

```bash
curl -X POST http://localhost:6627/api/v1/recognize \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@/path/to/books.jpg"
```

返回：
```json
{
  "image_url": "/uploads/xxx.jpg",
  "books": [
    { "title": "高等数学（同济第七版）", "author": "同济大学", "publisher": "高等教育出版社",
      "isbn": "9787040396638", "edition": "第七版", "price": 5.0, "confidence": 0.97, "position": 0 },
    { "title": "线性代数", "author": "...", ... }
  ],
  "raw_text": "...",
  "model": "agnes-2.0-flash"
}
```

---

## 九、识别流水线说明

```
照片上传
   │
   ▼
PaddleOCR  (POST /api/v2/ocr/jobs  →  轮询 GET /api/v2/ocr/jobs/{jobId})
   │  返回: 文本片段 + 坐标 + 置信度
   ▼
agnes-2.0-flash  #1  「结构化」
   │  prompt: 把 OCR 文本片段整理成 JSON 数组 {title, author, publisher, edition, isbn}
   ▼
agnes-2.0-flash  #2  「导师纠错」
   │  prompt: 纠正缩写（如"高数"→"高等数学"）、补全作者/出版社
   ▼
前端表格内联编辑（人最后把关）
   ▼
一键上架
```

如果 LLM 调用失败，自动回退到把每段 OCR 文本当成一本书的最小结构，确保流程不中断。

---

## 十、配置项一览（.env）

| Key | 默认值 | 说明 |
| --- | --- | --- |
| `APP_NAME` | `贝壳易书` | 应用名 |
| `DEBUG` | `true` | 调试模式 |
| `SECRET_KEY` | - | **生产环境必改**，JWT 签名密钥 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` (7 天) | Token 有效期 |
| `BACKEND_PORT` | `6627` | 后端监听端口 |
| `DATABASE_URL` | `sqlite:////app/data/vbook.db` | 数据库连接；可改为 `postgresql+psycopg://...` |
| `CORS_ORIGINS` | 见 `.env.example` | 允许的跨域来源，逗号分隔（默认含 6628/5173） |
| `UPLOAD_DIR` | `/app/uploads` | 上传文件目录 |
| `MAX_UPLOAD_SIZE` | `20971520` (20MB) | 单图最大字节数 |
| `ALLOWED_IMAGE_TYPES` | `image/jpeg,image/png,image/webp,image/jpg` | 允许的 MIME |
| `WECHAT_APPID` / `WECHAT_SECRET` | - | 小程序登录用，未填时 `wx-login` 走调试模式 |
| `AGNES_API_KEY` | - | 大模型 API Key |
| `AGNES_BASE_URL` | `https://agnes-ai.com` | OpenAI 兼容 base |
| `AGNES_MODEL` | `agnes-2.0-flash` | 模型名 |
| `AGNES_TIMEOUT` | `60` | 调用超时（秒） |
| `PADDLE_OCR_URL` | `https://paddleocr.aistudio-app.com/api/v2/ocr/jobs` | OCR 提交 URL |
| `PADDLE_OCR_TOKEN` | - | OCR Token |
| `PADDLE_OCR_MODEL` | `PP-OCRv6` | OCR 模型 |
| `PADDLE_OCR_POLL_INTERVAL` | `1.5` | 轮询间隔（秒） |
| `PADDLE_OCR_MAX_POLLS` | `40` | 最大轮询次数 |

---

## 十一、端口速查

| 角色               | 端口 | 备注 |
| ------------------ | ---- | ---- |
| **H5 用户访问**    | **6628** | 当前主交付物，Nginx 对外 |
| **后端 API**       | **6627** | FastAPI，H5 / 小程序都打这里 |
| **H5 本地开发**    | 5173   | Vite dev server（`bun run dev:h5`） |
| **后端 OpenAPI**   | 6627   | http://localhost:6627/docs |
| **微信小程序**     | -     | 走微信开发者工具，无端口；连后端 `6627`（或 HTTPS 域名） |

> 旧版本曾用 `8000`（后端）和 `8080`（H5）。如本机已占用这些端口，新端口 `6627 / 6628` 不冲突。

---

## 十二、常见问题

**Q1：识别的书名不准确怎么办？**
A：识别完成后表格里直接改。每本书都可以独立修改标题、作者、出版社、ISBN、定价。

**Q2：可以不用大模型只跑 OCR 吗？**
A：可以。把 `AGNES_API_KEY` 留空，系统会自动用 OCR 原文当作每本书的标题，上架流程不中断。

**Q3：能换其它大模型吗？**
A：可以。改 `AGNES_BASE_URL` 和 `AGNES_MODEL` 即可，已用 OpenAI 兼容协议，理论上兼容：
- OpenAI：`https://api.openai.com` + `gpt-4o-mini`
- DeepSeek：`https://api.deepseek.com` + `deepseek-chat`
- 智谱：`https://open.bigmodel.cn/api/paas/v4` + `glm-4-flash`
- SiliconFlow：`https://api.siliconflow.cn` + `Qwen/Qwen2.5-7B-Instruct`

**Q4：数据存哪里？会丢吗？**
A：默认 SQLite 存储在命名卷 `backend_data` 中，升级 / 重启容器都不会丢。生产环境建议改为外部 PostgreSQL 并定时备份。

**Q5：图片存在哪里？**
A：`backend_uploads` 卷。生产建议接入对象存储（S3 / 阿里云 OSS / 腾讯 COS），目前架构已用 `/uploads/` 路径前缀，方便后续替换。

**Q6：H5 跑起来了，但想同时跑小程序怎么搞？**
A：小程序不依赖 nginx 容器，本地直接：
```bash
cd frontend
bun run dev:mp-weixin   # 产物在 dist/dev/mp-weixin
# 用「微信开发者工具」导入该目录，AppID 填你的小程序 AppID
```
后端 API 完全一致（REST + JWT），只是鉴权方式由账号密码换成微信一键登录（`POST /api/v1/auth/wx-login`，需在 `.env` 配置 `WECHAT_APPID` / `WECHAT_SECRET`）。
小程序后台「服务器域名」需把后端 HTTPS 域名加入 `request` / `uploadFile` / `downloadFile` 合法域名（开发期可勾选「不校验合法域名」跳过）。

**Q7：端口 6627 / 6628 已被占用怎么办？**
A：改根目录 `.env` 中的 `BACKEND_PORT` 同步修改：
- `docker-compose.yml` 的 `"6627:6627"` / `"6628:6628"`
- `backend/Dockerfile` 的 `EXPOSE 6627` 与 `CMD` 里的 `--port 6627`
- `frontend/Dockerfile.h5` 的 `EXPOSE 6628`
- `frontend/nginx.conf` 的 `listen 6628;` 与两处 `proxy_pass http://backend:6627`
- `frontend/src/api/config.js` 的 `localhost:6627`
- `README.md` 与 `.env.example` 中所有出现 6627/6628 的地方

---

## 十三、Roadmap

- [ ] **微信小程序**（基于现有 REST API）
  - `POST /api/v1/auth/wx-login`（code → openid → JWT）
  - `.env` 配 `WECHAT_APPID` / `WECHAT_SECRET`
  - 小程序后台「服务器域名」配置后端 HTTPS 域名
- [ ] 站内信 / 卖家联系买家
- [ ] 微信支付集成
- [ ] 卖家认证 + 信用分
- [ ] 多校区独立域（school1.vbook.com, school2.vbook.com）
- [ ] 接入对象存储（S3 / OSS）
- [ ] Redis 缓存 + Celery 异步任务

---

## 十四、许可证

MIT
