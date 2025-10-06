# backend/Dockerfile
FROM python:3.12-slim

# 设置环境变量，防止 python 写入 .pyc 文件
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 关键步骤：安装 mysqlclient 的编译依赖
RUN rm -rf /etc/apt/sources.list.d/* \
    && echo "deb http://mirrors.aliyun.com/debian stable main contrib non-free" > /etc/apt/sources.list \
    && apt-get update && apt-get install -y \
    pkg-config \
    gcc \
    default-libmysqlclient-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt

COPY . .