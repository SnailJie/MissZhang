#!/bin/bash

# 微信登录调试启动脚本

echo "=== 微信登录调试启动脚本 ==="
echo "时间: $(date)"
echo ""

# 检查Python环境
echo "检查Python环境..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ 未找到Python环境"
    exit 1
fi

echo "✓ 使用Python命令: $PYTHON_CMD"
echo ""

# 检查依赖
echo "检查Python依赖..."
$PYTHON_CMD -c "import flask, requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 缺少必要的Python依赖，正在安装..."
    pip install flask requests python-dotenv
fi
echo "✓ 依赖检查完成"
echo ""

# 检查环境变量文件
echo "检查环境变量配置..."
if [ ! -f ".env" ]; then
    echo "⚠ 未找到.env文件，正在从env.example复制..."
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✓ 已创建.env文件，请编辑其中的配置"
    else
        echo "❌ 未找到env.example文件"
        exit 1
    fi
else
    echo "✓ 找到.env文件"
fi
echo ""

# 运行调试测试
echo "运行微信登录调试测试..."
echo "----------------------------------------"
$PYTHON_CMD test_wechat_debug.py
echo "----------------------------------------"
echo ""

# 询问是否启动应用
read -p "是否启动Flask应用进行进一步测试？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "启动Flask应用..."
    echo "应用将在 http://localhost:5000 启动"
    echo "按 Ctrl+C 停止应用"
    echo ""
    
    # 启动Flask应用
    $PYTHON_CMD run.py
else
    echo "跳过启动Flask应用"
    echo ""
    echo "如需手动启动，请运行:"
    echo "  $PYTHON_CMD run.py"
    echo ""
    echo "然后在另一个终端运行接口测试:"
    echo "  $PYTHON_CMD test_wechat_message.py"
fi

echo ""
echo "调试启动脚本完成！"
