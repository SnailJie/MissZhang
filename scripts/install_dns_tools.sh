#!/bin/bash

# CentOS 系统 DNS 工具安装脚本
# 安装 dig, host, nslookup 等 DNS 查询工具

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔧 CentOS DNS 工具安装脚本"
echo "=========================="

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ 错误: 此脚本需要 root 权限${NC}"
    echo "请使用: sudo bash scripts/install_dns_tools.sh"
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

# 检查是否为 CentOS/RHEL 系统
if [[ "$OS" != *"CentOS"* ]] && [[ "$OS" != *"Red Hat"* ]] && [[ "$OS" != *"Rocky"* ]] && [[ "$OS" != *"Alma"* ]]; then
    echo -e "${YELLOW}⚠️  此脚本专为 CentOS/RHEL 系统设计${NC}"
    echo "当前系统: $OS"
    echo "建议使用系统自带的包管理器安装 DNS 工具"
    exit 1
fi

# 检查当前可用的 DNS 工具
echo ""
echo -e "${BLUE}🔍 检查当前可用的 DNS 工具...${NC}"

DNS_TOOLS_AVAILABLE=()
DNS_TOOLS_MISSING=()

if command -v dig &> /dev/null; then
    echo -e "${GREEN}✅ dig 已安装${NC}"
    DNS_TOOLS_AVAILABLE+=("dig")
else
    echo -e "${RED}❌ dig 未安装${NC}"
    DNS_TOOLS_MISSING+=("dig")
fi

if command -v host &> /dev/null; then
    echo -e "${GREEN}✅ host 已安装${NC}"
    DNS_TOOLS_AVAILABLE+=("host")
else
    echo -e "${RED}❌ host 未安装${NC}"
    DNS_TOOLS_MISSING+=("host")
fi

if command -v nslookup &> /dev/null; then
    echo -e "${GREEN}✅ nslookup 已安装${NC}"
    DNS_TOOLS_AVAILABLE+=("nslookup")
else
    echo -e "${RED}❌ nslookup 未安装${NC}"
    DNS_TOOLS_MISSING+=("nslookup")
fi

if command -v whois &> /dev/null; then
    echo -e "${GREEN}✅ whois 已安装${NC}"
    DNS_TOOLS_AVAILABLE+=("whois")
else
    echo -e "${YELLOW}⚠️  whois 未安装（可选）${NC}"
    DNS_TOOLS_MISSING+=("whois")
fi

