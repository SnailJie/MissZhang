#!/usr/bin/env bash
set -euo pipefail

echo "📊 MissZhang 系统状态检查"
echo "=========================="

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$PROJECT_ROOT/run/gunicorn.pid"
LOG_DIR="$PROJECT_ROOT/logs"
DATA_DIR="$PROJECT_ROOT/data"

# 检查应用运行状态
echo "🔍 应用运行状态："
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "✅ 应用正在运行 (PID: $PID)"
        
        # 检查端口占用
        if command -v netstat &> /dev/null; then
            PORT=$(netstat -tlnp 2>/dev/null | grep "$PID" | head -1 | awk '{print $4}' | cut -d: -f2)
            if [ -n "$PORT" ]; then
                echo "🌐 监听端口: $PORT"
            fi
        fi
        
        # 健康检查
        if command -v curl &> /dev/null; then
            if curl -f -s "http://127.0.0.1:80/health" > /dev/null; then
                echo "💚 健康检查: 通过"
            else
                echo "⚠️  健康检查: 失败"
            fi
        fi
    else
        echo "❌ 应用未运行 (PID文件存在但进程不存在)"
        echo "清理PID文件..."
        rm -f "$PID_FILE"
    fi
else
    echo "❌ 应用未运行 (无PID文件)"
fi

echo ""

# 检查环境配置
echo "🔧 环境配置状态："
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "✅ .env 配置文件存在"
    
    # 检查关键配置
    if grep -q "WECHAT_APP_ID" "$PROJECT_ROOT/.env"; then
        APP_ID=$(grep "WECHAT_APP_ID" "$PROJECT_ROOT/.env" | cut -d= -f2)
        if [ "$APP_ID" != "your_app_id_here" ]; then
            echo "✅ 微信 AppID 已配置"
        else
            echo "⚠️  微信 AppID 未配置 (使用默认值)"
        fi
    else
        echo "❌ 微信 AppID 配置缺失"
    fi
    
    if grep -q "WECHAT_APP_SECRET" "$PROJECT_ROOT/.env"; then
        APP_SECRET=$(grep "WECHAT_APP_SECRET" "$PROJECT_ROOT/.env" | cut -d= -f2)
        if [ "$APP_SECRET" != "your_app_secret_here" ]; then
            echo "✅ 微信 AppSecret 已配置"
        else
            echo "⚠️  微信 AppSecret 未配置 (使用默认值)"
        fi
    else
        echo "❌ 微信 AppSecret 配置缺失"
    fi
else
    echo "❌ .env 配置文件不存在"
    echo "请运行: bash scripts/setup_env.sh"
fi

echo ""

# 检查数据库状态
echo "🗄️  数据库状态："
if [ -d "$DATA_DIR" ]; then
    echo "✅ 数据目录存在: $DATA_DIR"
    
    if [ -f "$DATA_DIR/app.db" ]; then
        echo "✅ 数据库文件存在"
        
        # 检查数据库大小
        DB_SIZE=$(du -h "$DATA_DIR/app.db" | cut -f1)
        echo "📊 数据库大小: $DB_SIZE"
        
        # 检查数据库权限
        if [ -r "$DATA_DIR/app.db" ] && [ -w "$DATA_DIR/app.db" ]; then
            echo "✅ 数据库权限正常"
        else
            echo "⚠️  数据库权限异常"
        fi
    else
        echo "⚠️  数据库文件不存在 (首次运行时会自动创建)"
    fi
else
    echo "❌ 数据目录不存在"
fi

echo ""

# 检查日志状态
echo "📝 日志状态："
if [ -d "$LOG_DIR" ]; then
    echo "✅ 日志目录存在: $LOG_DIR"
    
    # 检查日志文件
    if [ -f "$LOG_DIR/gunicorn.access.log" ]; then
        ACCESS_LOG_SIZE=$(du -h "$LOG_DIR/gunicorn.access.log" | cut -f1)
        echo "📊 访问日志: $ACCESS_LOG_SIZE"
    fi
    
    if [ -f "$LOG_DIR/gunicorn.error.log" ]; then
        ERROR_LOG_SIZE=$(du -h "$LOG_DIR/gunicorn.error.log" | cut -f1)
        echo "📊 错误日志: $ERROR_LOG_SIZE"
    fi
else
    echo "⚠️  日志目录不存在 (应用启动时会自动创建)"
fi

echo ""

# 检查依赖状态
echo "📦 依赖状态："
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo "✅ 虚拟环境存在"
    
    # 检查 Python 版本
    if [ -f "$PROJECT_ROOT/.venv/bin/python" ]; then
        PYTHON_VERSION=$("$PROJECT_ROOT/.venv/bin/python" --version 2>&1)
        echo "🐍 Python版本: $PYTHON_VERSION"
    fi
    
    # 检查关键包
    if [ -f "$PROJECT_ROOT/.venv/bin/pip" ]; then
        if "$PROJECT_ROOT/.venv/bin/pip" show flask &> /dev/null; then
            echo "✅ Flask 已安装"
        else
            echo "❌ Flask 未安装"
        fi
        
        if "$PROJECT_ROOT/.venv/bin/pip" show python-dotenv &> /dev/null; then
            echo "✅ python-dotenv 已安装"
        else
            echo "❌ python-dotenv 未安装"
        fi
    fi
else
    echo "⚠️  虚拟环境不存在"
    echo "请运行: bash scripts/start.sh (会自动创建虚拟环境)"
fi

echo ""
echo "🎯 系统状态检查完成"
echo "如有问题，请查看相关日志文件或运行配置脚本"
