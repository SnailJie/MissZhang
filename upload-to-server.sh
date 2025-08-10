#!/usr/bin/env bash
set -euo pipefail

# 服务器信息
SERVER_IP="172.31.73.92"
SERVER_USER="root"
PROJECT_NAME="missZhang"

echo "🚀 准备上传项目到服务器..."

# 检查当前目录
if [ ! -f "app/main.py" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 创建临时目录
TEMP_DIR="/tmp/${PROJECT_NAME}_$(date +%s)"
echo "📁 创建临时目录: $TEMP_DIR"

# 复制项目文件（排除不需要的文件）
mkdir -p "$TEMP_DIR"
cp -r app "$TEMP_DIR/"
cp -r scripts "$TEMP_DIR/"
cp -r docs "$TEMP_DIR/"
cp gunicorn.conf.py "$TEMP_DIR/"
cp requirements.txt "$TEMP_DIR/"
cp README.md "$TEMP_DIR/"
cp .gitignore "$TEMP_DIR/"

# 创建必要的目录
mkdir -p "$TEMP_DIR/data"
mkdir -p "$TEMP_DIR/logs"
mkdir -p "$TEMP_DIR/run"

# 上传到服务器
echo "📤 上传项目到服务器..."
scp -r "$TEMP_DIR" "${SERVER_USER}@${SERVER_IP}:/opt/${PROJECT_NAME}"

# 清理临时目录
rm -rf "$TEMP_DIR"

echo "✅ 上传完成!"
echo ""
echo "🔗 接下来请执行以下命令:"
echo "ssh ${SERVER_USER}@${SERVER_IP}"
echo "cd /opt/${PROJECT_NAME}"
echo "sudo bash scripts/deploy.sh"
echo ""
echo "🌐 部署完成后访问:"
echo "http://${SERVER_IP}"
echo "http://yourdomain.com (配置域名解析后)" 