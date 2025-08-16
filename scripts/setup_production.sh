#!/bin/bash

# 生产环境配置脚本
# 用于快速配置生产环境参数

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🚀 生产环境配置脚本"
echo "=================="

# 检查 .env 文件
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${RED}❌ 错误: 未找到 .env 配置文件${NC}"
    echo "请先运行: bash scripts/setup_env.sh"
    exit 1
fi

echo -e "${GREEN}✅ 找到 .env 配置文件${NC}"

# 备份当前配置
cp "$PROJECT_ROOT/.env" "$PROJECT_ROOT/.env.backup.$(date +%Y%m%d_%H%M%S)"
echo -e "${BLUE}📋 已备份当前配置${NC}"

# 生成强随机密钥
echo -e "${YELLOW}🔑 生成强随机密钥...${NC}"
NEW_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# 获取用户输入
echo ""
echo -e "${BLUE}请输入生产环境配置信息:${NC}"

# 域名配置
read -p "🌐 请输入你的域名 (例如: example.com): " DOMAIN_NAME
if [ -z "$DOMAIN_NAME" ]; then
    echo -e "${RED}❌ 域名不能为空${NC}"
    exit 1
fi

# 端口配置
read -p "🔌 请输入端口号 (默认: 80): " PORT_NUMBER
PORT_NUMBER=${PORT_NUMBER:-80}

# 确认配置
echo ""
echo -e "${YELLOW}📋 配置确认:${NC}"
echo "域名: $DOMAIN_NAME"
echo "端口: $PORT_NUMBER"
echo "密钥: ${NEW_SECRET_KEY:0:16}..."

read -p "确认使用以上配置? (y/N): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "配置已取消"
    exit 0
fi

# 更新配置文件
echo ""
echo -e "${YELLOW}📝 更新配置文件...${NC}"

# 使用 sed 更新配置
sed -i.bak \
    -e "s/FLASK_SECRET_KEY=.*/FLASK_SECRET_KEY=$NEW_SECRET_KEY/" \
    -e "s/FLASK_ENV=.*/FLASK_ENV=production/" \
    -e "s/FLASK_DEBUG=.*/FLASK_DEBUG=0/" \
    -e "s|WECHAT_REDIRECT_URI=.*|WECHAT_REDIRECT_URI=https://$DOMAIN_NAME/wechat/callback|" \
    "$PROJECT_ROOT/.env"

# 添加生产环境配置（如果不存在）
if ! grep -q "PRODUCTION_HOST" "$PROJECT_ROOT/.env"; then
    echo "" >> "$PROJECT_ROOT/.env"
    echo "# 生产环境配置" >> "$PROJECT_ROOT/.env"
    echo "PRODUCTION_HOST=0.0.0.0" >> "$PROJECT_ROOT/.env"
    echo "PRODUCTION_PORT=$PORT_NUMBER" >> "$PROJECT_ROOT/.env"
else
    # 更新现有配置
    sed -i.bak \
        -e "s/PRODUCTION_HOST=.*/PRODUCTION_HOST=0.0.0.0/" \
        -e "s/PRODUCTION_PORT=.*/PRODUCTION_PORT=$PORT_NUMBER/" \
        "$PROJECT_ROOT/.env"
fi

# 清理备份文件
rm -f "$PROJECT_ROOT/.env.bak"

echo -e "${GREEN}✅ 配置文件更新完成${NC}"

# 设置文件权限
chmod 600 "$PROJECT_ROOT/.env"
echo -e "${BLUE}🔒 已设置 .env 文件权限为 600${NC}"

# 显示更新后的配置
echo ""
echo -e "${GREEN}📋 更新后的配置摘要:${NC}"
echo "=================="
grep -E "^(FLASK_|WECHAT_|PRODUCTION_)" "$PROJECT_ROOT/.env" | while read line; do
    if [[ $line == *"SECRET"* ]]; then
        # 隐藏密钥的完整内容
        key="${line%%=*}"
        value="${line#*=}"
        echo "$key=${value:0:16}..."
    else
        echo "$line"
    fi
done

echo ""
echo -e "${GREEN}🎉 生产环境配置完成！${NC}"
echo ""
echo -e "${YELLOW}⚠️  重要提醒:${NC}"
echo "1. 确保域名 $DOMAIN_NAME 已解析到服务器 IP"
echo "2. 配置 HTTPS 证书（微信要求）"
echo "3. 在微信公众平台更新授权回调域名"
echo "4. 运行 'bash scripts/status.sh' 检查配置"
echo "5. 运行 'sudo bash scripts/deploy.sh' 部署应用"
echo ""
echo -e "${BLUE}📚 更多信息请查看 QUICKSTART.md 文件${NC}"
