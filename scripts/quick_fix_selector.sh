#!/bin/bash

# 快速修复选择脚本
# 帮助用户选择最适合的修复方案

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔧 快速修复选择器"
echo "=================="
echo "此脚本将检测你的系统并推荐最适合的修复方案"
echo ""

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
echo -e "${BLUE}🔍 检测系统类型...${NC}"

# 检测系统类型
if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]] || [[ "$ID" == "ubuntu" ]] || [[ "$ID" == "debian" ]]; then
    SYSTEM_TYPE="ubuntu_debian"
    echo -e "${GREEN}✅ 检测到 Ubuntu/Debian 系统${NC}"
elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"Rocky"* ]] || [[ "$OS" == *"Alma"* ]] || \
     [[ "$ID" == "centos" ]] || [[ "$ID" == "rhel" ]] || [[ "$ID" == "rocky" ]] || [[ "$ID" == "almalinux" ]] || \
     [[ "$ID" == "alinux" ]] || [[ "$ID_LIKE" == *"rhel"* ]] || [[ "$ID_LIKE" == *"centos"* ]]; then
    SYSTEM_TYPE="centos_rhel"
    if [[ "$ID" == "alinux" ]]; then
        echo -e "${GREEN}✅ 检测到阿里云 Linux 系统${NC}"
    else
        echo -e "${GREEN}✅ 检测到 CentOS/RHEL 兼容系统${NC}"
    fi
else
    SYSTEM_TYPE="other"
    echo -e "${YELLOW}⚠️  检测到其他系统${NC}"
fi

# 检测问题类型
echo ""
echo -e "${BLUE}🔍 检测问题类型...${NC}"

DNS_ISSUE=false
CERTBOT_ISSUE=false

# 检查 DNS 工具
if ! command -v dig &> /dev/null && ! command -v host &> /dev/null && ! command -v nslookup &> /dev/null; then
    DNS_ISSUE=true
    echo -e "${RED}❌ 缺少 DNS 查询工具${NC}"
else
    echo -e "${GREEN}✅ DNS 查询工具正常${NC}"
fi

# 检查 certbot
if ! command -v certbot &> /dev/null; then
    CERTBOT_ISSUE=true
    echo -e "${RED}❌ 缺少 certbot${NC}"
else
    echo -e "${GREEN}✅ certbot 已安装${NC}"
fi

echo ""
echo -e "${BLUE}🔍 推荐修复方案...${NC}"

if [ "$SYSTEM_TYPE" = "ubuntu_debian" ]; then
    if [ "$DNS_ISSUE" = true ]; then
        echo -e "${YELLOW}⚠️  Ubuntu/Debian 系统通常不需要额外安装 DNS 工具${NC}"
        echo "建议检查系统配置或手动安装: sudo apt install -y dnsutils"
    fi
    if [ "$CERTBOT_ISSUE" = true ]; then
        echo -e "${YELLOW}⚠️  需要安装 certbot${NC}"
        echo "建议运行: sudo apt update && sudo apt install -y certbot python3-certbot-nginx python3-certbot-apache"
    fi
elif [ "$SYSTEM_TYPE" = "centos_rhel" ]; then
    if [ "$ID" = "alinux" ]; then
        # 阿里云 Linux 系统
        if [ "$DNS_ISSUE" = true ] && [ "$CERTBOT_ISSUE" = true ]; then
            echo -e "${GREEN}💡 推荐方案: 使用阿里云 Linux 专用修复脚本${NC}"
            echo "运行: sudo bash scripts/fix_alinux_dns.sh"
            echo "然后运行: sudo bash scripts/fix_alinux_certbot.sh"
        elif [ "$DNS_ISSUE" = true ]; then
            echo -e "${GREEN}💡 推荐方案: 修复 DNS 工具${NC}"
            echo "运行: sudo bash scripts/fix_alinux_dns.sh"
        elif [ "$CERTBOT_ISSUE" = true ]; then
            echo -e "${GREEN}💡 推荐方案: 修复 certbot 安装${NC}"
            echo "运行: sudo bash scripts/fix_alinux_certbot.sh"
        fi
    else
        # 其他 CentOS/RHEL 兼容系统
        if [ "$DNS_ISSUE" = true ] && [ "$CERTBOT_ISSUE" = true ]; then
            echo -e "${GREEN}💡 推荐方案: 使用 CentOS/RHEL 修复脚本${NC}"
            echo "运行: sudo bash scripts/fix_centos_dns.sh"
        elif [ "$DNS_ISSUE" = true ]; then
            echo -e "${GREEN}💡 推荐方案: 修复 DNS 工具${NC}"
            echo "运行: sudo bash scripts/fix_centos_dns.sh"
        elif [ "$CERTBOT_ISSUE" = true ]; then
            echo -e "${GREEN}💡 推荐方案: 修复 certbot 安装${NC}"
            echo "运行: sudo bash scripts/fix_centos_dns.sh"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  系统兼容性有限${NC}"
    echo "建议手动安装所需工具: https://certbot.eff.org/"
fi

echo ""
echo -e "${BLUE}🔍 一键修复选项...${NC}"

if [ "$SYSTEM_TYPE" = "centos_rhel" ] && [ "$ID" = "alinux" ]; then
    echo -e "${GREEN}🚀 阿里云 Linux 一键修复:${NC}"
    echo "sudo bash scripts/fix_alinux_dns.sh && sudo bash scripts/fix_alinux_certbot.sh"
elif [ "$SYSTEM_TYPE" = "centos_rhel" ]; then
    echo -e "${GREEN}🚀 CentOS/RHEL 一键修复:${NC}"
    echo "sudo bash scripts/fix_centos_dns.sh"
elif [ "$SYSTEM_TYPE" = "ubuntu_debian" ]; then
    echo -e "${GREEN}🚀 Ubuntu/Debian 一键修复:${NC}"
    echo "sudo apt update && sudo apt install -y dnsutils certbot python3-certbot-nginx python3-certbot-apache"
fi

echo ""
echo -e "${BLUE}📚 相关脚本:${NC}"
echo "- 阿里云 Linux DNS 修复: sudo bash scripts/fix_alinux_dns.sh"
echo "- 阿里云 Linux certbot 修复: sudo bash scripts/fix_alinux_certbot.sh"
echo "- CentOS/RHEL 修复: sudo bash scripts/fix_centos_dns.sh"
echo "- 通用安装: sudo bash scripts/install_dns_tools.sh"
echo "- SSL 配置: sudo bash scripts/ssl_setup.sh"
echo ""
echo -e "${BLUE}🔍 测试脚本:${NC}"
echo "- 系统兼容性测试: bash scripts/test_system_detection.sh"
echo "- SSL 系统检测测试: bash scripts/test_ssl_system_detection.sh"
echo "- 快速修复选择器: bash scripts/quick_fix_selector.sh"
