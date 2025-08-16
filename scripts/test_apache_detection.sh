#!/bin/bash

# Apache 系统类型检测测试脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔍 Apache 系统类型检测测试"
echo "=========================="

# 检测 Apache 系统类型
echo -e "${BLUE}📁 检测 Apache 配置目录...${NC}"

if [ -d "/etc/apache2/sites-available" ]; then
    APACHE_TYPE="debian"
    echo -e "${GREEN}✅ 检测到 Ubuntu/Debian 风格 Apache${NC}"
    echo "配置目录: /etc/apache2/sites-available"
    echo "配置文件路径: /etc/apache2/sites-available/example.com.conf"
    echo "启用命令: a2ensite"
    echo "重载命令: systemctl reload apache2"
    echo "测试命令: apache2ctl configtest"
elif [ -d "/etc/httpd/conf.d" ]; then
    APACHE_TYPE="rhel"
    echo -e "${GREEN}✅ 检测到 CentOS/RHEL/阿里云风格 Apache${NC}"
    echo "配置目录: /etc/httpd/conf.d"
    echo "配置文件路径: /etc/httpd/conf.d/example.com.conf"
    echo "启用命令: 手动重启 httpd 服务"
    echo "重载命令: systemctl reload httpd"
    echo "测试命令: httpd -t"
else
    echo -e "${YELLOW}⚠️  未检测到标准 Apache 配置目录${NC}"
    echo "可能的原因："
    echo "1. Apache 未安装"
    echo "2. 使用非标准配置目录"
    echo "3. 系统架构特殊"
fi

echo ""
echo -e "${BLUE}🔧 检查 Apache 服务状态...${NC}"

# 检查 Apache 服务
if command -v apache2 &> /dev/null; then
    echo -e "${GREEN}✅ 检测到 apache2 命令${NC}"
    if systemctl is-active --quiet apache2; then
        echo -e "${GREEN}✅ apache2 服务正在运行${NC}"
    else
        echo -e "${YELLOW}⚠️  apache2 服务未运行${NC}"
    fi
elif command -v httpd &> /dev/null; then
    echo -e "${GREEN}✅ 检测到 httpd 命令${NC}"
    if systemctl is-active --quiet httpd; then
        echo -e "${GREEN}✅ httpd 服务正在运行${NC}"
    else
        echo -e "${YELLOW}⚠️  httpd 服务未运行${NC}"
    fi
else
    echo -e "${RED}❌ 未检测到 Apache 命令${NC}"
fi

echo ""
echo -e "${BLUE}📋 系统信息...${NC}"

# 显示系统信息
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "操作系统: $NAME $VERSION_ID"
    echo "系统 ID: $ID"
    echo "系统类型: $ID_LIKE"
else
    echo "操作系统: $(uname -s) $(uname -r)"
fi

echo ""
echo -e "${BLUE}💡 建议...${NC}"

if [ "$APACHE_TYPE" = "debian" ]; then
    echo "✅ 系统完全兼容 SSL 配置脚本"
    echo "可以直接运行: sudo bash scripts/ssl_setup.sh"
elif [ "$APACHE_TYPE" = "rhel" ]; then
    echo "✅ 系统兼容 SSL 配置脚本"
    echo "建议先运行: sudo bash scripts/fix_centos_dns.sh"
    echo "然后运行: sudo bash scripts/ssl_setup.sh"
else
    echo "⚠️  系统兼容性未知"
    echo "建议手动检查 Apache 配置"
fi

echo ""
echo "测试完成！"
