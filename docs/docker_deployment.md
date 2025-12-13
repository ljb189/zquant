# Docker 部署指南

## 概述

本文档介绍如何使用 Docker 和 Docker Compose 部署 ZQuant 量化分析平台。Docker 部署方案支持：

- ✅ 前后端代码混淆打包
- ✅ 一键部署（包含应用、MySQL、Redis）
- ✅ 生产环境就绪
- ✅ 健康检查和自动重启
- ✅ 数据持久化

## 前置要求

### 系统要求

- **操作系统**: Linux、macOS 或 Windows（支持 WSL2）
- **Docker**: 版本 20.10 或更高
- **Docker Compose**: 版本 2.0 或更高
- **磁盘空间**: 至少 5GB 可用空间
- **内存**: 至少 2GB RAM（推荐 4GB+）

### 检查 Docker 环境

```bash
# 检查 Docker 版本
docker --version

# 检查 Docker Compose 版本
docker-compose --version

# 检查 Docker 服务状态
docker info
```

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yoyoung/zquant.git
cd zquant
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp docker/.env.example docker/.env

# 编辑环境变量文件
# Windows: notepad docker\.env
# Linux/macOS: nano docker/.env
```

**必须配置的项**：

- `SECRET_KEY`: JWT 密钥（必须修改为强密码）
- `DB_PASSWORD`: 数据库密码
- `TUSHARE_TOKEN`: Tushare API Token

生成 SECRET_KEY：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. 构建和启动服务

```bash
# 使用 Docker Compose 一键启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f zquant-app
```

### 4. 初始化数据库（首次部署）

首次部署时，需要初始化数据库：

```bash
# 方法1: 设置环境变量自动初始化
# 在 docker/.env 中设置: INIT_DATABASE=true
# 然后重启服务: docker-compose restart zquant-app

# 方法2: 手动执行初始化脚本
docker-compose exec zquant-app python3 -m zquant.scripts.init_db
docker-compose exec zquant-app python3 -m zquant.scripts.init_scheduler
docker-compose exec zquant-app python3 -m zquant.scripts.init_view
docker-compose exec zquant-app python3 -m zquant.scripts.init_strategies
```

### 5. 访问应用

- **前端界面**: http://localhost
- **API 文档**: http://localhost/docs
- **健康检查**: http://localhost/health

## 详细配置说明

### 环境变量配置

环境变量文件位于 `docker/.env`，主要配置项说明：

#### 数据库配置

```env
DB_HOST=mysql          # 数据库主机（Docker Compose 服务名）
DB_PORT=3306           # 数据库端口
DB_USER=root           # 数据库用户名
DB_PASSWORD=your_password  # 数据库密码（必须修改）
DB_NAME=zquant         # 数据库名称
```

#### Redis 配置

```env
REDIS_HOST=redis       # Redis 主机（Docker Compose 服务名）
REDIS_PORT=6379        # Redis 端口
REDIS_DB=0             # Redis 数据库编号
# REDIS_PASSWORD=your_redis_password  # Redis 密码（可选）
```

#### 安全配置

```env
SECRET_KEY=your-secret-key  # JWT 密钥（必须修改）
# ENCRYPTION_KEY=your-encryption-key  # 加密密钥（可选）
```

#### 应用配置

```env
WORKERS=1             # 工作进程数（根据 CPU 核心数调整）
LOG_LEVEL=info         # 日志级别：DEBUG, INFO, WARNING, ERROR
INIT_DATABASE=false    # 是否自动初始化数据库
```

### Docker Compose 服务说明

#### zquant-app（应用服务）

- **端口**: 80（HTTP）
- **健康检查**: 每 30 秒检查一次
- **自动重启**: 除非手动停止
- **数据卷**: `./logs:/app/logs`（日志持久化）

#### mysql（数据库服务）

- **端口**: 3306（可自定义）
- **数据持久化**: `mysql_data` 卷
- **字符集**: utf8mb4
- **初始化脚本**: `./docker/mysql-init/`（可选）

#### redis（缓存服务）

- **端口**: 6379（可自定义）
- **数据持久化**: `redis_data` 卷
- **AOF 持久化**: 已启用

## 构建和运行

### 单独构建镜像

```bash
# 构建应用镜像
docker build -t zquant:latest .

# 运行容器（需要先启动 MySQL 和 Redis）
docker run -d \
  --name zquant-app \
  --network zquant-network \
  -p 80:80 \
  --env-file docker/.env \
  zquant:latest
```

### 使用 Docker Compose

```bash
# 构建镜像（不启动）
docker-compose build

# 启动所有服务（后台运行）
docker-compose up -d

# 启动服务（前台运行，查看日志）
docker-compose up

# 停止所有服务
docker-compose down

# 停止服务并删除数据卷（谨慎使用）
docker-compose down -v

# 重启服务
docker-compose restart

# 查看服务日志
docker-compose logs -f [service_name]

# 查看服务状态
docker-compose ps

# 进入容器
docker-compose exec zquant-app bash
```

## 代码混淆说明

### 前端代码混淆

前端代码使用 **Terser** 进行混淆和压缩：

- **工具**: UmiJS 内置 Terser
- **配置位置**: `web/config/config.ts`
- **混淆内容**:
  - 移除 `console` 语句
  - 移除 `debugger` 语句
  - 混淆变量名和函数名
  - 压缩代码体积

**验证混淆**：

```bash
# 查看构建产物
docker-compose exec zquant-app ls -la /app/web/dist/

