"""
微信配置文件
"""
import os
from typing import Optional

class WeChatConfig:
    """微信配置类"""
    
    # 微信公众号配置
    APP_ID = os.getenv('WECHAT_APP_ID', 'your_app_id_here')
    APP_SECRET = os.getenv('WECHAT_APP_SECRET', 'your_app_secret_here')
    
    # 微信网页授权配置 - 回调地址
    REDIRECT_URI = os.getenv('WECHAT_REDIRECT_URI', 'http://localhost:5000/wechat/callback')
    
    # 微信API接口
    ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token'
    USER_INFO_URL = 'https://api.weixin.qq.com/sns/userinfo'
    OAUTH2_URL = 'https://open.weixin.qq.com/connect/oauth2/authorize'
    
    @classmethod
    def is_configured(cls) -> bool:
        """检查微信配置是否完整"""
        return (cls.APP_ID != 'your_app_id_here' and 
                cls.APP_SECRET != 'your_app_secret_here' and
                cls.REDIRECT_URI != 'http://localhost:5000/wechat/callback')
    
    @classmethod
    def get_oauth_url(cls, state: str = '') -> str:
        """生成微信网页授权URL"""
        params = {
            'appid': cls.APP_ID,
            'redirect_uri': cls.REDIRECT_URI,
            'response_type': 'code',
            'scope': 'snsapi_userinfo',  # 获取用户基本信息
            'state': state,
            '#wechat_redirect': ''
        }
        
        query_string = '&'.join([f'{k}={v}' for k, v in params.items() if v])
        return f"{cls.OAUTH2_URL}?{query_string}"
