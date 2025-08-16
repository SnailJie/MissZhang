"""
微信配置文件 - 已认证公众号版本
"""
import os
import time
import hashlib
from typing import Optional, Dict, List

class WeChatConfig:
    """微信配置类 - 适用于已认证公众号"""
    
    # 微信公众号配置
    APP_ID = os.getenv('WECHAT_APP_ID', 'your_app_id_here')
    APP_SECRET = os.getenv('WECHAT_APP_SECRET', 'your_app_secret_here')
    
    # 微信API接口 - 已认证公众号可用
    ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token'
    USER_INFO_URL = 'https://api.weixin.qq.com/cgi-bin/user/info'
    FOLLOWERS_URL = 'https://api.weixin.qq.com/cgi-bin/user/get'
    CUSTOM_MESSAGE_URL = 'https://api.weixin.qq.com/cgi-bin/message/custom/send'
    
    # 网页授权相关（仅用于获取openid，不用于获取用户信息）
    OAUTH2_URL = 'https://open.weixin.qq.com/connect/oauth2/authorize'
    OAUTH2_ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/sns/oauth2/access_token'
    
    # 用户身份识别相关
    LOGIN_KEYWORD = os.getenv('WECHAT_LOGIN_KEYWORD', '登录')
    SESSION_TIMEOUT = int(os.getenv('WECHAT_SESSION_TIMEOUT', '3600'))  # 1小时
    
    @classmethod
    def is_configured(cls) -> bool:
        """检查微信配置是否完整"""
        return (cls.APP_ID != 'your_app_id_here' and 
                cls.APP_SECRET != 'your_app_secret_here')
    
    @classmethod
    def get_access_token_url(cls) -> str:
        """获取access_token的完整URL"""
        return f"{cls.ACCESS_TOKEN_URL}?grant_type=client_credential&appid={cls.APP_ID}&secret={cls.APP_SECRET}"
    
    @classmethod
    def get_user_info_url(cls, access_token: str, openid: str) -> str:
        """获取用户基本信息的完整URL"""
        return f"{cls.USER_INFO_URL}?access_token={access_token}&openid={openid}&lang=zh_CN"
    
    @classmethod
    def get_followers_url(cls, access_token: str, next_openid: str = '') -> str:
        """获取关注者列表的完整URL"""
        url = f"{cls.FOLLOWERS_URL}?access_token={access_token}"
        if next_openid:
            url += f"&next_openid={next_openid}"
        return url
    
    @classmethod
    def get_custom_message_url(cls, access_token: str) -> str:
        """发送客服消息的完整URL"""
        return f"{cls.CUSTOM_MESSAGE_URL}?access_token={access_token}"
    
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
