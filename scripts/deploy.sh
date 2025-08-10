#!/usr/bin/env bash
set -euo pipefail

echo "🚀 开始部署 MissZhang Web应用..."

# 检查是否为root用户（80端口需要root权限）
if [ "$EUID" -ne 0 ]; then
  echo "⚠️  警告: 使用80端口需要root权限"
  echo "请使用: sudo bash deploy.sh"
  exit 1
fi


# 创建应用目录
APP_DIR="/opt/missZhang"
echo "📁 创建应用目录: $APP_DIR"
mkdir -p "$APP_DIR"

# 如果项目文件在当前目录，复制到目标目录
if [ -f "app/main.py" ]; then
    echo "📋 复制项目文件..."
    cp -r . "$APP_DIR/"
else
    echo "⚠️  请确保在项目根目录运行此脚本"
    exit 1
fi

# 设置权限
chown -R root:root "$APP_DIR"
chmod +x "$APP_DIR/scripts/"*.sh

# 切换到应用目录
cd "$APP_DIR"

# 启动应用
echo "🚀 启动应用..."
bash scripts/start.sh

# 配置防火墙
echo "🔥 配置防火墙..."
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp
    echo "✅ UFW防火墙已配置"
elif command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-port=80/tcp
    firewall-cmd --permanent --add-port=443/tcp
    firewall-cmd --reload
    echo "✅ firewalld防火墙已配置"
else
    echo "⚠️  未检测到防火墙，请手动配置"
fi

# 等待应用启动
echo "⏳ 等待应用启动..."
sleep 3

# 健康检查
if curl -f -s "http://127.0.0.1/health" > /dev/null; then
    echo "✅ 应用启动成功!"
    echo "🌐 访问地址: http://$(curl -s ifconfig.me)"
    echo "📊 日志位置: $APP_DIR/logs/"
    echo "🛑 停止命令: cd $APP_DIR && bash scripts/stop.sh"
else
    echo "❌ 应用启动失败，请检查日志: $APP_DIR/logs/gunicorn.error.log"
    exit 1
fi

echo "🎉 部署完成!" 