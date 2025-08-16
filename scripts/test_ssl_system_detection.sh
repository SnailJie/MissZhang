#!/bin/bash

# 测试 SSL 脚本的系统检测逻辑
# 无需 root 权限

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🧪 测试 SSL 脚本系统检测逻辑"
echo "=============================="

# 检测操作系统
echo -e "${BLUE}🔍 检测操作系统...${NC}"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
    ID=$ID
    ID_LIKE=$ID_LIKE
else
    OS=$(uname -s)
    VER=$(uname -r)
    ID="unknown"
    ID_LIKE="unknown"
fi

echo "操作系统名称: $OS"
echo "版本: $VER"
echo "系统 ID: $ID"
echo "系统类型: $ID_LIKE"

echo ""
echo -e "${BLUE}🔍 测试系统类型判断...${NC}"

# 测试 Ubuntu/Debian 检测
if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]] || [[ "$ID" == "ubuntu" ]] || [[ "$ID" == "debian" ]]; then
    echo -e "${GREEN}✅ 检测到 Ubuntu/Debian 系统${NC}"
    SYSTEM_TYPE="ubuntu_debian"
elif [[ "$ID" == "alinux" ]] || [[ "$OS" == *"Alibaba Cloud Linux"* ]]; then
    echo -e "${GREEN}✅ 检测到阿里云 Linux 系统${NC}"
    SYSTEM_TYPE="alinux"
elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"Rocky"* ]] || [[ "$OS" == *"Alma"* ]] || \
     [[ "$ID" == "centos" ]] || [[ "$ID" == "rhel" ]] || [[ "$ID" == "rocky" ]] || [[ "$ID" == "almalinux" ]] || \
     [[ "$ID_LIKE" == *"rhel"* ]] || [[ "$ID_LIKE" == *"centos"* ]]; then
    echo -e "${GREEN}✅ 检测到 CentOS/RHEL 兼容系统${NC}"
    SYSTEM_TYPE="centos_rhel"
else
    echo -e "${YELLOW}⚠️  检测到其他系统${NC}"
    SYSTEM_TYPE="other"
fi

echo ""
echo -e "${BLUE}🔍 测试包管理器检测...${NC}"

# 检测包管理器
if command -v dnf &> /dev/null; then
    echo -e "${GREEN}✅ 检测到 dnf 包管理器${NC}"
    PKG_MANAGER="dnf"
elif command -v yum &> /dev/null; then
    echo -e "${GREEN}✅ 检测到 yum 包管理器${NC}"
    PKG_MANAGER="yum"
elif command -v apt &> /dev/null; then
    echo -e "${GREEN}✅ 检测到 apt 包管理器${NC}"
    PKG_MANAGER="apt"
else
    echo -e "${RED}❌ 未检测到支持的包管理器${NC}"
    PKG_MANAGER="none"
fi

echo ""
echo -e "${BLUE}🔍 测试 certbot 安装命令...${NC}"

# 模拟 certbot 安装命令
case $SYSTEM_TYPE in
    "ubuntu_debian")
        echo "将执行: apt update && apt install -y certbot python3-certbot-nginx python3-certbot-apache"
        ;;
    "alinux")
        echo -e "${BLUE}🔧 阿里云 Linux 系统专用建议:${NC}"
        echo "建议使用专用修复脚本: sudo bash scripts/fix_alinux_certbot.sh"
        echo "或者尝试标准安装:"
        if [ "$PKG_MANAGER" = "dnf" ]; then
            echo "将执行: dnf install -y certbot python3-certbot-nginx python3-certbot-apache"
        else
            echo "将执行: yum install -y certbot python3-certbot-nginx python3-certbot-apache"
        fi
        ;;
    "centos_rhel")
        if [ "$PKG_MANAGER" = "dnf" ]; then
            echo "将执行: dnf install -y certbot python3-certbot-nginx python3-certbot-apache"
        else
            echo "将执行: yum install -y certbot python3-certbot-nginx python3-certbot-apache"
        fi
        ;;
    "other")
        if command -v snap &> /dev/null; then
            echo "将执行: snap install --classic certbot"
        else
            echo -e "${RED}❌ 无法自动安装 certbot${NC}"
        fi
        ;;
esac

echo ""
echo -e "${BLUE}🔍 系统兼容性总结...${NC}"

if [ "$SYSTEM_TYPE" = "ubuntu_debian" ]; then
    echo -e "${GREEN}✅ 完全兼容 Ubuntu/Debian 系统${NC}"
elif [ "$SYSTEM_TYPE" = "centos_rhel" ]; then
    echo -e "${GREEN}✅ 完全兼容 CentOS/RHEL 系统${NC}"
    if [ "$ID" = "alinux" ]; then
        echo -e "${GREEN}✅ 特别支持阿里云 Linux 系统${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  系统兼容性有限${NC}"
fi

echo ""
echo -e "${BLUE}💡 建议:${NC}"
if [ "$SYSTEM_TYPE" = "centos_rhel" ] && [ "$ID" = "alinux" ]; then
    echo "推荐使用: sudo bash scripts/fix_alinux_dns.sh"
elif [ "$SYSTEM_TYPE" = "centos_rhel" ]; then
    echo "推荐使用: sudo bash scripts/fix_centos_dns.sh"
elif [ "$SYSTEM_TYPE" = "ubuntu_debian" ]; then
    echo "系统已支持，可直接运行: sudo bash scripts/ssl_setup.sh"
else
    echo "建议手动安装 certbot: https://certbot.eff.org/"
fi

echo ""
echo -e "${BLUE}📚 相关脚本:${NC}"
echo "- 阿里云 Linux 修复: bash scripts/fix_alinux_dns.sh"
echo "- CentOS/RHEL 修复: bash scripts/fix_centos_dns.sh"
echo "- 系统检测测试: bash scripts/test_system_detection.sh"
echo "- SSL 配置: sudo bash scripts/ssl_setup.sh"

# 阿里云系统特殊提示
if [ "$SYSTEM_TYPE" = "alinux" ]; then
    echo ""
    echo -e "${BLUE}🔧 阿里云 Linux 系统特殊提示:${NC}"
    echo "- DNS 工具修复: sudo bash scripts/fix_alinux_dns.sh"
    echo "- certbot 修复: sudo bash scripts/fix_alinux_certbot.sh"
    echo "- 快速修复选择器: bash scripts/quick_fix_selector.sh"
    echo "- 查看 SSL 配置指南: docs/ssl-setup-guide.md"
fi