# 查看混淆后的 JS 文件
docker-compose exec zquant-app head -n 20 /app/web/dist/umi.*.js
```

### 后端代码混淆

后端代码使用 **PyArmor** 进行混淆：

- **工具**: PyArmor 8.5.7
- **混淆模式**: `--restrict`（增强安全性）
- **排除文件**:
  - 测试文件（`tests/`）
  - 数据库迁移（`alembic/`）
  - 初始化脚本（`scripts/init_*.py`）

**验证混淆**：

```bash
# 查看混淆后的代码
docker-compose exec zquant-app ls -la /app/zquant/

# 查看混淆后的 Python 文件（应该是加密的字节码）
docker-compose exec zquant-app file /app/zquant/api/v1/auth.py
```

## 数据管理

### 备份数据

```bash
# 备份 MySQL 数据
docker-compose exec mysql mysqldump -u root -p zquant > backup.sql

# 备份 Redis 数据
docker-compose exec redis redis-cli --rdb /data/dump.rdb
docker cp zquant-redis:/data/dump.rdb ./redis-backup.rdb
```

### 恢复数据

```bash
# 恢复 MySQL 数据
docker-compose exec -T mysql mysql -u root -p zquant < backup.sql

# 恢复 Redis 数据
docker cp ./redis-backup.rdb zquant-redis:/data/dump.rdb
docker-compose restart redis
```

### 清理数据

```bash
# 停止服务并删除数据卷（会删除所有数据）
docker-compose down -v

# 仅删除 MySQL 数据
docker volume rm zquant-cursor_mysql_data

# 仅删除 Redis 数据
docker volume rm zquant-cursor_redis_data
```

## 监控和日志

### 查看日志

```bash
# 查看应用日志
docker-compose logs -f zquant-app

# 查看 MySQL 日志
docker-compose logs -f mysql

# 查看 Redis 日志
docker-compose logs -f redis

# 查看所有服务日志
docker-compose logs -f
```

### 健康检查

```bash
# 检查应用健康状态
curl http://localhost/health

# 检查容器健康状态
docker-compose ps

# 查看容器详细信息
docker inspect zquant-app
```

### 性能监控

```bash
# 查看容器资源使用情况
docker stats

# 查看特定容器的资源使用
docker stats zquant-app
```

## 常见问题

### 1. 容器启动失败

**问题**: 容器无法启动或立即退出

**解决方案**:

```bash
# 查看详细日志
docker-compose logs zquant-app

# 检查环境变量配置
docker-compose config

# 检查端口占用
netstat -tulpn | grep :80

# 检查磁盘空间
df -h
```

### 2. 数据库连接失败

**问题**: 应用无法连接到数据库

**解决方案**:

```bash
# 检查 MySQL 服务状态
docker-compose ps mysql

# 检查 MySQL 日志
docker-compose logs mysql

# 测试数据库连接
docker-compose exec mysql mysql -u root -p

# 检查网络连接
docker-compose exec zquant-app ping mysql
```

### 3. Redis 连接失败

**问题**: 应用无法连接到 Redis

**解决方案**:

```bash
# 检查 Redis 服务状态
docker-compose ps redis

# 测试 Redis 连接
docker-compose exec redis redis-cli ping

# 检查 Redis 密码配置
docker-compose exec redis redis-cli -a your_password ping
```

### 4. 前端页面无法访问

**问题**: 浏览器无法打开前端页面

**解决方案**:

```bash
# 检查 Nginx 配置
docker-compose exec zquant-app nginx -t

# 检查前端文件是否存在
docker-compose exec zquant-app ls -la /app/web/dist/

# 检查端口映射
docker-compose ps zquant-app
```

### 5. 代码混淆失败

**问题**: 构建时混淆失败

**解决方案**:

```bash
# 查看构建日志
docker-compose build --no-cache zquant-app

# 检查 PyArmor 版本
docker-compose run --rm zquant-app python3 -c "import pyarmor; print(pyarmor.__version__)"

# 手动测试混淆
docker-compose run --rm zquant-app pyarmor gen --help
```

## 生产环境部署建议

### 1. 安全配置

- ✅ 修改所有默认密码
- ✅ 使用强密码（至少 32 位）
- ✅ 启用 Redis 密码认证
- ✅ 配置防火墙规则
- ✅ 使用 HTTPS（配置反向代理）

### 2. 性能优化

- ✅ 根据服务器配置调整 `WORKERS` 数量
- ✅ 配置数据库连接池大小
- ✅ 启用 Redis 缓存
- ✅ 配置 Nginx 缓存策略

### 3. 监控和告警

- ✅ 配置日志收集（如 ELK、Loki）
- ✅ 配置监控告警（如 Prometheus、Grafana）
- ✅ 定期备份数据
- ✅ 设置自动重启策略

### 4. 高可用部署

- ✅ 使用 Docker Swarm 或 Kubernetes
- ✅ 配置负载均衡
- ✅ 数据库主从复制
- ✅ Redis 集群模式

## 更新和升级

### 更新应用

```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose build zquant-app

# 重启服务
docker-compose up -d zquant-app
```

### 升级数据库

```bash
# 备份数据
docker-compose exec mysql mysqldump -u root -p zquant > backup.sql

# 更新 MySQL 镜像版本（修改 docker-compose.yml）
# 重启服务
docker-compose up -d mysql
```

## 相关文档

- [README.md](../README.md) - 项目主文档
- [数据库初始化指南](database_init.md) - 数据库初始化说明
- [API 访问指南](../API_ACCESS.md) - API 访问配置

## 技术支持

如遇到问题，请通过以下方式获取帮助：

- 📧 **邮箱**: kevin@vip.qq.com
- 💬 **微信**: zquant2025
- 🐛 **问题反馈**: [GitHub Issues](https://github.com/yoyoung/zquant/issues)
- 📚 **文档网站**: [GitHub README](https://github.com/yoyoung/zquant/blob/main/README.md)
