#!/usr/bin/env bash
set -euo pipefail

echo "🚀 开始部署 MissZhang Web应用 (包含nginx配置)..."

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
  echo "⚠️  警告: 此脚本需要root权限"
  echo "请使用: sudo bash deploy_with_nginx.sh"
  exit 1
fi

# 检查nginx是否安装
if ! command -v nginx &> /dev/null; then
    echo "❌ nginx未安装，请先安装nginx"
    echo "在阿里云OS上可以使用: yum install nginx 或 apt install nginx"
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
    
    # 检查环境配置
    if [ ! -f ".env" ]; then
        echo "⚠️  警告: 未找到 .env 配置文件"
        echo "请配置微信参数后再部署"
        echo "cp env.example .env"
        echo "编辑 .env 文件填入真实的微信配置"
        exit 1
    fi
    
    echo "✅ 环境配置文件检查通过"
else
    echo "⚠️  请确保在项目根目录运行此脚本"
    exit 1
fi

# 设置权限
chown -R root:root "$APP_DIR"
chmod +x "$APP_DIR/scripts/"*.sh

# 配置nginx
echo "🔧 配置nginx..."
NGINX_CONF="/etc/nginx/conf.d/misszhang.conf"

# 备份原配置
if [ -f "$NGINX_CONF" ]; then
    cp "$NGINX_CONF" "${NGINX_CONF}.backup.$(date +%Y%m%d_%H%M%S)"
fi

# 复制nginx配置
cp nginx.conf "$NGINX_CONF"

# 测试nginx配置
echo "🧪 测试nginx配置..."
if nginx -t; then
    echo "✅ nginx配置测试通过"
else
    echo "❌ nginx配置测试失败"
    exit 1
fi

# 重启nginx
echo "🔄 重启nginx..."
systemctl restart nginx
systemctl enable nginx

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
    echo "⚠️  未检测到防火墙，请手动配置80和443端口"
fi

# 切换到应用目录
cd "$APP_DIR"

# 启动应用
echo "🚀 启动应用..."
bash scripts/start.sh

# 等待应用启动
echo "⏳ 等待应用启动..."
sleep 5

# 健康检查
if curl -f -s "http://127.0.0.1:8000/health" > /dev/null; then
    echo "✅ 应用启动成功!"
    echo "🌐 访问地址: http://www.wuyinxinghai.cn"
    echo "📊 应用日志位置: $APP_DIR/logs/"
    echo "📊 nginx日志位置: /var/log/nginx/"
    echo "🛑 停止命令: cd $APP_DIR && bash scripts/stop.sh"
    echo "🔄 重启nginx: systemctl restart nginx"
else
    echo "❌ 应用启动失败，请检查日志: $APP_DIR/logs/gunicorn.error.log"
    exit 1
fi

echo "🎉 部署完成!"
echo ""
echo "📋 部署摘要:"
echo "   - 应用目录: $APP_DIR"
echo "   - nginx配置: $NGINX_CONF"
echo "   - 域名: www.wuyinxinghai.cn"
echo "   - 端口: 80 (nginx) -> 8000 (Flask)"
echo ""
echo "🔍 检查服务状态:"
echo "   - nginx状态: systemctl status nginx"
echo "   - 应用状态: cd $APP_DIR && bash scripts/status.sh"
echo "   - 查看日志: tail -f $APP_DIR/logs/gunicorn.error.log"
