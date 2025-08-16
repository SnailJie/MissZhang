#!/usr/bin/env python3
"""
测试修复后的微信配置
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_wechat_config():
    """测试WeChatConfig类"""
    try:
        from wechat_config import WeChatConfig
        
        # 创建实例
        config = WeChatConfig()
        print("✅ WeChatConfig 实例化成功")
        
        # 测试属性
        print(f"APP_ID: {config.app_id}")
        print(f"APP_SECRET: {'*' * len(config.app_secret) if config.app_secret else '未配置'}")
        print(f"LOGIN_KEYWORD: {config.login_keyword}")
        print(f"SESSION_TIMEOUT: {config.session_timeout}秒")
        
        # 测试方法
        print(f"ACCESS_TOKEN_URL: {config.access_token_url}")
        print(f"USER_INFO_URL: {config.user_info_url}")
        print(f"CUSTOM_MESSAGE_URL: {config.custom_message_url}")
        
        # 测试配置检查
        print(f"配置完整: {config.is_configured}")
        
        return True
        
    except Exception as e:
        print(f"❌ WeChatConfig 测试失败: {e}")
        return False

def test_wechat_auth():
    """测试WeChatAuth类"""
    try:
        from wechat_auth import WeChatAuth
        
        # 创建实例
        auth = WeChatAuth()
        print("✅ WeChatAuth 实例化成功")
        
        # 测试属性
        print(f"APP_ID: {auth.app_id}")
        print(f"APP_SECRET: {'*' * len(auth.app_secret) if auth.app_secret else '未配置'}")
        
        return True
        
    except Exception as e:
        print(f"❌ WeChatAuth 测试失败: {e}")
        return False

def test_wechat_service():
    """测试WeChatService类"""
    try:
        from wechat_service import WeChatService
        
        # 创建实例
        service = WeChatService()
        print("✅ WeChatService 实例化成功")
        
        return True
        
    except Exception as e:
        print(f"❌ WeChatService 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试修复后的微信配置...")
    print("=" * 50)
    
    success_count = 0
    total_tests = 3
    
    if test_wechat_config():
        success_count += 1
    
    if test_wechat_auth():
        success_count += 1
    
    if test_wechat_service():
        success_count += 1
    
    print("=" * 50)
    print(f"测试完成: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！修复成功！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败，需要进一步检查")
        sys.exit(1)
