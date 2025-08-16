#!/bin/bash

# SSL Nginx 配置部署脚本
# 适用于阿里云 OS 系统

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔐 SSL Nginx 配置部署脚本"
echo "=========================="

# 检查是否以 root 权限运行
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ 此脚本需要 root 权限${NC}"
    echo "请使用: sudo bash scripts/deploy_ssl_nginx.sh"
    exit 1
fi

# 检查 Nginx 是否安装
if ! command -v nginx &> /dev/null; then
    echo -e "${RED}❌ Nginx 未安装${NC}"
    echo "请先安装 Nginx: yum install nginx -y"
    exit 1
fi

# 检查 SSL 证书是否存在
SSL_CERT="/etc/letsencrypt/live/wuyinxinghai.cn/fullchain.pem"
SSL_KEY="/etc/letsencrypt/live/wuyinxinghai.cn/privkey.pem"

if [ ! -f "$SSL_CERT" ] || [ ! -f "$SSL_KEY" ]; then
    echo -e "${RED}❌ SSL 证书文件不存在${NC}"
    echo "请先运行: certbot --nginx -d wuyinxinghai.cn -d www.wuyinxinghai.cn"
    echo "或者检查证书路径: $SSL_CERT"
    exit 1
fi

echo -e "${GREEN}✅ SSL 证书文件检查通过${NC}"

# 备份当前 Nginx 配置
echo -e "${BLUE}📋 备份当前 Nginx 配置...${NC}"
BACKUP_DIR="/etc/nginx/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -f "/etc/nginx/nginx.conf" ]; then
    cp /etc/nginx/nginx.conf "$BACKUP_DIR/"
    echo -e "${GREEN}✅ 已备份: /etc/nginx/nginx.conf${NC}"
fi

if [ -d "/etc/nginx/conf.d" ]; then
    cp -r /etc/nginx/conf.d "$BACKUP_DIR/"
    echo -e "${GREEN}✅ 已备份: /etc/nginx/conf.d${NC}"
fi

# 复制新的 Nginx 配置
echo -e "${BLUE}📋 复制新的 Nginx 配置...${NC}"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 复制配置文件
if [ -f "$PROJECT_DIR/nginx.conf" ]; then
    cp "$PROJECT_DIR/nginx.conf" /etc/nginx/conf.d/wuyinxinghai.cn.conf
    echo -e "${GREEN}✅ 已复制配置文件到: /etc/nginx/conf.d/wuyinxinghai.cn.conf${NC}"
else
    echo -e "${RED}❌ 项目目录中未找到 nginx.conf 文件${NC}"
    exit 1
fi

# 检查 Nginx 配置语法
echo -e "${BLUE}🔍 检查 Nginx 配置语法...${NC}"
if nginx -t; then
    echo -e "${GREEN}✅ Nginx 配置语法检查通过${NC}"
else
    echo -e "${RED}❌ Nginx 配置语法错误${NC}"
    echo "正在恢复备份配置..."
    cp "$BACKUP_DIR/nginx.conf" /etc/nginx/nginx.conf 2>/dev/null || true
    echo "请检查配置文件并重新运行脚本"
    exit 1
fi

# 重启 Nginx 服务
echo -e "${BLUE}🔄 重启 Nginx 服务...${NC}"
if systemctl restart nginx; then
    echo -e "${GREEN}✅ Nginx 服务重启成功${NC}"
else
    echo -e "${RED}❌ Nginx 服务重启失败${NC}"
    echo "正在恢复备份配置..."
    cp "$BACKUP_DIR/nginx.conf" /etc/nginx/nginx.conf 2>/dev/null || true
    systemctl restart nginx
    exit 1
fi

# 检查 Nginx 服务状态
echo -e "${BLUE}🔍 检查 Nginx 服务状态...${NC}"
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx 服务正在运行${NC}"
else
    echo -e "${RED}❌ Nginx 服务未运行${NC}"
    exit 1
fi

# 检查端口监听状态
echo -e "${BLUE}🔍 检查端口监听状态...${NC}"
if netstat -tlnp | grep -q ":80 "; then
    echo -e "${GREEN}✅ HTTP 端口 80 正在监听${NC}"
else
    echo -e "${YELLOW}⚠️  HTTP 端口 80 未监听${NC}"
fi

if netstat -tlnp | grep -q ":443 "; then
    echo -e "${GREEN}✅ HTTPS 端口 443 正在监听${NC}"
else
    echo -e "${RED}❌ HTTPS 端口 443 未监听${NC}"
fi

# 测试 SSL 连接
echo -e "${BLUE}🔍 测试 SSL 连接...${NC}"
if command -v openssl &> /dev/null; then
    echo | openssl s_client -connect wuyinxinghai.cn:443 -servername wuyinxinghai.cn 2>/dev/null | grep -q "Verify return code: 0 (ok)"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ SSL 证书验证通过${NC}"
    else
        echo -e "${YELLOW}⚠️  SSL 证书验证失败${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  未安装 openssl，跳过 SSL 测试${NC}"
fi

echo ""
echo -e "${GREEN}🎉 SSL Nginx 配置部署完成！${NC}"
echo ""
echo "📋 部署摘要："
echo "• 配置文件: /etc/nginx/conf.d/wuyinxinghai.cn.conf"
echo "• 备份目录: $BACKUP_DIR"
echo "• HTTP 重定向: 80 → 443"
echo "• SSL 证书: $SSL_CERT"
echo ""
echo "🌐 测试链接："
echo "• HTTP:  http://wuyinxinghai.cn"
echo "• HTTPS: https://wuyinxinghai.cn"
echo ""
echo "📝 注意事项："
echo "• 证书将在 90 天后过期，请设置自动续期"
echo "• 建议运行: crontab -e 添加自动续期任务"
echo "• 自动续期命令: certbot renew --quiet"
echo ""
echo "🔧 常用命令："
echo "• 查看 Nginx 状态: systemctl status nginx"
echo "• 查看 Nginx 日志: tail -f /var/log/nginx/error.log"
echo "• 重新加载配置: nginx -s reload"
echo "• 测试配置: nginx -t"
