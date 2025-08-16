"""
微信配置文件 - 已认证公众号版本
"""
import os
import time
import hashlib
from typing import Optional, Dict, List

class WeChatConfig:
    """微信配置管理类"""
    
    def __init__(self):
        # 微信公众号配置
        self.app_id = os.getenv('WECHAT_APP_ID', 'your_app_id_here')
        self.app_secret = os.getenv('WECHAT_APP_SECRET', '')
        
        # 服务器配置
        self.token = os.getenv('WECHAT_TOKEN', 'mytoken123')  # 添加Token配置
        self.encoding_aes_key = os.getenv('WECHAT_ENCODING_AES_KEY', '')
        
        # 登录配置
        self.login_keyword = os.getenv('WECHAT_LOGIN_KEYWORD', '登录')
        self.session_timeout = int(os.getenv('WECHAT_SESSION_TIMEOUT', '3600'))
        
        # 接口URL配置
        self.base_url = 'https://api.weixin.qq.com'
        self.access_token_url = f'{self.base_url}/cgi-bin/token'
        self.user_info_url = f'{self.base_url}/cgi-bin/user/info'
        self.custom_message_url = f'{self.base_url}/cgi-bin/message/custom/send'
        
        # 消息加解密方式
        self.encrypt_mode = os.getenv('WECHAT_ENCRYPT_MODE', 'plain')  # plain, compatible, safe
        
    @property
    def is_configured(self) -> bool:
        """检查配置是否完整"""
        return bool(self.app_id and self.app_secret and self.app_id != 'your_app_id_here')
    
    @property
    def server_config_summary(self) -> dict:
        """获取服务器配置摘要"""
        return {
            'token': self.token,
            'encoding_aes_key': self.encoding_aes_key,
            'encrypt_mode': self.encrypt_mode,
            'callback_url': '/wechat/message'
        }
    
    def get_access_token_url(self) -> str:
        """获取access_token接口URL"""
        return f'{self.access_token_url}?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}'
    
    def get_user_info_url(self, access_token: str, openid: str) -> str:
        """获取用户信息接口URL"""
        return f'{self.user_info_url}?access_token={access_token}&openid={openid}&lang=zh_CN'
    
    def get_custom_message_url(self, access_token: str) -> str:
        """获取客服消息接口URL"""
        return f'{self.custom_message_url}?access_token={access_token}'
    
    @classmethod
    def generate_session_id(cls, openid: str, timestamp: int = None) -> str:
        """生成会话ID"""
        if timestamp is None:
            timestamp = int(time.time())
        data = f"{openid}_{timestamp}_{cls.APP_SECRET}"
        return hashlib.md5(data.encode()).hexdigest()
    
    @classmethod
    def verify_session_id(cls, session_id: str, openid: str, timestamp: int) -> bool:
        """验证会话ID"""
        expected_session_id = cls.generate_session_id(openid, timestamp)
        return session_id == expected_session_id
    
    @classmethod
    def is_session_expired(cls, timestamp: int) -> bool:
        """检查会话是否过期"""
        current_time = int(time.time())
        return (current_time - timestamp) > cls.SESSION_TIMEOUT