# 如果所有必需工具都已安装，退出
if [ ${#DNS_TOOLS_MISSING[@]} -eq 0 ] || ([ ${#DNS_TOOLS_MISSING[@]} -eq 1 ] && [[ " ${DNS_TOOLS_MISSING[@]} " =~ " whois " ]]); then
    echo ""
    echo -e "${GREEN}🎉 所有必需的 DNS 工具都已安装！${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}📦 开始安装缺失的 DNS 工具...${NC}"

# 更新系统包列表
echo "更新系统包列表..."
if command -v dnf &> /dev/null; then
    dnf update -y
    PKG_MANAGER="dnf"
elif command -v yum &> /dev/null; then
    yum update -y
    PKG_MANAGER="yum"
else
    echo -e "${RED}❌ 未找到包管理器 (dnf/yum)${NC}"
    exit 1
fi

echo "使用包管理器: $PKG_MANAGER"

# 安装 bind-utils 包（包含 dig, host, nslookup）
echo ""
echo -e "${YELLOW}📦 安装 bind-utils 包...${NC}"
if [ "$PKG_MANAGER" = "dnf" ]; then
    dnf install -y bind-utils
else
    yum install -y bind-utils
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ bind-utils 安装成功${NC}"
else
    echo -e "${RED}❌ bind-utils 安装失败${NC}"
    exit 1
fi

# 安装 whois 包（可选）
echo ""
echo -e "${YELLOW}📦 安装 whois 包...${NC}"
if [ "$PKG_MANAGER" = "dnf" ]; then
    dnf install -y whois
else
    yum install -y whois
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ whois 安装成功${NC}"
else
    echo -e "${YELLOW}⚠️  whois 安装失败（非必需）${NC}"
fi

# 验证安装结果
echo ""
echo -e "${BLUE}🔍 验证安装结果...${NC}"

DNS_TOOLS_AVAILABLE_AFTER=()
DNS_TOOLS_MISSING_AFTER=()

if command -v dig &> /dev/null; then
    DIG_VERSION=$(dig -v | head -1)
    echo -e "${GREEN}✅ dig 已安装: $DIG_VERSION${NC}"
    DNS_TOOLS_AVAILABLE_AFTER+=("dig")
else
    echo -e "${RED}❌ dig 安装失败${NC}"
    DNS_TOOLS_MISSING_AFTER+=("dig")
fi

if command -v host &> /dev/null; then
    HOST_VERSION=$(host -V 2>&1 | head -1)
    echo -e "${GREEN}✅ host 已安装: $HOST_VERSION${NC}"
    DNS_TOOLS_AVAILABLE_AFTER+=("host")
else
    echo -e "${RED}❌ host 安装失败${NC}"
    DNS_TOOLS_MISSING_AFTER+=("host")
fi

if command -v nslookup &> /dev/null; then
    NSLOOKUP_VERSION=$(nslookup -version 2>&1 | head -1)
    echo -e "${GREEN}✅ nslookup 已安装: $NSLOOKUP_VERSION${NC}"
    DNS_TOOLS_AVAILABLE_AFTER+=("nslookup")
else
    echo -e "${RED}❌ nslookup 安装失败${NC}"
    DNS_TOOLS_MISSING_AFTER+=("nslookup")
fi

if command -v whois &> /dev/null; then
    WHOIS_VERSION=$(whois --version 2>&1 | head -1)
    echo -e "${GREEN}✅ whois 已安装: $WHOIS_VERSION${NC}"
    DNS_TOOLS_AVAILABLE_AFTER+=("whois")
else
    echo -e "${YELLOW}⚠️  whois 未安装（非必需）${NC}"
fi

# 测试 DNS 查询功能
echo ""
echo -e "${BLUE}🧪 测试 DNS 查询功能...${NC}"

# 测试 dig
if command -v dig &> /dev/null; then
    echo "测试 dig 命令..."
    if dig +short google.com &> /dev/null; then
        echo -e "${GREEN}✅ dig 功能正常${NC}"
    else
        echo -e "${RED}❌ dig 功能异常${NC}"
    fi
fi

# 测试 host
if command -v host &> /dev/null; then
    echo "测试 host 命令..."
    if host google.com &> /dev/null; then
        echo -e "${GREEN}✅ host 功能正常${NC}"
    else
        echo -e "${RED}❌ host 功能异常${NC}"
    fi
fi

# 测试 nslookup
if command -v nslookup &> /dev/null; then
    echo "测试 nslookup 命令..."
    if nslookup google.com &> /dev/null; then
        echo -e "${GREEN}✅ nslookup 功能正常${NC}"
    else
        echo -e "${RED}❌ nslookup 功能异常${NC}"
    fi
fi

# 安装总结
echo ""
echo -e "${BLUE}📋 安装总结:${NC}"
echo "=================="

if [ ${#DNS_TOOLS_MISSING_AFTER[@]} -eq 0 ]; then
    echo -e "${GREEN}🎉 所有必需的 DNS 工具安装成功！${NC}"
    echo ""
    echo -e "${BLUE}🔧 可用的 DNS 工具:${NC}"
    for tool in "${DNS_TOOLS_AVAILABLE_AFTER[@]}"; do
        echo "- $tool"
    done
    echo ""
    echo -e "${BLUE}💡 使用示例:${NC}"
    echo "检查域名解析: dig example.com"
    echo "检查域名解析: host example.com"
    echo "检查域名解析: nslookup example.com"
    echo "查询域名信息: whois example.com"
    echo ""
    echo -e "${GREEN}✅ 现在可以运行 SSL 配置脚本了！${NC}"
    echo "运行: sudo bash scripts/ssl_setup.sh"
else
    echo -e "${YELLOW}⚠️  部分 DNS 工具安装失败${NC}"
    echo "失败的工具: ${DNS_TOOLS_MISSING_AFTER[*]}"
    echo ""
    echo -e "${BLUE}🔧 建议:${NC}"
    echo "1. 检查网络连接"
    echo "2. 检查包管理器配置"
    echo "3. 手动安装: $PKG_MANAGER install -y bind-utils"
fi

echo ""
echo -e "${BLUE}📚 相关文档:${NC}"
echo "- DNS 工具使用指南: man dig, man host, man nslookup"
echo "- SSL 配置指南: docs/ssl-setup-guide.md"
echo "- SSL 配置脚本: scripts/ssl_setup.sh"
