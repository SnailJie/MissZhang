#!/usr/bin/env bash
set -euo pipefail

echo "🔧 MissZhang 环境配置设置脚本"
echo "================================"

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_EXAMPLE="$PROJECT_ROOT/env.example"
ENV_FILE="$PROJECT_ROOT/.env"

# 检查是否已有 .env 文件
if [ -f "$ENV_FILE" ]; then
    echo "⚠️  发现已存在的 .env 文件"
    read -p "是否要重新配置？这将覆盖现有配置 (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "✅ 保持现有配置不变"
        exit 0
    fi
    echo "🔄 将重新配置环境变量"
fi

# 复制环境变量模板
if [ ! -f "$ENV_EXAMPLE" ]; then
    echo "❌ 未找到 env.example 文件"
    exit 1
fi

cp "$ENV_EXAMPLE" "$ENV_FILE"
echo "✅ 已创建 .env 文件"

# 提示用户配置
echo ""
echo "📝 请编辑 .env 文件配置以下参数："
echo ""
echo "1. 微信配置："
echo "   - WECHAT_APP_ID: 从微信公众平台获取"
echo "   - WECHAT_APP_SECRET: 从微信公众平台获取"
echo "   - WECHAT_REDIRECT_URI: 回调地址"
echo ""
echo "2. Flask配置："
echo "   - FLASK_SECRET_KEY: 使用强随机字符串"
echo "   - FLASK_ENV: 开发环境设为 development"
echo ""
echo "3. 生产环境配置："
echo "   - PRODUCTION_HOST: 生产环境主机地址"
echo "   - PRODUCTION_PORT: 生产环境端口"
echo ""

# 询问是否立即编辑
if command -v nano &> /dev/null; then
    read -p "是否立即使用 nano 编辑 .env 文件？(Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo "请手动编辑 .env 文件"
    else
        nano "$ENV_FILE"
    fi
elif command -v vim &> /dev/null; then
    read -p "是否立即使用 vim 编辑 .env 文件？(Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo "请手动编辑 .env 文件"
    else
        vim "$ENV_FILE"
    fi
else
    echo "请使用你喜欢的编辑器手动编辑 .env 文件"
fi

echo ""
echo "🎯 配置完成后，你可以："
echo "1. 运行 'python run.py' 启动开发环境"
echo "2. 运行 'bash scripts/start.sh' 启动生产环境"
echo "3. 运行 'bash scripts/deploy.sh' 部署到服务器"
echo ""
echo "📚 更多信息请查看 QUICKSTART.md 文件"
