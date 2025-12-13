#!/bin/bash
# Copyright 2025 ZQuant Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e

echo "=========================================="
echo "ZQuant 容器启动脚本"
echo "=========================================="

# 等待数据库连接
wait_for_db() {
    echo "等待数据库连接..."
    python3 << EOF
import sys
import time
import os
from urllib.parse import urlparse

# 从环境变量获取数据库连接
database_url = os.getenv('DATABASE_URL', '')
if not database_url:
    print("警告: DATABASE_URL 未设置")
    sys.exit(0)

# 解析数据库连接
parsed = urlparse(database_url)
db_host = parsed.hostname or 'localhost'
db_port = parsed.port or 3306

# 尝试连接数据库
max_attempts = 30
attempt = 0

while attempt < max_attempts:
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((db_host, db_port))
        sock.close()
        if result == 0:
            print(f"数据库连接成功: {db_host}:{db_port}")
            sys.exit(0)
    except Exception as e:
        pass
    
    attempt += 1
    print(f"尝试连接数据库 ({attempt}/{max_attempts})...")
    time.sleep(2)

print("错误: 无法连接到数据库")
sys.exit(1)
EOF
}

# 等待 Redis 连接
wait_for_redis() {
    echo "等待 Redis 连接..."
    python3 << EOF
import sys
import time
import os
from urllib.parse import urlparse

redis_url = os.getenv('REDIS_URL', '')
if not redis_url:
    print("警告: REDIS_URL 未设置，跳过 Redis 检查")
    sys.exit(0)

parsed = urlparse(redis_url)
redis_host = parsed.hostname or 'localhost'
redis_port = parsed.port or 6379

max_attempts = 30
attempt = 0

while attempt < max_attempts:
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((redis_host, redis_port))
        sock.close()
        if result == 0:
            print(f"Redis 连接成功: {redis_host}:{redis_port}")
            sys.exit(0)
    except Exception as e:
        pass
    
    attempt += 1
    print(f"尝试连接 Redis ({attempt}/{max_attempts})...")
    time.sleep(2)

print("错误: 无法连接到 Redis")
sys.exit(1)
EOF
}

# 检查必要的环境变量
check_env() {
    echo "检查环境变量..."
    
    required_vars=("DATABASE_URL" "SECRET_KEY")
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        echo "错误: 缺少必要的环境变量: ${missing_vars[*]}"
        exit 1
    fi
    
    echo "环境变量检查通过"
}

# 初始化数据库（可选）
init_database() {
    if [ "${INIT_DATABASE:-false}" = "true" ]; then
        echo "初始化数据库..."
        cd /app
        python3 -m zquant.scripts.init_db || echo "数据库初始化失败，继续启动..."
    fi
}

# 启动后端服务
start_backend() {
    echo "启动后端服务..."
    cd /app
    
    # 使用 uvicorn 启动 FastAPI 应用
    uvicorn zquant.main:app \
        --host 127.0.0.1 \
        --port 8000 \
        --workers ${WORKERS:-1} \
        --log-level ${LOG_LEVEL:-info} \
        --no-access-log \
        &
    
    BACKEND_PID=$!
    echo "后端服务已启动 (PID: $BACKEND_PID)"
    
    # 等待后端服务就绪
    echo "等待后端服务就绪..."
    for i in {1..30}; do
        if curl -f http://127.0.0.1:8000/health > /dev/null 2>&1; then
            echo "后端服务就绪"
            return 0
        fi
        sleep 1
    done
    
    echo "警告: 后端服务可能未完全就绪"
}

# 主函数
main() {
    check_env
    wait_for_db
    wait_for_redis
    init_database
    start_backend
    
    # 执行传入的命令（通常是启动 Nginx）
    echo "=========================================="
    echo "启动完成，执行命令: $@"
    echo "=========================================="
    
    exec "$@"
}

# 捕获退出信号，清理后台进程
cleanup() {
    if [ ! -z "$BACKEND_PID" ]; then
        echo "停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
    fi
}

trap cleanup EXIT INT TERM

# 运行主函数
main "$@"
