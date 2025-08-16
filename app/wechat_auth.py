"""
微信认证工具模块
"""
import json
import requests
from typing import Dict, Optional, Tuple
from app.wechat_config import WeChatConfig

class WeChatAuth:
    """微信认证处理类"""
    
    def __init__(self):
        self.app_id = WeChatConfig.APP_ID
        self.app_secret = WeChatConfig.APP_SECRET
    
    def get_authorization_url(self, redirect_uri: str = None, state: str = None) -> str:
        """生成微信网页授权URL"""
        if not redirect_uri:
            # 默认回调地址
            redirect_uri = WeChatConfig.REDIRECT_URI
        
        params = {
            'appid': self.app_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'snsapi_userinfo',  # 获取用户基本信息
            'state': state or 'STATE'
        }
        
        # 构建授权URL
        auth_url = 'https://open.weixin.qq.com/connect/oauth2/authorize'
        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        return f"{auth_url}?{query_string}#wechat_redirect"
    
    def get_user_info(self, code: str) -> Optional[Dict]:
        """通过授权码获取用户信息（简化版本）"""
        return self.get_user_info_by_code(code)
    
    def get_access_token(self) -> Optional[str]:
        """获取微信接口调用凭证"""
        try:
            params = {
                'grant_type': 'client_credential',
                'appid': self.app_id,
                'secret': self.app_secret
            }
            
            response = requests.get(WeChatConfig.ACCESS_TOKEN_URL, params=params, timeout=10)
            data = response.json()
            
            if 'access_token' in data:
                return data['access_token']
            else:
                print(f"获取access_token失败: {data}")
                return None
                
        except Exception as e:
            print(f"获取access_token异常: {e}")
            return None
    
    def get_user_info_by_code(self, code: str) -> Optional[Dict]:
        """通过授权码获取用户信息"""
        try:
            # 获取网页授权access_token
            token_url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
            params = {
                'appid': self.app_id,
                'secret': self.app_secret,
                'code': code,
                'grant_type': 'authorization_code'
            }
            
            response = requests.get(token_url, params=params, timeout=10)
            token_data = response.json()
            
            if 'access_token' not in token_data:
                print(f"获取网页授权access_token失败: {token_data}")
                return None
            
            # 获取用户信息
            user_params = {
                'access_token': token_data['access_token'],
                'openid': token_data['openid'],
                'lang': 'zh_CN'
            }
            
            user_response = requests.get(WeChatConfig.USER_INFO_URL, params=user_params, timeout=10)
            user_data = user_response.json()
            
            if 'openid' in user_data:
                return {
                    'openid': user_data['openid'],
                    'nickname': user_data.get('nickname', ''),
                    'headimgurl': user_data.get('headimgurl', ''),
                    'city': user_data.get('city', ''),
                    'province': user_data.get('province', ''),
                    'country': user_data.get('country', ''),
                    'unionid': user_data.get('unionid', ''),
                    'access_token': token_data['access_token']
                }
            else:
                print(f"获取用户信息失败: {user_data}")
                return None
                
        except Exception as e:
            print(f"获取用户信息异常: {e}")
            return None
    
    def verify_signature(self, signature: str, timestamp: str, nonce: str, token: str) -> bool:
        """验证微信服务器签名"""
        import hashlib
        
        # 将token、timestamp、nonce三个参数进行字典序排序
        params = [token, timestamp, nonce]
        params.sort()
        
        # 将三个参数字符串拼接成一个字符串进行sha1加密
        temp_str = ''.join(params)
        hash_str = hashlib.sha1(temp_str.encode('utf-8')).hexdigest()
        
        return hash_str == signature
    
    def is_wechat_browser(self, user_agent: str) -> bool:
        """判断是否为微信浏览器"""
        return 'MicroMessenger' in user_agent
