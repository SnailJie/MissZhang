"""
微信服务类 - 处理已认证公众号的用户身份识别
"""
import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from .wechat_config import WeChatConfig

class WeChatService:
    """微信服务类"""
    
    def __init__(self):
        self.access_token = None
        self.token_expires_at = 0
    
    def get_access_token(self) -> Optional[str]:
        """获取access_token，带缓存机制"""
        current_time = time.time()
        
        # 如果token还有效，直接返回
        if self.access_token and current_time < self.token_expires_at:
            return self.access_token
        
        # 获取新的access_token
        try:
            response = requests.get(WeChatConfig.get_access_token_url())
            data = response.json()
            
            if 'access_token' in data:
                self.access_token = data['access_token']
                # token有效期通常是7200秒，我们提前100秒刷新
                self.token_expires_at = current_time + data.get('expires_in', 7200) - 100
                return self.access_token
            else:
                print(f"获取access_token失败: {data}")
                return None
                
        except Exception as e:
            print(f"获取access_token异常: {e}")
            return None
    
    def get_user_info(self, openid: str) -> Optional[Dict]:
        """获取用户基本信息"""
        access_token = self.get_access_token()
        if not access_token:
            return None
        
        try:
            response = requests.get(WeChatConfig.get_user_info_url(access_token, openid))
            data = response.json()
            
            if 'errcode' not in data:
                return data
            else:
                print(f"获取用户信息失败: {data}")
                return None
                
        except Exception as e:
            print(f"获取用户信息异常: {e}")
            return None
    
    def get_followers_list(self, next_openid: str = '') -> Optional[Dict]:
        """获取关注者列表"""
        access_token = self.get_access_token()
        if not access_token:
            return None
        
        try:
            response = requests.get(WeChatConfig.get_followers_url(access_token, next_openid))
            data = response.json()
            
            if 'data' in data:
                return data
            else:
                print(f"获取关注者列表失败: {data}")
                return None
                
        except Exception as e:
            print(f"获取关注者列表异常: {e}")
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
        access_token = self.get_access_token()
        if not access_token:
            return False
        
        try:
            url = WeChatConfig.get_custom_message_url(access_token)
            data = {
                "touser": openid,
                "msgtype": "text",
                "text": {
                    "content": message
                }
            }
            
            response = requests.post(url, json=data)
            result = response.json()
            
            if result.get('errcode') == 0:
                return True
            else:
                print(f"发送客服消息失败: {result}")
                return False
                
        except Exception as e:
            print(f"发送客服消息异常: {e}")
            return False
    
    def verify_user_is_follower(self, openid: str) -> bool:
        """验证用户是否为公众号关注者"""
        try:
            user_info = self.get_user_info(openid)
            if user_info and user_info.get('subscribe') == 1:
                return True
            return False
        except:
            return False
    
    def create_login_session(self, openid: str) -> Tuple[str, int]:
        """创建登录会话"""
        timestamp = int(time.time())
        session_id = WeChatConfig.generate_session_id(openid, timestamp)
        return session_id, timestamp
    
    def verify_login_session(self, session_id: str, openid: str, timestamp: int) -> bool:
        """验证登录会话"""
        # 检查会话是否过期
        if self.is_session_expired(timestamp):
            return False
        
        # 验证会话ID
        return WeChatConfig.verify_session_id(session_id, openid, timestamp)
    
    def is_session_expired(self, timestamp: int) -> bool:
        """检查会话是否过期"""
        current_time = time.time()
        return (current_time - timestamp) > WeChatConfig.SESSION_TIMEOUT
    
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
