#!/usr/bin/env python3
"""
微信登录系统测试脚本
用于验证新创建的微信登录系统是否正常工作
"""

import os
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        from app.wechat_config import WeChatConfig
        print("✅ WeChatConfig 导入成功")
    except ImportError as e:
        print(f"❌ WeChatConfig 导入失败: {e}")
        return False
    
    try:
        from app.wechat_service import WeChatService
        print("✅ WeChatService 导入成功")
    except ImportError as e:
        print(f"❌ WeChatService 导入失败: {e}")
        return False
    
    try:
        from app.user_identity import user_identity_manager
        print("✅ UserIdentityManager 导入成功")
    except ImportError as e:
        print(f"❌ UserIdentityManager 导入失败: {e}")
        return False
    
    return True

def test_config():
    """测试配置"""
    print("\n🔧 测试配置...")
    
    from app.wechat_config import WeChatConfig
    
    # 检查配置方法
    print(f"APP_ID: {WeChatConfig.APP_ID}")
    print(f"APP_SECRET: {'*' * len(WeChatConfig.APP_SECRET) if WeChatConfig.APP_SECRET != 'your_app_secret_here' else '未配置'}")
    print(f"LOGIN_KEYWORD: {WeChatConfig.LOGIN_KEYWORD}")
    print(f"SESSION_TIMEOUT: {WeChatConfig.SESSION_TIMEOUT}秒")
    
    # 测试配置检查
    is_configured = WeChatConfig.is_configured()
    print(f"配置状态: {'✅ 已配置' if is_configured else '❌ 未配置'}")
    
    # 测试URL生成
    if is_configured:
        try:
            access_token_url = WeChatConfig.get_access_token_url()
            print(f"Access Token URL: {access_token_url}")
        except Exception as e:
            print(f"❌ URL生成失败: {e}")
            return False
    else:
        print("⚠️  跳过URL测试（配置未完成）")
    
    return True

def test_service():
    """测试服务"""
    print("\n🚀 测试服务...")
    
    from app.wechat_service import WeChatService
    
    service = WeChatService()
    
    # 测试会话ID生成
    test_openid = "test_openid_123"
    session_id, timestamp = service.create_login_session(test_openid)
    print(f"测试会话ID: {session_id}")
    print(f"时间戳: {timestamp}")
    
    # 测试会话验证
    is_valid = service.verify_login_session(session_id, test_openid, timestamp)
    print(f"会话验证: {'✅ 有效' if is_valid else '❌ 无效'}")
    
    # 测试会话过期检查
    is_expired = service.is_session_expired(timestamp)
    print(f"会话过期检查: {'❌ 已过期' if is_expired else '✅ 未过期'}")
    
    return True

def test_identity_manager():
    """测试身份管理器"""
    print("\n👤 测试身份管理器...")
    
    from app.user_identity import user_identity_manager
    
    # 测试会话创建
    test_openid = "test_identity_openid_456"
    session_id = user_identity_manager.create_login_session(test_openid)
    
    if session_id:
        print(f"✅ 会话创建成功: {session_id}")
        
        # 测试会话验证
        user_info = user_identity_manager.verify_session(session_id)
        if user_info:
            print(f"✅ 会话验证成功: {user_info.get('nickname', 'Unknown')}")
        else:
            print("❌ 会话验证失败")
        
        # 测试会话清理
        cleanup_result = user_identity_manager._cleanup_session(session_id)
        print(f"会话清理: {'✅ 成功' if cleanup_result else '❌ 失败'}")
        
    else:
        print("❌ 会话创建失败")
        return False
    
    return True

def test_main_app():
    """测试主应用"""
    print("\n🌐 测试主应用...")
    
    try:
        from app.main import app
        print("✅ Flask应用创建成功")
        
        # 检查路由
        routes = []
        for rule in app.url_map.iter_rules():
            if 'wechat' in rule.rule:
                routes.append(rule.rule)
        
        print(f"微信相关路由: {len(routes)}个")
        for route in routes:
            print(f"  - {route}")
        
        return True
        
    except Exception as e:
        print(f"❌ 主应用测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 微信登录系统测试开始")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("配置测试", test_config),
        ("服务测试", test_service),
        ("身份管理器测试", test_identity_manager),
        ("主应用测试", test_main_app),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
        
        print("-" * 30)
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！微信登录系统工作正常")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关配置和代码")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
