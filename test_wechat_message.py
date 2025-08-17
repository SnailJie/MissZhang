#!/usr/bin/env python3
"""
微信消息模拟测试脚本
用于测试微信消息处理接口是否正常工作
"""

import requests
import json
import time
from datetime import datetime

def test_wechat_message_interface():
    """测试微信消息处理接口"""
    print("=== 微信消息接口测试 ===")
    
    # 测试服务器地址
    base_url = "http://localhost:5000"
    
    # 模拟微信消息数据
    test_messages = [
        {
            "name": "登录关键词消息",
            "xml": f'''<xml>
<ToUserName><![CDATA[gh_1234567890]]></ToUserName>
<FromUserName><![CDATA[oTestUser123]]></FromUserName>
<CreateTime>{int(time.time())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[登录]]></Content>
<MsgId>1234567890</MsgId>
</xml>'''
        },
        {
            "name": "其他关键词消息",
            "xml": f'''<xml>
<ToUserName><![CDATA[gh_1234567890]]></ToUserName>
<FromUserName><![CDATA[oTestUser456]]></FromUserName>
<CreateTime>{int(time.time())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[你好]]></Content>
<MsgId>1234567891</MsgId>
</xml>'''
        }
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- 测试 {i}: {message['name']} ---")
        
        try:
            # 发送POST请求到微信消息接口
            response = requests.post(
                f"{base_url}/wechat/message",
                data=message['xml'].encode('utf-8'),
                headers={'Content-Type': 'application/xml'},
                timeout=10
            )
            
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                print("✓ 请求成功")
            else:
                print("❌ 请求失败")
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败 - 请确保Flask应用正在运行")
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except Exception as e:
            print(f"❌ 请求异常: {e}")

def test_wechat_verification():
    """测试微信服务器验证接口"""
    print("\n=== 微信服务器验证测试 ===")
    
    base_url = "http://localhost:5000"
    
    # 模拟微信服务器验证请求
    test_params = {
        'signature': 'test_signature',
        'timestamp': '1234567890',
        'nonce': 'test_nonce',
        'echostr': 'test_echostr'
    }
    
    try:
        response = requests.get(f"{base_url}/wechat/message", params=test_params, timeout=10)
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✓ 验证接口可访问")
        else:
            print("❌ 验证接口返回错误状态码")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - 请确保Flask应用正在运行")
    except Exception as e:
        print(f"❌ 验证测试异常: {e}")

def test_login_status_check():
    """测试登录状态检查接口"""
    print("\n=== 登录状态检查测试 ===")
    
    base_url = "http://localhost:5000"
    
    test_data = {
        'timestamp': int(time.time())
    }
    
    try:
        response = requests.post(
            f"{base_url}/wechat/check_login_status",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                print("✓ 登录状态检查接口正常")
            except json.JSONDecodeError:
                print("⚠ 响应不是有效的JSON格式")
        else:
            print("❌ 登录状态检查接口返回错误状态码")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - 请确保Flask应用正在运行")
    except Exception as e:
        print(f"❌ 登录状态检查测试异常: {e}")

def test_manual_login():
    """测试手动登录接口"""
    print("\n=== 手动登录测试 ===")
    
    base_url = "http://localhost:5000"
    
    # 测试数据
    test_cases = [
        {
            "name": "空OpenID",
            "data": {"openid": ""}
        },
        {
            "name": "无效OpenID",
            "data": {"openid": "invalid_openid_123"}
        },
        {
            "name": "正常OpenID格式",
            "data": {"openid": "oTestUser123"}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 测试用例 {i}: {test_case['name']} ---")
        
        try:
            response = requests.post(
                f"{base_url}/wechat/manual_login",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                except json.JSONDecodeError:
                    print("⚠ 响应不是有效的JSON格式")
            else:
                print("❌ 接口返回错误状态码")
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败 - 请确保Flask应用正在运行")
        except Exception as e:
            print(f"❌ 测试异常: {e}")

def main():
    """主测试函数"""
    print("微信登录接口测试开始...")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # 测试微信消息处理接口
        test_wechat_message_interface()
        
        # 测试微信服务器验证接口
        test_wechat_verification()
        
        # 测试登录状态检查接口
        test_login_status_check()
        
        # 测试手动登录接口
        test_manual_login()
        
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n\n测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("\n注意事项:")
    print("1. 确保Flask应用正在运行 (python run.py)")
    print("2. 检查控制台日志输出")
    print("3. 如果连接失败，请检查端口和防火墙设置")

if __name__ == "__main__":
    main()
