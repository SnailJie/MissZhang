#!/usr/bin/env python3
"""
微信登录调试测试脚本
用于测试和调试微信登录的各个组件
"""

import os
import sys
import time
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ 环境变量加载成功")
except ImportError:
    print("⚠ 未安装python-dotenv，使用系统环境变量")

def test_wechat_config():
    """测试微信配置"""
    print("\n=== 测试微信配置 ===")
    
    try:
        from app.wechat_config import WeChatConfig
        config = WeChatConfig()
        
        print(f"AppID: {config.app_id}")
        print(f"AppSecret: {'*' * len(config.app_secret) if config.app_secret else '未设置'}")
        print(f"Token: {config.token}")
        print(f"登录关键词: {config.login_keyword}")
        print(f"会话超时: {config.session_timeout}秒")
        print(f"是否已配置: {config.is_configured}")
        
        if not config.is_configured:
            print("❌ 微信配置不完整，请检查环境变量")
            return False
        else:
            print("✓ 微信配置完整")
            return True
            
    except Exception as e:
        print(f"❌ 微信配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_wechat_service():
    """测试微信服务"""
    print("\n=== 测试微信服务 ===")
    
    try:
        from app.wechat_service import WeChatService
        service = WeChatService()
        
        print("开始获取access_token...")
        access_token = service.get_access_token()
        
        if access_token:
            print(f"✓ 成功获取access_token: {access_token[:10]}...")
            
            # 测试获取关注者列表
            print("开始获取关注者列表...")
            followers = service.get_followers_list()
            if followers:
                openids = followers.get('data', {}).get('openid', [])
                print(f"✓ 成功获取关注者列表，共 {len(openids)} 个用户")
                
                if openids:
                    # 测试获取第一个用户信息
                    test_openid = openids[0]
                    print(f"测试获取用户信息: {test_openid}")
                    user_info = service.get_user_info(test_openid)
                    if user_info:
                        print(f"✓ 成功获取用户信息: {user_info.get('nickname', '未知用户')}")
                        print(f"  关注状态: {'已关注' if user_info.get('subscribe') == 1 else '未关注'}")
                    else:
                        print("❌ 获取用户信息失败")
                else:
                    print("⚠ 关注者列表为空")
            else:
                print("❌ 获取关注者列表失败")
        else:
            print("❌ 获取access_token失败")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 微信服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_identity_manager():
    """测试用户身份管理"""
    print("\n=== 测试用户身份管理 ===")
    
    try:
        from app.user_identity import user_identity_manager
        
        print(f"当前活跃会话数量: {user_identity_manager.get_active_sessions_count()}")
        
        # 测试创建会话（需要有效的openid）
        test_openid = "test_openid_123"
        print(f"测试创建会话: {test_openid}")
        
        # 注意：这里会失败，因为test_openid不是真实的关注者
        session_id = user_identity_manager.create_login_session(test_openid)
        if session_id:
            print(f"✓ 会话创建成功: {session_id}")
        else:
            print("⚠ 会话创建失败（这是预期的，因为使用了测试openid）")
        
        print("✓ 用户身份管理测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 用户身份管理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_wechat_auth():
    """测试微信认证"""
    print("\n=== 测试微信认证 ===")
    
    try:
        from app.wechat_auth import WeChatAuth
        auth = WeChatAuth()
        
        # 测试签名验证
        test_token = "mytoken123"
        test_timestamp = "1234567890"
        test_nonce = "test_nonce"
        
        # 生成测试签名
        import hashlib
        params = [test_token, test_timestamp, test_nonce]
        params.sort()
        temp_str = ''.join(params)
        test_signature = hashlib.sha1(temp_str.encode('utf-8')).hexdigest()
        
        print(f"测试签名验证...")
        is_valid = auth.verify_signature(test_signature, test_timestamp, test_nonce, test_token)
        
        if is_valid:
            print("✓ 签名验证测试通过")
        else:
            print("❌ 签名验证测试失败")
            return False
        
        print("✓ 微信认证测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 微信认证测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_variables():
    """测试环境变量"""
    print("\n=== 测试环境变量 ===")
    
    required_vars = [
        'WECHAT_APP_ID',
        'WECHAT_APP_SECRET',
        'WECHAT_TOKEN',
        'FLASK_SECRET_KEY'
    ]
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value and value != 'your_app_id_here':
            print(f"✓ {var}: {'*' * len(value)}")
        else:
            print(f"❌ {var}: 未设置或使用默认值")
            all_set = False
    
    if all_set:
        print("✓ 所有必需的环境变量都已设置")
    else:
        print("⚠ 部分环境变量未设置，请检查.env文件")
    
    return all_set

def main():
    """主测试函数"""
    print("微信登录调试测试开始...")
    print("=" * 50)
    
    tests = [
        ("环境变量", test_environment_variables),
        ("微信配置", test_wechat_config),
        ("微信认证", test_wechat_auth),
        ("微信服务", test_wechat_service),
        ("用户身份管理", test_user_identity_manager),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！微信登录配置正常")
    else:
        print("⚠ 部分测试失败，请检查配置和日志")
        print("\n建议检查:")
        print("1. 环境变量是否正确设置")
        print("2. 微信公众平台配置是否正确")
        print("3. 网络连接是否正常")
        print("4. 查看应用日志获取详细错误信息")

if __name__ == "__main__":
    main()
