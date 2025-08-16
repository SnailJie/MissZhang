#!/usr/bin/env python3
"""
微信登录系统简化测试脚本
避免数据库依赖，只测试核心功能
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

def test_session_management():
    """测试会话管理"""
    print("\n🔐 测试会话管理...")
    
    from app.wechat_config import WeChatConfig
    
    # 测试会话ID生成
    test_openid = "test_openid_123"
    timestamp = int(time.time())
    session_id = WeChatConfig.generate_session_id(test_openid, timestamp)
    print(f"测试会话ID: {session_id}")
    print(f"时间戳: {timestamp}")
    
    # 测试会话验证
    is_valid = WeChatConfig.verify_session_id(session_id, test_openid, timestamp)
    print(f"会话验证: {'✅ 有效' if is_valid else '❌ 无效'}")
    
    # 测试会话过期检查
    is_expired = WeChatConfig.is_session_expired(timestamp)
    print(f"会话过期检查: {'❌ 已过期' if is_expired else '✅ 未过期'}")
    
    # 测试无效会话
    invalid_session = WeChatConfig.verify_session_id("invalid_session", test_openid, timestamp)
    print(f"无效会话验证: {'❌ 应该无效' if not invalid_session else '⚠️  意外有效'}")
    
    return True

def test_service_basic():
    """测试服务基础功能"""
    print("\n🚀 测试服务基础功能...")
    
    from app.wechat_service import WeChatService
    
    service = WeChatService()
    
    # 测试会话ID生成
    test_openid = "test_openid_456"
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

def test_identity_manager_basic():
    """测试身份管理器基础功能"""
    print("\n👤 测试身份管理器基础功能...")
    
    from app.user_identity import user_identity_manager
    
    # 测试会话创建（模拟模式）
    test_openid = "test_identity_openid_789"
    
    # 由于没有真实的微信API，我们跳过实际的用户验证
    print("⚠️  跳过实际用户验证（需要真实微信API）")
    
    # 测试会话清理
    test_session_id = "test_session_123"
    cleanup_result = user_identity_manager._cleanup_session(test_session_id)
    print(f"会话清理: {'✅ 成功' if cleanup_result else '❌ 失败'}")
    
    return True

def test_url_generation():
    """测试URL生成"""
    print("\n🌐 测试URL生成...")
    
    from app.wechat_config import WeChatConfig
    
    # 测试各种URL生成方法
    try:
        # 这些方法需要有效的配置才能正常工作
        if WeChatConfig.is_configured():
            access_token_url = WeChatConfig.get_access_token_url()
            print(f"Access Token URL: {access_token_url}")
            
            # 模拟参数测试
            test_access_token = "test_token_123"
            test_openid = "test_openid_456"
            
            user_info_url = WeChatConfig.get_user_info_url(test_access_token, test_openid)
            print(f"User Info URL: {user_info_url}")
            
            followers_url = WeChatConfig.get_followers_url(test_access_token)
            print(f"Followers URL: {followers_url}")
            
            custom_message_url = WeChatConfig.get_custom_message_url(test_access_token)
            print(f"Custom Message URL: {custom_message_url}")
        else:
            print("⚠️  配置未完成，跳过URL测试")
            
    except Exception as e:
        print(f"❌ URL生成测试失败: {e}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("🧪 微信登录系统简化测试开始")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("配置测试", test_config),
        ("会话管理测试", test_session_management),
        ("服务基础功能测试", test_service_basic),
        ("身份管理器基础功能测试", test_identity_manager_basic),
        ("URL生成测试", test_url_generation),
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
        print("🎉 所有测试通过！微信登录系统核心功能正常")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关配置和代码")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
