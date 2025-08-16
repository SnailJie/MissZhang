#!/bin/bash

# 阿里云 Linux 系统 certbot 安装修复脚本
# 专门解决 certbot 安装问题

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔧 阿里云 Linux certbot 安装修复"
echo "================================="

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ 错误: 此脚本需要 root 权限${NC}"
    echo "请使用: sudo bash scripts/fix_alinux_certbot.sh"
    exit 1
fi

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

# 检查是否为阿里云 Linux 系统
ALINUX=false
if [[ "$OS" == *"Alibaba Cloud Linux"* ]] || [[ "$ID" == "alinux" ]]; then
    ALINUX=true
    echo -e "${GREEN}✅ 检测到阿里云 Linux 系统${NC}"
else
    echo -e "${YELLOW}⚠️  此脚本专为阿里云 Linux 系统设计${NC}"
    echo "当前系统: $OS"
    echo "建议使用通用脚本: sudo bash scripts/fix_centos_dns.sh"
    exit 1
fi

echo ""
echo -e "${BLUE}📦 安装 certbot 和相关组件...${NC}"

# 确定包管理器
if command -v dnf &> /dev/null; then
    PKG_MANAGER="dnf"
    echo "使用包管理器: dnf"
elif command -v yum &> /dev/null; then
    PKG_MANAGER="yum"
    echo "使用包管理器: yum"
else
    echo -e "${RED}❌ 未找到包管理器 (dnf/yum)${NC}"
    exit 1
fi

# 更新包索引
echo "更新包索引..."
if [ "$PKG_MANAGER" = "dnf" ]; then
    dnf update -y
else
    yum update -y
fi

# 安装 EPEL 仓库（如果不存在）
echo "检查 EPEL 仓库..."
if [ "$PKG_MANAGER" = "dnf" ]; then
    if ! dnf repolist | grep -q "epel"; then
        echo "安装 EPEL 仓库..."
        dnf install -y epel-release
    else
        echo "EPEL 仓库已存在"
    fi
else
    if ! yum repolist | grep -q "epel"; then
        echo "安装 EPEL 仓库..."
        yum install -y epel-release
    else
        echo "EPEL 仓库已存在"
    fi
fi

# 安装 certbot
echo "安装 certbot..."
if [ "$PKG_MANAGER" = "dnf" ]; then
    dnf install -y certbot python3-certbot-nginx python3-certbot-apache
else
    yum install -y certbot python3-certbot-nginx python3-certbot-apache
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ certbot 安装成功！${NC}"
else
    echo -e "${RED}❌ certbot 安装失败，尝试替代方案...${NC}"
    
    # 尝试安装 EPEL 版本的 certbot
    echo "尝试安装 EPEL 版本的 certbot..."
    if [ "$PKG_MANAGER" = "dnf" ]; then
        dnf install -y python3-certbot
    else
        yum install -y python3-certbot
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ python3-certbot 安装成功！${NC}"
    else
        echo -e "${RED}❌ 所有安装方法都失败了${NC}"
        echo "请手动安装 certbot: https://certbot.eff.org/"
        exit 1
    fi
fi

# 验证安装
echo ""
echo -e "${BLUE}🔍 验证安装结果...${NC}"

if command -v certbot &> /dev/null; then
    echo -e "${GREEN}✅ certbot 命令可用${NC}"
    certbot --version
else
    echo -e "${RED}❌ certbot 命令不可用${NC}"
fi

# 检查 Python 模块
echo ""
echo -e "${BLUE}🔍 检查 Python 模块...${NC}"

if python3 -c "import certbot" 2>/dev/null; then
    echo -e "${GREEN}✅ python3-certbot 模块可用${NC}"
else
    echo -e "${RED}❌ python3-certbot 模块不可用${NC}"
fi

if python3 -c "import certbot_nginx" 2>/dev/null; then
    echo -e "${GREEN}✅ python3-certbot-nginx 模块可用${NC}"
else
    echo -e "${YELLOW}⚠️  python3-certbot-nginx 模块不可用${NC}"
fi

if python3 -c "import certbot_apache" 2>/dev/null; then
    echo -e "${GREEN}✅ python3-certbot-apache 模块可用${NC}"
else
    echo -e "${YELLOW}⚠️  python3-certbot-apache 模块不可用${NC}"
fi

# 测试 certbot 功能
echo ""
echo -e "${BLUE}🧪 测试 certbot 功能...${NC}"

if command -v certbot &> /dev/null; then
    echo "测试 certbot 帮助命令..."
    if certbot --help &> /dev/null; then
        echo -e "${GREEN}✅ certbot 功能正常${NC}"
    else
        echo -e "${RED}❌ certbot 功能异常${NC}"
    fi
fi

echo ""
echo -e "${GREEN}🎉 阿里云 Linux certbot 安装修复完成！${NC}"
echo ""
echo -e "${BLUE}💡 下一步:${NC}"
echo "现在可以运行 SSL 配置脚本了："
echo "sudo bash scripts/ssl_setup.sh"
echo ""
echo -e "${BLUE}📚 相关脚本:${NC}"
echo "- DNS 工具修复: sudo bash scripts/fix_alinux_dns.sh"
echo "- 通用修复: sudo bash scripts/fix_centos_dns.sh"
echo "- SSL 配置: sudo bash scripts/ssl_setup.sh"
echo "- 状态检查: bash scripts/ssl_status.sh"
echo ""
echo -e "${BLUE}🔍 系统检测:${NC}"
echo "- 测试系统兼容性: bash scripts/test_system_detection.sh"
echo "- 测试 SSL 系统检测: bash scripts/test_ssl_system_detection.sh"
