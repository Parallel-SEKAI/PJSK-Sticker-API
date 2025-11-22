# 使用官方Python镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（用于处理图片的库）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
RUN pip install --no-cache-dir uv

# 复制项目代码
COPY . .

# 安装项目依赖
RUN uv sync

# 创建必要的目录
RUN mkdir -p /tmp/pjsk_sticker

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1\
    TZ=Asia/Shanghai

# 暴露API服务端口
EXPOSE 8000

# 启动命令
# CMD ["uv", "run", "api.py"]
CMD ["uv", "run", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
