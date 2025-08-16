"""
用户身份管理模块
"""
import time
from typing import Dict, Optional, Tuple
from .wechat_service import WeChatService

class UserIdentityManager:
    """用户身份管理器"""
    
    def __init__(self):
        self.wechat_service = WeChatService()
        # 内存存储用户会话信息（生产环境建议使用Redis或数据库）
        self.user_sessions = {}  # {session_id: {openid, timestamp, user_info}}
        self.openid_sessions = {}  # {openid: session_id} 用于快速查找
    
    def create_login_session(self, openid: str) -> Optional[str]:
        """创建用户登录会话"""
        try:
            # 验证用户是否为公众号关注者
            if not self.wechat_service.verify_user_is_follower(openid):
                return None
            
            # 创建会话
            session_id, timestamp = self.wechat_service.create_login_session(openid)
            
            # 获取用户信息
            user_info = self.wechat_service.get_user_profile(openid)
            
            # 存储会话信息
            self.user_sessions[session_id] = {
                'openid': openid,
                'timestamp': timestamp,
                'user_info': user_info
            }
            
            # 建立openid到session_id的映射
            self.openid_sessions[openid] = session_id
            
            return session_id
            
        except Exception as e:
            print(f"创建登录会话失败: {e}")
            return None
    
    def verify_session(self, session_id: str) -> Optional[Dict]:
        """验证会话并返回用户信息"""
        if session_id not in self.user_sessions:
            return None
        
        session_data = self.user_sessions[session_id]
        openid = session_data['openid']
        timestamp = session_data['timestamp']
        
        # 验证会话是否有效
        if not self.wechat_service.verify_login_session(session_id, openid, timestamp):
            # 会话无效，清理数据
            self._cleanup_session(session_id)
            return None
        
        return session_data['user_info']
    
    def get_user_by_openid(self, openid: str) -> Optional[Dict]:
        """根据openid获取用户信息"""
        if openid in self.openid_sessions:
            session_id = self.openid_sessions[openid]
            return self.verify_session(session_id)
        return None
    
    def refresh_session(self, session_id: str) -> bool:
        """刷新会话"""
        if session_id not in self.user_sessions:
            return False
        
        session_data = self.user_sessions[session_id]
        openid = session_data['openid']
        
        # 创建新的会话
        new_session_id, new_timestamp = self.wechat_service.create_login_session(openid)
        
        # 更新会话信息
        self.user_sessions[new_session_id] = {
            'openid': openid,
            'timestamp': new_timestamp,
            'user_info': session_data['user_info']
        }
        
        # 更新映射关系
        self.openid_sessions[openid] = new_session_id
        
        # 清理旧会话
        self._cleanup_session(session_id)
        
        return True
    
    def logout(self, session_id: str) -> bool:
        """用户登出"""
        return self._cleanup_session(session_id)
    
    def _cleanup_session(self, session_id: str) -> bool:
        """清理会话数据"""
        if session_id in self.user_sessions:
            openid = self.user_sessions[session_id]['openid']
            
            # 清理映射关系
            if openid in self.openid_sessions:
                del self.openid_sessions[openid]
            
            # 清理会话数据
            del self.user_sessions[session_id]
            return True
        
        return False
    
    def cleanup_expired_sessions(self):
        """清理过期的会话"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session_data in self.user_sessions.items():
            timestamp = session_data['timestamp']
            if self.wechat_service.is_session_expired(timestamp):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self._cleanup_session(session_id)
    
    def get_active_sessions_count(self) -> int:
        """获取活跃会话数量"""
        return len(self.user_sessions)
    
    def get_user_session_info(self, session_id: str) -> Optional[Dict]:
        """获取会话详细信息"""
        if session_id in self.user_sessions:
            session_data = self.user_sessions[session_id].copy()
            # 添加会话状态信息
            session_data['is_expired'] = self.wechat_service.is_session_expired(
                session_data['timestamp']
            )
            return session_data
        return None

# 全局用户身份管理器实例
user_identity_manager = UserIdentityManager()
