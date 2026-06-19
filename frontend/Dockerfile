# ---- 构建阶段 ----
FROM node:20-alpine AS builder

WORKDIR /app

# 利用缓存
COPY package.json ./
RUN npm install --no-audit --no-fund

# 构建
COPY . .
# 容器内构建时不依赖后端代理，但仍设置一个空值即可
ENV VITE_API_BASE=/api/v1
ENV VITE_BACKEND_URL=http://backend:8000
RUN npm run build

# ---- 运行阶段 ----
FROM nginx:1.27-alpine

# 自定义 nginx 配置：把 /api 和 /uploads 反代到后端
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 拷贝构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
