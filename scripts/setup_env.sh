#!/usr/bin/env bash
set -euo pipefail

echo "🔧 配置 MissZhang 环境变量..."

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"
ENV_EXAMPLE="$PROJECT_ROOT/env.example"

if [ ! -f "$ENV_EXAMPLE" ]; then
    echo "❌ 未找到 env.example 文件"
    exit 1
fi

# 如果.env文件已存在，备份
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "📋 已备份现有 .env 文件"
fi

# 复制模板
cp "$ENV_EXAMPLE" "$ENV_FILE"
echo "📋 已创建 .env 文件"

# 生成随机密钥
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "your_secret_key_here_change_this_in_production")

# 更新密钥
sed -i "s/FLASK_SECRET_KEY=.*/FLASK_SECRET_KEY=$SECRET_KEY/" "$ENV_FILE"

echo ""
echo "✅ 环境配置文件已创建: $ENV_FILE"
echo ""
echo "📝 请编辑 .env 文件，配置以下参数："
echo "   1. WECHAT_APP_ID - 微信公众平台AppID"
echo "   2. WECHAT_APP_SECRET - 微信公众平台AppSecret"
echo "   3. WECHAT_REDIRECT_URI - 微信回调地址"
echo ""
echo "🔑 Flask密钥已自动生成"
echo "🌐 生产环境配置已设置为使用8000端口（nginx反向代理）"
echo ""
echo "编辑完成后，运行部署脚本："
echo "   sudo bash scripts/deploy_with_nginx.sh"
