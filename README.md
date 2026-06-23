# vBook · 贝壳易书

校园二手书交易平台。卖家拍一张书脊照片 → AI 自动识别书目 → 确认上架；买家可浏览、搜索、按校区筛选并下单购买。

## 技术栈

- **全栈框架**：Astro 5（SSR，`output: 'server'`）+ Node 适配器
- **交互组件**：Vue 3（`@astrojs/vue`，岛屿架构）
- **数据库**：PostgreSQL + Drizzle ORM（`postgres-js` 驱动）
- **认证**：Lucia v3（基于 Session 的认证 + bcryptjs 密码哈希）
- **AI**：`agnes-2.0-flash`（OpenAI 兼容接口）用于书脊 OCR 识别
- **样式**：Tailwind CSS v4

## 环境变量

复制 `.env.example` 为 `.env` 并填入：

```env
DATABASE_URL=postgresql://user:password@localhost:5432/vbook
AGNES_API_KEY=your_api_key_here
AGNES_BASE_URL=https://your-agnes-compatible-endpoint/v1
```

## 快速开始

```bash
# 1. 安装依赖
npm install

# 2. 准备数据库（确保 PostgreSQL 已运行且 vbook 库已创建）
npm run db:generate   # 生成迁移 SQL
npm run db:migrate    # 应用迁移
# 或开发期直接推送 schema：
# npm run db:push

# 3. 启动开发服务器
npm run dev

# 4. 构建与预览
npm run build
npm run preview
```

## 目录结构

```
src/
  middleware.ts                 # 每个请求校验 Session，注入 locals.user / locals.session
  layouts/Layout.astro          # 全局布局 + 导航
  lib/
    db.ts                       # Drizzle 客户端
    schema.ts                   # 数据库 schema
    auth.ts                     # Lucia v3 配置
    ai.ts                       # agnes-2.0-flash 封装（书脊识别）
  components/vue/               # Vue 交互组件（岛屿）
    ImageUploader.vue / RecognitionTable.vue / SellFlow.vue
    SearchBar.vue / CampusFilter.vue / BookGrid.vue / BookCard.vue
    BuyButton.vue / ListingActions.vue
  pages/
    index.astro                 # 浏览与搜索
    sell.astro                  # 上传 + AI 识别 + 上架
    book/[id].astro             # 书籍详情 + 购买
    auth/login.astro · register.astro
    profile/index.astro · listings.astro · orders.astro
    api/                        # 后端接口（recognize / listings / orders / books / auth / profile）
```

## API 一览

| 方法 & 路径 | 鉴权 | 说明 |
| --- | --- | --- |
| `POST /api/recognize` | 是 | 上传图片，AI 识别书脊，返回 `{ books }` |
| `POST /api/listings` | 是 | 事务内创建 listing + books，返回 `{ listingId }` |
| `POST /api/orders` | 是 | 校验在售并下单（事务），返回 `{ orderId }`，已售返回 409 |
| `PATCH /api/books/[id]/status` | 卖家 | 标记已售 / 重新上架 |
| `POST /api/auth/register` | — | 注册并创建 Session |
| `POST /api/auth/login` | — | 登录并创建 Session |
| `POST /api/auth/logout` | — | 退出登录 |
| `POST /api/profile` | 是 | 更新昵称 / 校区 / 头像 |

## 备注

- 校区枚举当前为 `['main', 'north', 'south', 'east']`，可在 `src/lib/schema.ts` 调整后重新生成迁移。
- 下单与上架均使用 Drizzle 事务保证原子性；下单时对书籍行加 `FOR UPDATE` 锁避免超卖。
