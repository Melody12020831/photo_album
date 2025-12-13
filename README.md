# 照片相册系统 - 部署指南

## 系统简介

这是一个基于 Django + Vue.js 的智能照片管理系统，具有以下功能：
- 照片上传和管理
- AI智能分析和标签
- 多维度搜索和筛选
- 照片轮播和批量操作
- EXIF信息提取

---

## 快速开始

### 前置要求

1. **安装 Docker 和 Docker Compose**

- Windows: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Mac: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Linux: 

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

2. **获取豆包AI API密钥**（用于AI分析功能）

- 访问：https://console.volcengine.com/ark
- 注册/登录账号
- 进入"模型推理"→"接入管理"→"密钥管理"
- 创建新密钥并复制保存

---

## 部署步骤

### 下载项目

```bash
# 使用Git克隆（如果你有Git）
git clone https://github.com/Melody12020831/photo_album.git
cd photo_album

# 或者直接下载ZIP包并解压
```

### 导入镜像和数据库

```shell
# 导入镜像
docker load -i backend.tar
docker load -i frontend.tar
docker load -i db.tar

# 导入数据库（启动数据库容器后）
docker cp photo_album_db.sql photo_album_db:/photo_album_db.sql
docker exec -it photo_album_db bash
mysql -uuser -ppassword photo_album_db < /photo_album_db.sql
```

### 启动应用

在项目根目录执行：

```bash
docker-compose up --build
```

首次启动需要下载镜像和构建，大约需要 5-10 分钟。

**查看启动日志：**
```bash
docker-compose logs -f
```

按 `Ctrl+C` 退出日志查看（不会停止容器）

### 初始化数据库

等待所有容器启动后，执行数据库迁移：

```bash
# 进入后端容器
docker-compose exec backend bash

# 执行迁移
python manage.py migrate

# 创建管理员账号（可选）
python manage.py createsuperuser

# 退出容器
exit
```

### 访问应用

- **前端界面**：http://localhost:5173
- **后端API**：http://localhost:8000
- **MySQL 数据库端口为**：3307（主机访问）

---

## 常用命令

### 启动服务

```bash
docker-compose up --build
```

### 停止服务

```bash
docker-compose down
```

### 查看运行状态

```bash
docker-compose ps
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 重启服务

```bash
docker-compose restart
```

### 重启前端

```bash
docker-compose restart frontend
```

### 重新构建并启动

```bash
docker-compose up -d --build
```

---

## 常见问题

### Q1: 启动后无法访问前端页面？

**解决方案：**

1. 检查容器是否都在运行：`docker-compose ps`
2. 查看前端日志：`docker-compose logs frontend`
3. 确保端口5173没有被其他程序占用
4. 等待1-2分钟，Vite开发服务器需要时间编译

### Q2: AI分析功能报错"AI服务配置错误"？

**可能原因：**

1. `.env` 文件中的 `DOUBAO_API_KEY` 未设置或错误
2. Docker没有读取到环境变量

**解决方案：**

1. 检查 `.env` 文件是否存在且配置正确
2. 重启Docker容器：

```bash
docker-compose down
docker-compose up -d
```

### Q3: 上传的图片无法显示？

**解决方案：**

1. 确保 `backend/media/photos/` 目录有写入权限
2. 检查后端日志：`docker-compose logs backend`
3. 清除浏览器缓存

### Q4: 数据库连接失败？

**解决方案：**

1. 确保MySQL容器正在运行：`docker-compose ps`
2. 等待30秒让MySQL完全启动
3. 检查 `.env` 文件中的数据库配置
4. 重启所有服务：

```bash
docker-compose down
docker-compose up -d
```

### Q5: 端口被占用怎么办？

**修改端口：**

编辑 `docker-compose.yml`，修改端口映射：

```yaml
# 前端端口修改示例
frontend:
  ports:
    - "5174:5173"  # 主机使用5174端口

# 后端端口修改示例
backend:
  ports:
    - "8001:8000"  # 主机使用8001端口
```

### Q6：如何使用移动端通过局域网访问？

**第 1 步**：查找电脑的局域网 IP

在你的电脑上打开 PowerShell，运行：

```powershell
ipconfig
```

查找输出中的 无线局域网适配器 WLAN 或 以太网适配器 Ethernet 下的 IPv4 地址，例如 `10.162.219.188`

常见的 IP 地址格式：

- `192.168.1.x`
- `192.168.0.x`
- `10.0.0.x`

**第 2 步**：确保防火墙允许访问

Windows 防火墙可能会阻止外部访问，需要允许端口：

```powershell
# 以管理员身份运行 PowerShell，然后执行：

# 允许端口 5173（前端）
netsh advfirewall firewall add rule name="Photo Album Frontend" dir=in action=allow protocol=TCP localport=5173
# 允许端口 8000（后端）
netsh advfirewall firewall add rule name="Photo Album Backend" dir=in action=allow protocol=TCP localport=8000
```   

**第 3 步**：使用移动设备访问

假设你的电脑 IP 是 `10.162.219.188`，在手机浏览器中输入：

**前端地址**：

```
http://10.162.219.188:5173
```

**后端API地址**（一般不需要直接访问）：

```
http://10.162.219.188:8000
```

---

### Q7：手机无法访问

1. **确认同一 WiFi**
2. **检查防火墙设置**
3. **检查 Docker 容器是否运行**

---

## API费用说明

### 豆包AI调用费用

- **本系统使用的模型**：`doubao-1.5-vision-lite-250315`
- **计费方式**：按调用次数计费
- **谁来付费**：使用你自己API密钥的调用，费用计入你的账户
- **如何控制成本**：

1. 合理使用AI分析功能
2. 在豆包控制台设置月度预算
3. 定期检查使用统计

### 费用监控

访问豆包控制台查看：

- 实时调用统计
- 费用明细
- 设置预算告警

---

## 安全建议

1. **保护API密钥**

- ❌ 不要将 `.env` 文件提交到Git
- ❌ 不要在公共场合分享密钥
- ✅ 定期更换API密钥

2. **数据库安全**

- 生产环境请修改默认密码
- 不要将数据库端口暴露到公网

3. **访问控制**

- 设置强密码
- 限制用户注册（如果需要）

---

## 获取帮助

如遇到问题，请：

1. 查看日志：`docker-compose logs -f`
2. 查看本文档的"常见问题"部分
3. 提交Issue：[GitHub Issues](https://github.com/Melody12020831/photo_album/issues)

---

## 开发相关

### 目录结构

```
photo_album/
├── backend/          # Django后端
│   ├── api/         # API应用
│   ├── core/        # 核心配置
│   └── media/       # 上传的文件
├── frontend/        # Vue.js前端
│   ├── src/         # 源代码
│   └── public/      # 静态资源
├── docker-compose.yml
├── .env.example     # 环境变量模板
└── .env            # 实际环境变量（不提交到Git）
```

### 技术栈

- **后端**：Django 4.x + Django REST Framework
- **前端**：Vue 3 + Element Plus + Vite
- **数据库**：MySQL 8.0
- **AI服务**：豆包大模型（通过OpenAI SDK）
- **容器化**：Docker + Docker Compose

---

## 许可证

本项目采用 MIT 许可证

---

**祝使用愉快！** 🎉
