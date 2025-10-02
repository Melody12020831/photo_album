# .

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```

---

一键启动（推荐）

1. 确保已安装 Docker 和 Docker Compose。
2. 在项目根目录（photo_album 文件夹）下，运行以下命令启动所有服务：

```sh
docker-compose up --build
```

- 这会自动构建并启动后端（Django）、前端（Vite）、数据库（MySQL）三个服务。
- 前端开发环境默认端口为：http://localhost:5173
- 后端 API 默认端口为：http://localhost:8000
- MySQL 数据库端口为：3307（主机访问）

3. 关闭服务

按下 Ctrl+C 停止服务，然后执行：

```sh
docker-compose down
```

---