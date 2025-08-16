#!/usr/bin/env python3
"""
MissZhang 应用启动脚本
"""
import os
from app.main import app, init_db

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    # 设置环境变量（如果没有设置）
    if not os.getenv('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'development'
    
    if not os.getenv('FLASK_DEBUG'):
        os.environ['FLASK_DEBUG'] = '1'
    
    # 运行应用
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', '1') == '1'
    )
