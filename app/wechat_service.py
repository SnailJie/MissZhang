"""
微信服务类 - 处理已认证公众号的用户身份识别
"""
import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from app.wechat_config import WeChatConfig

class WeChatService:
    """微信服务类"""
    
    def __init__(self):
        self.config = WeChatConfig()
        self.access_token = None
        self.token_expires_at = 0
    
    def get_access_token(self) -> Optional[str]:
        """获取access_token，带缓存机制"""
        current_time = time.time()
        
        # 如果token还有效，直接返回
        if self.access_token and current_time < self.token_expires_at:
            print(f"[微信服务] 使用缓存的access_token: {self.access_token[:10]}...")
            return self.access_token
        
        print(f"[微信服务] 开始获取新的access_token")
        # 获取新的access_token
        try:
            url = self.config.get_access_token_url()
            print(f"[微信服务] 请求URL: {url}")
            
            response = requests.get(url)
            print(f"[微信服务] 响应状态码: {response.status_code}")
            
            data = response.json()
            print(f"[微信服务] 响应数据: {data}")
            
            if 'access_token' in data:
                self.access_token = data['access_token']
                # token有效期通常是7200秒，我们提前100秒刷新
                self.token_expires_at = current_time + data.get('expires_in', 7200) - 100
                print(f"[微信服务] 成功获取access_token: {self.access_token[:10]}..., 过期时间: {self.token_expires_at}")
                return self.access_token
            else:
                print(f"[微信服务] 获取access_token失败: {data}")
                return None
                
        except Exception as e:
            print(f"[微信服务] 获取access_token异常: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_user_info(self, openid: str) -> Optional[Dict]:
        """获取用户基本信息"""
        print(f"[微信服务] 开始获取用户信息: {openid}")
        access_token = self.get_access_token()
        if not access_token:
            print(f"[微信服务] 无法获取access_token，无法获取用户信息")
            return None
        
        try:
            url = self.config.get_user_info_url(access_token, openid)
            print(f"[微信服务] 请求用户信息URL: {url}")
            
            response = requests.get(url)
            print(f"[微信服务] 用户信息响应状态码: {response.status_code}")
            
            data = response.json()
            print(f"[微信服务] 用户信息响应数据: {data}")
            
            if 'errcode' not in data:
                print(f"[微信服务] 成功获取用户信息: {data.get('nickname', '未知用户')}")
                return data
            else:
                print(f"[微信服务] 获取用户信息失败: {data}")
                return None
                
        except Exception as e:
            print(f"[微信服务] 获取用户信息异常: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_followers_list(self, next_openid: str = '') -> Optional[Dict]:
        """获取关注者列表"""
        print(f"[微信服务] 开始获取关注者列表，next_openid: {next_openid}")
        access_token = self.get_access_token()
        if not access_token:
            print(f"[微信服务] 无法获取access_token，无法获取关注者列表")
            return None
        
        try:
            url = self.config.get_followers_url(access_token, next_openid)
            print(f"[微信服务] 关注者列表URL: {url}")
            
            response = requests.get(url)
            print(f"[微信服务] 关注者列表响应状态码: {response.status_code}")
            
            data = response.json()
            print(f"[微信服务] 关注者列表响应数据: {data}")
            
            if 'data' in data:
                openids = data['data'].get('openid', [])
                total = data.get('total', 0)
                count = data.get('count', 0)
                print(f"[微信服务] 成功获取关注者列表，总数: {total}, 本次返回: {count}, OpenIDs: {openids[:3]}{'...' if len(openids) > 3 else ''}")
                return data
            else:
                print(f"[微信服务] 获取关注者列表失败: {data}")
                return None
                
        except Exception as e:
            print(f"[微信服务] 获取关注者列表异常: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_all_followers(self) -> List[str]:
        """获取所有关注者的openid列表"""
        all_openids = []
        next_openid = ''
        
        while True:
            result = self.get_followers_list(next_openid)
            if not result:
                break
            
            openids = result['data'].get('openid', [])
            all_openids.extend(openids)
            
            next_openid = result['data'].get('next_openid', '')
            if not next_openid:
                break
        
        return all_openids
    
    def send_custom_message(self, openid: str, message: str) -> bool:
        """发送客服消息"""
        print(f"[微信服务] 开始发送客服消息给用户: {openid}")
        print(f"[微信服务] 消息内容: {message}")
        
        access_token = self.get_access_token()
        if not access_token:
            print(f"[微信服务] 无法获取access_token，无法发送客服消息")
            return False
        
        try:
            url = self.config.get_custom_message_url(access_token)
            print(f"[微信服务] 客服消息URL: {url}")
            
            data = {
                "touser": openid,
                "msgtype": "text",
                "text": {
                    "content": message
                }
            }
            print(f"[微信服务] 发送数据: {data}")
            
            response = requests.post(url, json=data)
            print(f"[微信服务] 客服消息响应状态码: {response.status_code}")
            
            result = response.json()
            print(f"[微信服务] 客服消息响应结果: {result}")
            
            if result.get('errcode') == 0:
                print(f"[微信服务] 客服消息发送成功")
                return True
            else:
                print(f"[微信服务] 发送客服消息失败: {result}")
                return False
                
        except Exception as e:
            print(f"[微信服务] 发送客服消息异常: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_user_is_follower(self, openid: str) -> bool:
        """验证用户是否为公众号关注者"""
        print(f"[微信服务] 开始验证用户是否为关注者: {openid}")
        try:
            user_info = self.get_user_info(openid)
            if user_info and user_info.get('subscribe') == 1:
                print(f"[微信服务] 用户 {openid} 是公众号关注者")
                return True
            else:
                print(f"[微信服务] 用户 {openid} 不是公众号关注者，用户信息: {user_info}")
                return False
        except Exception as e:
            print(f"[微信服务] 验证用户关注状态异常: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_login_session(self, openid: str) -> Tuple[str, int]:
        """创建登录会话"""
        timestamp = int(time.time())
        session_id = self.config.generate_session_id(openid, timestamp)
        return session_id, timestamp
    
    def verify_login_session(self, session_id: str, openid: str, timestamp: int) -> bool:
        """验证登录会话"""
        # 检查会话是否过期
        if self.is_session_expired(timestamp):
            return False
        
        # 验证会话ID
        return self.config.verify_session_id(session_id, openid, timestamp)
    
    def is_session_expired(self, timestamp: int) -> bool:
        """检查会话是否过期"""
        current_time = time.time()
        return (current_time - timestamp) > self.config.session_timeout
    
    def get_user_profile(self, openid: str) -> Optional[Dict]:
        """获取用户资料信息"""
        user_info = self.get_user_info(openid)
        if not user_info:
            return None
        
        # 返回用户资料信息
        profile = {
            'openid': openid,
            'nickname': user_info.get('nickname', ''),
            'headimgurl': user_info.get('headimgurl', ''),
            'sex': user_info.get('sex', 0),  # 0: 未知, 1: 男, 2: 女
            'city': user_info.get('city', ''),
            'province': user_info.get('province', ''),
            'country': user_info.get('country', ''),
            'subscribe_time': user_info.get('subscribe_time', 0),
            'unionid': user_info.get('unionid', '')
        }
        
        return profile
