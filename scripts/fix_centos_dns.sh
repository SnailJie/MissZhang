#!/bin/bash

# CentOS 系统 DNS 工具快速修复脚本
# 快速安装 bind-utils 包

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔧 CentOS/RHEL 兼容系统 DNS 工具快速修复"
echo "=========================================="

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ 错误: 此脚本需要 root 权限${NC}"
    echo "请使用: sudo bash scripts/fix_centos_dns.sh"
    exit 1
fi

# 检测操作系统
echo -e "${BLUE}🔍 检测操作系统...${NC}"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    OS=$(uname -s)
    VER=$(uname -r)
fi

echo "操作系统: $OS $VER"

# 检查是否为 CentOS/RHEL 兼容系统
if [[ "$OS" != *"CentOS"* ]] && [[ "$OS" != *"Red Hat"* ]] && [[ "$OS" != *"Rocky"* ]] && [[ "$OS" != *"Alma"* ]] && [[ "$OS" != *"Alibaba Cloud Linux"* ]] && [[ "$OS" != *"Amazon Linux"* ]]; then
    echo -e "${YELLOW}⚠️  此脚本专为 CentOS/RHEL 兼容系统设计${NC}"
    echo "当前系统: $OS"
    
    # 根据系统类型提供不同的建议
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        echo "Ubuntu/Debian 系统建议使用: sudo apt install -y dnsutils"
    elif [[ "$OS" == *"Alibaba Cloud Linux"* ]] || [[ "$ID" == "alinux" ]]; then
        echo "阿里云 Linux 系统建议使用: sudo bash scripts/fix_alinux_dns.sh"
    else
        echo "建议使用系统自带的包管理器安装 DNS 工具"
    fi
    exit 1
fi

# 阿里云系统特殊提示
if [[ "$OS" == *"Alibaba Cloud Linux"* ]] || [[ "$ID" == "alinux" ]]; then
    echo -e "${BLUE}🔧 检测到阿里云 Linux 系统${NC}"
    echo "建议优先使用专用修复脚本: sudo bash scripts/fix_alinux_dns.sh"
    echo "或者继续使用此通用脚本..."
    echo ""
fi

echo -e "${GREEN}✅ 系统兼容性检查通过${NC}"

echo ""
echo -e "${BLUE}📦 快速安装 bind-utils 包...${NC}"

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

# 安装 bind-utils
echo "安装 bind-utils 包..."
if [ "$PKG_MANAGER" = "dnf" ]; then
    dnf install -y bind-utils
else
    yum install -y bind-utils
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ bind-utils 安装成功！${NC}"
else
    echo -e "${RED}❌ bind-utils 安装失败${NC}"
    exit 1
fi

# 验证安装
echo ""
echo -e "${BLUE}🔍 验证安装结果...${NC}"

if command -v dig &> /dev/null; then
    echo -e "${GREEN}✅ dig 命令可用${NC}"
else
    echo -e "${RED}❌ dig 命令不可用${NC}"
fi

if command -v host &> /dev/null; then
    echo -e "${GREEN}✅ host 命令可用${NC}"
else
    echo -e "${RED}❌ host 命令不可用${NC}"
fi

if command -v nslookup &> /dev/null; then
    echo -e "${GREEN}✅ nslookup 命令可用${NC}"
else
    echo -e "${RED}❌ nslookup 命令不可用${NC}"
fi

# 测试 DNS 查询
echo ""
echo -e "${BLUE}🧪 测试 DNS 查询功能...${NC}"

if command -v dig &> /dev/null; then
    echo "测试 dig 查询..."
    if dig +short google.com &> /dev/null; then
        echo -e "${GREEN}✅ dig 功能正常${NC}"
    else
        echo -e "${RED}❌ dig 功能异常${NC}"
    fi
fi

echo ""
echo -e "${GREEN}🎉 DNS 工具修复完成！${NC}"
echo ""
echo -e "${BLUE}💡 下一步:${NC}"
echo "现在可以运行 SSL 配置脚本了："
echo "sudo bash scripts/ssl_setup.sh"
echo ""
echo -e "${BLUE}📚 相关脚本:${NC}"
echo "- DNS 工具完整安装: sudo bash scripts/install_dns_tools.sh"
echo "- SSL 配置: sudo bash scripts/ssl_setup.sh"
echo "- 状态检查: bash scripts/ssl_status.sh"

# 阿里云系统特殊提示
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [[ "$ID" == "alinux" ]] || [[ "$OS" == *"Alibaba Cloud Linux"* ]]; then
        echo ""
        echo -e "${BLUE}🔧 阿里云 Linux 系统特殊提示:${NC}"
        echo "- 如果遇到问题，建议使用专用修复脚本: sudo bash scripts/fix_alinux_dns.sh"
        echo "- 使用快速修复选择器: bash scripts/quick_fix_selector.sh"
        echo "- 检查系统兼容性: bash scripts/test_system_detection.sh"
    fi
fi
