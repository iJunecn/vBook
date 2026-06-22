FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      curl \
    && rm -rf /var/lib/apt/lists/*

# Python 依赖（利用 Docker 缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 应用代码
COPY app ./app

# 数据 / 上传目录
RUN mkdir -p /app/data /app/uploads

EXPOSE 6627

# 启动命令（使用 1 worker；开发用 --reload）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "6627"]
