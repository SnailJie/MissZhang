#!/bin/bash

# 系统检测测试脚本
# 用于验证系统识别功能（无需 root 权限）

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔍 系统检测测试"
echo "==============="

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
echo "ID: $ID"
echo "ID_LIKE: $ID_LIKE"

# 检查是否为 CentOS/RHEL 兼容系统
echo ""
echo -e "${BLUE}🔍 检查系统兼容性...${NC}"

COMPATIBLE=false

# 检查各种标识符
if [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"Rocky"* ]] || [[ "$OS" == *"Alma"* ]] || [[ "$OS" == *"Alibaba Cloud Linux"* ]] || [[ "$OS" == *"Amazon Linux"* ]]; then
    COMPATIBLE=true
    echo -e "${GREEN}✅ 通过操作系统名称匹配${NC}"
fi

if [[ "$ID" == "centos" ]] || [[ "$ID" == "rhel" ]] || [[ "$ID" == "rocky" ]] || [[ "$ID" == "almalinux" ]] || [[ "$ID" == "alinux" ]] || [[ "$ID" == "amzn" ]]; then
    COMPATIBLE=true
    echo -e "${GREEN}✅ 通过系统 ID 匹配${NC}"
fi

if [[ "$ID_LIKE" == *"rhel"* ]] || [[ "$ID_LIKE" == *"centos"* ]]; then
    COMPATIBLE=true
    echo -e "${GREEN}✅ 通过系统 ID_LIKE 匹配${NC}"
fi

# 检查包管理器
echo ""
echo -e "${BLUE}🔍 检查包管理器...${NC}"

if command -v dnf &> /dev/null; then
    echo -e "${GREEN}✅ 找到 dnf 包管理器${NC}"
    PKG_MANAGER="dnf"
elif command -v yum &> /dev/null; then
    echo -e "${GREEN}✅ 找到 yum 包管理器${NC}"
    PKG_MANAGER="yum"
else
    echo -e "${RED}❌ 未找到 dnf 或 yum 包管理器${NC}"
    PKG_MANAGER="none"
fi

# 检查 DNS 工具
echo ""
echo -e "${BLUE}🔍 检查当前可用的 DNS 工具...${NC}"

DNS_TOOLS=()

if command -v dig &> /dev/null; then
    echo -e "${GREEN}✅ dig 命令可用${NC}"
    DNS_TOOLS+=("dig")
else
    echo -e "${RED}❌ dig 命令不可用${NC}"
fi

if command -v host &> /dev/null; then
    echo -e "${GREEN}✅ host 命令可用${NC}"
    DNS_TOOLS+=("host")
else
    echo -e "${RED}❌ host 命令不可用${NC}"
fi

if command -v nslookup &> /dev/null; then
    echo -e "${GREEN}✅ nslookup 命令可用${NC}"
    DNS_TOOLS+=("host")
else
    echo -e "${RED}❌ nslookup 命令不可用${NC}"
fi

# 总结
echo ""
echo -e "${BLUE}📊 检测结果总结${NC}"
echo "=================="

if [ "$COMPATIBLE" = true ]; then
    echo -e "${GREEN}✅ 系统兼容性: 通过${NC}"
else
    echo -e "${RED}❌ 系统兼容性: 不通过${NC}"
fi

if [ "$PKG_MANAGER" != "none" ]; then
    echo -e "${GREEN}✅ 包管理器: $PKG_MANAGER${NC}"
else
    echo -e "${RED}❌ 包管理器: 未找到${NC}"
fi

if [ ${#DNS_TOOLS[@]} -gt 0 ]; then
    echo -e "${GREEN}✅ 可用 DNS 工具: ${DNS_TOOLS[*]}${NC}"
else
    echo -e "${RED}❌ 可用 DNS 工具: 无${NC}"
fi

echo ""
if [ "$COMPATIBLE" = true ] && [ "$PKG_MANAGER" != "none" ]; then
    echo -e "${GREEN}🎉 系统完全兼容！可以使用 DNS 工具安装脚本${NC}"
    echo ""
    echo -e "${BLUE}💡 建议操作:${NC}"
    if [ ${#DNS_TOOLS[@]} -eq 0 ]; then
        echo "sudo bash scripts/install_dns_tools.sh"
    else
        echo "sudo bash scripts/fix_centos_dns.sh"
    fi
else
    echo -e "${YELLOW}⚠️  系统不完全兼容，建议手动安装 DNS 工具${NC}"
fi
