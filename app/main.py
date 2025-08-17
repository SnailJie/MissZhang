from __future__ import annotations

import json
import sqlite3
import re
import os
import time
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List

from flask import Flask, jsonify, render_template, request, redirect, url_for, send_from_directory, session

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 导入微信认证模块
from app.wechat_auth import WeChatAuth
from app.wechat_config import WeChatConfig
from app.wechat_service import WeChatService
from app.user_identity import user_identity_manager

# 导入排班表数据结构
from app.schedule_data import get_mock_schedule_data, get_schedule_data, ScheduleData

# 导入邮件服务
from app.email_service import EmailService

# 排班表数据结构定义
@dataclass
class ScheduleShift:
    """排班班次"""
    position: str  # 岗位，如 "MR1", "MR2" 等
    time_range: str  # 时间范围，如 "07:30-13:00"
    assignments: Dict[str, str]  # 日期到人员姓名的映射
    shift: Optional[str] = None  # 班次类型，如 "上午", "下午", "晚班", "夜班"

@dataclass
class ScheduleTable:
    """排班表"""
    title: str  # 表标题，如 "MRI上午", "MRI下午", "MRI晚班", "周末班"
    shifts: List[ScheduleShift]  # 班次列表
    dates: List[str]  # 日期列表，如 ["8月4日", "8月5日", ...]

@dataclass
class ScheduleData:
    """完整的排班数据"""
    week: str  # 周次，如 "2024-32"
    tables: List[ScheduleTable]  # 排班表列表

# Mock数据 - 基于图片中的排班表
def get_mock_schedule_data(week: str) -> ScheduleData:
    """获取mock排班数据"""
    
    # MRI上午班次
    mri_morning_shifts = [
        ScheduleShift("MR1", "07:30-13:00", {
            "8月4日": "张三", "8月5日": "李四", "8月6日": "王五", "8月7日": "赵六", "8月8日": "钱七"
        }),
        ScheduleShift("MR2", "07:30-13:00", {
            "8月4日": "孙八", "8月5日": "周九", "8月6日": "孙八", "8月7日": "郑十一", "8月8日": "王十二"
        }),
        ScheduleShift("MR3", "07:30-13:00", {
            "8月4日": "孙八", "8月5日": "陈十四", "8月6日": "褚十五", "8月7日": "卫十六", "8月8日": "蒋十七"
        }),
        ScheduleShift("MR4", "07:30-13:00", {
            "8月4日": "沈十八", "8月5日": "韩十九", "8月6日": "杨二十", "8月7日": "朱二一", "8月8日": "秦二二"
        }),
        ScheduleShift("MR5", "07:30-13:00", {
            "8月4日": "尤二三", "8月5日": "孙八", "8月6日": "何二五", "8月7日": "吕二六", "8月8日": "施二七"
        }),
        ScheduleShift("MR6", "07:30-13:00", {
            "8月4日": "张二八", "8月5日": "孔二九", "8月6日": "曹三十", "8月7日": "严三一", "8月8日": "华三二"
        }),
        ScheduleShift("MR7", "07:30-13:00", {
            "8月4日": "金三三", "8月5日": "魏三四", "8月6日": "陶三五", "8月7日": "姜三六", "8月8日": "戚三七"
        }),
        ScheduleShift("MR8", "07:30-13:00", {
            "8月4日": "谢三八", "8月5日": "邹三九", "8月6日": "喻四十", "8月7日": "柏四一", "8月8日": "水四二"
        }),
        ScheduleShift("MR9", "07:30-13:00", {
            "8月4日": "窦四三", "8月5日": "章四四", "8月6日": "云四五", "8月7日": "苏四六", "8月8日": "潘四七"
        }),
        ScheduleShift("MR10", "07:30-13:00", {
            "8月4日": "葛四八", "8月5日": "奚四九", "8月6日": "范五十", "8月7日": "彭五一", "8月8日": "郎五二"
        }),
        ScheduleShift("MR11", "07:30-13:00", {
            "8月4日": "鲁五三", "8月5日": "韦五四", "8月6日": "昌五五", "8月7日": "马五六", "8月8日": "苗五七"
        }),
        ScheduleShift("MR12", "07:30-13:00", {
            "8月4日": "凤五八", "8月5日": "花五九", "8月6日": "方六十", "8月7日": "俞六一", "8月8日": "任六二"
        }),
        ScheduleShift("MR13", "07:30-13:00", {
            "8月4日": "袁六三", "8月5日": "柳六四", "8月6日": "酆六五", "8月7日": "鲍六六", "8月8日": "史六七"
        })
    ]
    
    # MRI下午班次
    mri_afternoon_shifts = [
        ScheduleShift("MR1", "13:00-18:30", {
            "8月4日": "唐六八", "8月5日": "孙八", "8月6日": "廉七十", "8月7日": "岑七一", "8月8日": "薛七二"
        }),
        ScheduleShift("MR2", "13:00-18:30", {
            "8月4日": "雷七三", "8月5日": "贺七四", "8月6日": "倪七五", "8月7日": "汤七六", "8月8日": "滕七七"
        }),
        ScheduleShift("MR3", "13:00-18:30", {
            "8月4日": "殷七八", "8月5日": "罗七九", "8月6日": "毕八十", "8月7日": "郝八一", "8月8日": "邬八二"
        }),
        ScheduleShift("MR4", "13:00-18:30", {
            "8月4日": "安八三", "8月5日": "常八四", "8月6日": "孙八", "8月7日": "于八六", "8月8日": "时八七"
        }),
        ScheduleShift("MR5", "13:00-18:30", {
            "8月4日": "傅八八", "8月5日": "皮八九", "8月6日": "卞九十", "8月7日": "齐九一", "8月8日": "康九二"
        }),
        ScheduleShift("MR6", "13:00-18:30", {
            "8月4日": "伍九三", "8月5日": "孙八", "8月6日": "孙八", "8月7日": "卜九六", "8月8日": "顾九七"
        }),
        ScheduleShift("MR7", "13:00-18:30", {
            "8月4日": "孟九八", "8月5日": "平九九", "8月6日": "黄一百", "8月7日": "和百一", "8月8日": "穆百二"
        }),
        ScheduleShift("MR8", "13:00-18:30", {
            "8月4日": "萧百三", "8月5日": "尹百四", "8月6日": "姚百五", "8月7日": "邵百六", "8月8日": "湛百七"
        }),
        ScheduleShift("MR9", "13:00-18:30", {
            "8月4日": "汪百八", "8月5日": "祁百九", "8月6日": "毛百十", "8月7日": "禹百十一", "8月8日": "狄百十二"
        }),
        ScheduleShift("MR10", "13:00-18:30", {
            "8月4日": "米百十三", "8月5日": "贝百十四", "8月6日": "明百十五", "8月7日": "臧百十六", "8月8日": "计百十七"
        }),
        ScheduleShift("MR11", "13:00-18:30", {
            "8月4日": "伏百十八", "8月5日": "成百十九", "8月6日": "戴百二十", "8月7日": "谈百二一", "8月8日": "宋百二二"
        }),
        ScheduleShift("MR12", "13:00-18:30", {
            "8月4日": "茅百二三", "8月5日": "庞百二四", "8月6日": "熊百二五", "8月7日": "纪百二六", "8月8日": "舒百二七"
        }),
        ScheduleShift("MR13", "13:00-18:30", {
            "8月4日": "屈百二八", "8月5日": "项百二九", "8月6日": "祝百三十", "8月7日": "董百三一", "8月8日": "梁百三二"
        })
    ]
    
    # MRI晚班班次
    mri_evening_shifts = [
        ScheduleShift("MR1", "18:30-23:00", {
            "8月4日": "杜百三三", "8月5日": "孙八", "8月6日": "蓝百三五", "8月7日": "闵百三六", "8月8日": "席百三七"
        }),
        ScheduleShift("MR2", "18:30-23:00", {
            "8月4日": "季百三八", "8月5日": "孙八三九", "8月6日": "强百四十", "8月7日": "贾百四一", "8月8日": "路百四二"
        }),
        ScheduleShift("MR3", "18:30-23:00", {
            "8月4日": "娄百四三", "8月5日": "危百四四", "8月6日": "江百四五", "8月7日": "童百四六", "8月8日": "颜百四七"
        }),
        ScheduleShift("MR4", "18:30-23:00", {
            "8月4日": "郭百四八", "8月5日": "梅百四九", "8月6日": "孙八五十", "8月7日": "林百五一", "8月8日": "刁百五二"
        }),
        ScheduleShift("MR5", "18:30-23:00", {
            "8月4日": "钟百五三", "8月5日": "徐百五四", "8月6日": "邱百五五", "8月7日": "骆百五六", "8月8日": "高百五七"
        }),
        ScheduleShift("MR6", "18:30-23:00", {
            "8月4日": "夏百五八", "8月5日": "蔡百五九", "8月6日": "田百六十", "8月7日": "樊百六一", "8月8日": "胡百六二"
        }),
        ScheduleShift("MR7", "18:30-23:00", {
            "8月4日": "凌百六三", "8月5日": "霍百六四", "8月6日": "虞百六五", "8月7日": "万百六六", "8月8日": "支百六七"
        }),
        ScheduleShift("MR8", "18:30-23:00", {
            "8月4日": "柯百六八", "8月5日": "昝百六九", "8月6日": "管百七十", "8月7日": "卢百七一", "8月8日": "莫百七二"
        }),
        ScheduleShift("MR9", "18:30-23:00", {
            "8月4日": "经百七三", "8月5日": "房百七四", "8月6日": "裘百七五", "8月7日": "缪百七六", "8月8日": "干百七七"
        }),
        ScheduleShift("MR10", "18:30-23:00", {
            "8月4日": "解百七八", "8月5日": "应百七九", "8月6日": "宗百八十", "8月7日": "丁百八一", "8月8日": "宣百八二"
        }),
        ScheduleShift("MR11", "18:30-23:00", {
            "8月4日": "贲百八三", "8月5日": "邓百八四", "8月6日": "郁百八五", "8月7日": "单百八六", "8月8日": "杭百八七"
        })
    ]
    
    # 周末班班次
    weekend_shifts = [
        ScheduleShift("MR1", "07:30-13:00", {
            "8月9日": "洪百八八", "8月10日": "包百八九"
        }),
        ScheduleShift("MR2", "07:30-13:00", {
            "8月9日": "诸百九十", "8月10日": "左百九一"
        }),
        ScheduleShift("MR3", "07:30-13:00", {
            "8月9日": "石百九二", "8月10日": "崔百九三"
        }),
        ScheduleShift("MR4", "07:30-13:00", {
            "8月9日": "吉百九四", "8月10日": "钮百九五"
        }),
        ScheduleShift("MR5", "07:30-13:00", {
            "8月9日": "龚百九六", "8月10日": "程百九七"
        }),
        ScheduleShift("MR6", "07:30-13:00", {
            "8月9日": "孙八", "8月10日": "邢百九九"
        }),
        ScheduleShift("MR7", "07:30-13:00", {
            "8月9日": "滑二百", "8月10日": "裴二百一"
        }),
        ScheduleShift("MR8", "07:30-13:00", {
            "8月9日": "陆二百二", "8月10日": "荣二百三"
        }),
        ScheduleShift("MR9", "07:30-13:00", {
            "8月9日": "翁二百四", "8月10日": "荀二百五"
        }),
        ScheduleShift("MR10", "07:30-13:00", {
            "8月9日": "羊二百六", "8月10日": "於二百七"
        }),
        ScheduleShift("MR11", "07:30-13:00", {
            "8月9日": "惠二百八", "8月10日": "甄二百九"
        }),
        ScheduleShift("MR12", "07:30-13:00", {
            "8月9日": "曲二百十", "8月10日": "家二百十一"
        }),
        ScheduleShift("晚班行政班", "18:30-23:00", {
            "8月9日": "孙八", "8月10日": "芮二百十三"
        }),
        ScheduleShift("补休周末班", "全天", {
            "8月9日": "羿二百十四", "8月10日": "储二百十五"
        })
    ]
    
    # 创建排班表
    mri_morning_table = ScheduleTable("MRI上午", mri_morning_shifts, ["8月4日", "8月5日", "8月6日", "8月7日", "8月8日"])
    mri_afternoon_table = ScheduleTable("MRI下午", mri_afternoon_shifts, ["8月4日", "8月5日", "8月6日", "8月7日", "8月8日"])
    mri_evening_table = ScheduleTable("MRI晚班", mri_evening_shifts, ["8月4日", "8月5日", "8月6日", "8月7日", "8月8日"])
    weekend_table = ScheduleTable("周末班", weekend_shifts, ["8月9日", "8月10日"])
    
    return ScheduleData(week, [mri_morning_table, mri_afternoon_table, mri_evening_table, weekend_table])

BASE_DIR: Path = Path(__file__).resolve().parents[1]
DATA_DIR: Path = BASE_DIR / "data"
DB_PATH: Path = DATA_DIR / "app.db"
SCHEDULES_DIR: Path = DATA_DIR / "schedules"
ALLOWED_IMAGE_EXTENSIONS = ("webp", "png", "jpg", "jpeg")

app = Flask(
    __name__,
    template_folder=str((Path(__file__).parent / "templates")),
    static_folder=str((Path(__file__).parent / "static")),
)

# Configure Flask session
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your_secret_key_here')

# Configure file upload limits
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit for file uploads

# Initialize WeChat services
wechat_config = WeChatConfig()
wechat_auth = WeChatAuth()
wechat_service = WeChatService()

# Initialize Email service
email_service = EmailService()


# Error handlers for file upload
@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        'error': '文件过大',
        'message': '上传的文件超过16MB限制，请压缩图片后重试',
        'max_size': '16MB'
    }), 413


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def ensure_schedules_dir() -> None:
    ensure_data_dir()
    SCHEDULES_DIR.mkdir(parents=True, exist_ok=True)


def init_db() -> None:
    ensure_data_dir()
    with sqlite3.connect(DB_PATH) as conn:
        # 联系消息表
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        
        # 用户表 - 支持多用户
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                openid TEXT UNIQUE NOT NULL,
                nickname TEXT,
                avatar_url TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        
        # 用户档案表 - 关联到用户ID
        conn.execute("DROP TABLE IF EXISTS user_profiles")
        conn.execute(
            """
            CREATE TABLE user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                hospital TEXT NOT NULL,
                department TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        
        # 手动填写的排班数据表
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS manual_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week TEXT NOT NULL,
                date TEXT NOT NULL,
                shift TEXT NOT NULL,
                position TEXT,
                staff_name TEXT NOT NULL,
                schedule_type TEXT NOT NULL CHECK (schedule_type IN ('weekday', 'weekend')),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        
        # 创建索引
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_openid ON users(openid)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_manual_schedules_week ON manual_schedules(week)")
        
        conn.commit()


@dataclass
class ContactPayload:
    name: str
    email: str
    message: str


def parse_contact_payload(payload: Optional[Dict[str, Any]]) -> Tuple[Optional[ContactPayload], Optional[str]]:
    if not payload:
        return None, "请求体不能为空"

    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip()
    message = (payload.get("message") or "").strip()

    if not name or not email or not message:
        return None, "请填写姓名、邮箱和留言"

    if "@" not in email or "." not in email:
        return None, "邮箱格式不正确"

    if len(name) > 100:
        return None, "姓名过长"

    if len(email) > 200:
        return None, "邮箱过长"

    if len(message) > 5000:
        return None, "留言过长"

    return ContactPayload(name=name, email=email, message=message), None


# ---------- Main Routes ----------

# ---------- WeChat Authentication Routes ----------

@app.route("/wechat/login")
def wechat_login():
    """微信登录入口 - 新版本"""
    # 检查是否已配置微信
    if not wechat_config.is_configured:
        return render_template("wechat_login.html", 
                             login_keyword=wechat_config.login_keyword,
                             error="微信配置未完成")
    
    # return render_template("wechat_login.html", 
    #                      login_keyword=wechat_config.login_keyword)


@app.route("/wechat/callback")
def wechat_callback():
    """微信授权回调"""
    try:
        # 获取授权码
        code = request.args.get('code')
        if not code:
            return jsonify({"error": "授权失败"}), 400
        
        # 通过授权码获取用户信息
        user_info = wechat_auth.get_user_info(code)
        if not user_info:
            return jsonify({"error": "获取用户信息失败"}), 400
        
        # 保存或更新用户信息
        user_id = save_or_update_user(user_info)
        
        # 设置用户会话
        session['user_id'] = user_id
        session['openid'] = user_info['openid']
        session['nickname'] = user_info.get('nickname', '')
        
        # 重定向到个人主页
        return redirect(url_for('profile'))
        
    except Exception as e:
        print(f"微信回调处理失败: {e}")
        return jsonify({"error": "登录失败，请重试"}), 500


@app.route("/wechat/logout")
def wechat_logout():
    """微信登出"""
    session.clear()
    return redirect(url_for('index'))


@app.route("/wechat/check_login_status", methods=["POST"])
def wechat_check_login_status():
    """检查用户登录状态"""
    try:
        print(f"[登录状态检查] 收到检查请求")
        data = request.get_json()
        if not data:
            print(f"[登录状态检查] 请求数据为空")
            return jsonify({"success": False, "message": "请求数据不能为空"})
        
        print(f"[登录状态检查] 请求数据: {data}")
        
        # 检查是否有活跃的登录会话
        # 这里我们需要检查是否有用户通过微信公众号发送了登录关键词
        # 由于微信消息是异步的，我们需要在用户身份管理器中维护一个状态
        
        # 获取所有活跃会话
        active_sessions = user_identity_manager.get_all_active_sessions()
        print(f"[登录状态检查] 活跃会话数量: {len(active_sessions)}")
        
        if active_sessions:
            # 找到最新的会话
            latest_session = max(active_sessions, key=lambda x: x['timestamp'])
            print(f"[登录状态检查] 最新会话: {latest_session}")
            
            # 检查会话是否过期
            if not user_identity_manager.is_session_expired(latest_session['session_id']):
                print(f"[登录状态检查] 会话有效，返回用户信息")
                return jsonify({
                    "success": True,
                    "user_info": latest_session['user_info'],
                    "session_id": latest_session['session_id'],
                    "message": "登录成功"
                })
            else:
                print(f"[登录状态检查] 会话已过期")
                # 清理过期会话
                user_identity_manager.cleanup_expired_sessions()
        
        print(f"[登录状态检查] 没有有效的登录会话")
        return jsonify({
            "success": False, 
            "message": "请向公众号发送关键词进行登录"
        })
        
    except Exception as e:
        print(f"[登录状态检查] 检查登录状态失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": "检查失败"})


@app.route("/wechat/manual_login", methods=["POST"])
def wechat_manual_login():
    """手动登录接口（开发测试用）"""
    try:
        data = request.get_json()
        if not data or not data.get('openid'):
            return jsonify({"success": False, "message": "请提供OpenID"})
        
        openid = data['openid'].strip()
        
        # 验证用户是否为公众号关注者
        if not wechat_service.verify_user_is_follower(openid):
            return jsonify({"success": False, "message": "该用户未关注公众号"})
        
        # 创建登录会话
        session_id = user_identity_manager.create_login_session(openid)
        if not session_id:
            return jsonify({"success": False, "message": "创建会话失败"})
        
        # 获取用户信息
        user_info = wechat_service.get_user_profile(openid)
        
        # 设置会话
        session['session_id'] = session_id
        session['openid'] = openid
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "user_info": user_info
        })
        
    except Exception as e:
        print(f"手动登录失败: {e}")
        return jsonify({"success": False, "message": "登录失败"})


@app.route("/wechat/message", methods=["POST", "GET"])
def wechat_message():
    """处理微信公众号消息"""
    try:
        print(f"[微信消息] 收到请求: {request.method}")
        print(f"[微信消息] 请求头: {dict(request.headers)}")
        print(f"[微信消息] 请求参数: {dict(request.args)}")
        
        # GET请求用于微信服务器配置验证
        if request.method == 'GET':
            signature = request.args.get('signature', '')
            timestamp = request.args.get('timestamp', '')
            nonce = request.args.get('nonce', '')
            echostr = request.args.get('echostr', '')
            
            print(f"[微信验证] 收到验证请求: signature={signature}, timestamp={timestamp}, nonce={nonce}, echostr={echostr}")
            
            # 验证微信服务器签名
            if wechat_auth.verify_signature(signature, timestamp, nonce, wechat_config.token):
                print(f"[微信验证] 签名验证成功")
                return echostr
            else:
                print(f"[微信验证] 签名验证失败")
                return "签名验证失败", 403
        
        # POST请求处理用户消息
        print(f"[微信消息] 处理POST消息")
        
        # 解析XML消息
        xml_data = request.data.decode('utf-8')
        print(f"[微信消息] 收到XML数据: {xml_data}")
        
        # 简单的XML解析（生产环境建议使用xml.etree.ElementTree）
        if '<MsgType><![CDATA[text]]></MsgType>' in xml_data:
            print(f"[微信消息] 检测到文本消息")
            
            # 提取消息内容
            content_start = xml_data.find('<Content><![CDATA[') + 18
            content_end = xml_data.find(']]></Content>')
            if content_start > 17 and content_end > content_start:
                content = xml_data[content_start:content_end]
                print(f"[微信消息] 消息内容: '{content}'")
                
                # 检查是否为登录关键词
                if content == wechat_config.login_keyword:
                    print(f"[微信消息] 检测到登录关键词: '{wechat_config.login_keyword}'")
                    
                    # 提取openid
                    openid_start = xml_data.find('<FromUserName><![CDATA[') + 20
                    openid_end = xml_data.find(']]></FromUserName>')
                    if openid_start > 19 and openid_end > openid_start:
                        openid = xml_data[openid_start:openid_end]
                        print(f"[微信消息] 提取到OpenID: {openid}")
                        
                        # 验证用户是否为公众号关注者
                        print(f"[微信消息] 开始验证用户是否为关注者")
                        is_follower = wechat_service.verify_user_is_follower(openid)
                        print(f"[微信消息] 用户关注状态: {is_follower}")
                        
                        if is_follower:
                            print(f"[微信消息] 用户验证成功，开始创建登录会话")
                            
                            # 创建登录会话
                            session_id = user_identity_manager.create_login_session(openid)
                            print(f"[微信消息] 会话创建结果: {session_id}")
                            
                            if session_id:
                                print(f"[微信消息] 会话创建成功，开始发送客服消息")
                                
                                # 发送登录成功消息
                                message_sent = wechat_service.send_custom_message(
                                    openid, 
                                    f"登录成功！您的会话ID是：{session_id}"
                                )
                                print(f"[微信消息] 客服消息发送结果: {message_sent}")
                                
                                # 返回成功响应
                                response_xml = f"""<xml>
                                    <ToUserName><![CDATA[{openid}]]></ToUserName>
                                    <FromUserName><![CDATA[{wechat_config.app_id}]]></FromUserName>
                                    <CreateTime>{int(time.time())}</CreateTime>
                                    <MsgType><![CDATA[text]]></MsgType>
                                    <Content><![CDATA[登录成功！请返回网页刷新页面。]]></Content>
                                </xml>"""
                                print(f"[微信消息] 返回成功响应XML")
                                return response_xml
                            else:
                                print(f"[微信消息] 会话创建失败")
                        else:
                            print(f"[微信消息] 用户未关注公众号")
                    else:
                        print(f"[微信消息] 无法提取OpenID")
                else:
                    print(f"[微信消息] 消息内容不是登录关键词")
            else:
                print(f"[微信消息] 无法提取消息内容")
        else:
            print(f"[微信消息] 不是文本消息")
        
        # 默认回复
        default_response = f"""<xml>
            <ToUserName><![CDATA[{request.form.get('FromUserName', '')}]]></ToUserName>
            <FromUserName><![CDATA[{wechat_config.app_id}]]></FromUserName>
            <CreateTime>{int(time.time())}</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[请发送"{wechat_config.login_keyword}"进行登录]]></Content>
        </xml>"""
        print(f"[微信消息] 返回默认回复")
        return default_response
        
    except Exception as e:
        print(f"[微信消息] 处理微信消息失败: {e}")
        import traceback
        traceback.print_exc()
        return "success"


# ---------- WeChat Menu Management Routes ----------

@app.route("/wechat/menu/create", methods=["POST"])
def create_wechat_menu():
    """创建微信公众号自定义菜单"""
    try:
        print("[菜单管理] 开始创建微信自定义菜单")
        
        # 检查是否已配置微信
        if not wechat_config.is_configured:
            return jsonify({
                "success": False, 
                "message": "微信配置未完成，请先配置WECHAT_APP_ID和WECHAT_APP_SECRET"
            }), 400
        
        # 从请求中获取自定义菜单数据（可选）
        menu_data = None
        if request.is_json:
            data = request.get_json()
            menu_data = data.get('menu_data') if data else None
        
        # 创建菜单
        success = wechat_service.create_custom_menu(menu_data)
        
        if success:
            print("[菜单管理] 微信自定义菜单创建成功")
            return jsonify({
                "success": True,
                "message": "自定义菜单创建成功，菜单将在24小时内生效"
            })
        else:
            print("[菜单管理] 微信自定义菜单创建失败")
            return jsonify({
                "success": False,
                "message": "创建自定义菜单失败，请检查微信配置和网络连接"
            }), 500
            
    except Exception as e:
        print(f"[菜单管理] 创建微信自定义菜单异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"创建菜单异常: {str(e)}"
        }), 500


@app.route("/wechat/menu/get", methods=["GET"])
def get_wechat_menu():
    """获取当前微信公众号自定义菜单"""
    try:
        print("[菜单管理] 开始获取微信自定义菜单")
        
        # 检查是否已配置微信
        if not wechat_config.is_configured:
            return jsonify({
                "success": False, 
                "message": "微信配置未完成，请先配置WECHAT_APP_ID和WECHAT_APP_SECRET"
            }), 400
        
        # 获取菜单
        menu_info = wechat_service.get_custom_menu()
        
        if menu_info:
            print("[菜单管理] 成功获取微信自定义菜单")
            return jsonify({
                "success": True,
                "message": "获取自定义菜单成功",
                "data": menu_info
            })
        else:
            print("[菜单管理] 获取微信自定义菜单失败或菜单不存在")
            return jsonify({
                "success": False,
                "message": "获取自定义菜单失败或菜单不存在"
            }), 404
            
    except Exception as e:
        print(f"[菜单管理] 获取微信自定义菜单异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"获取菜单异常: {str(e)}"
        }), 500


@app.route("/wechat/menu/delete", methods=["POST"])
def delete_wechat_menu():
    """删除微信公众号自定义菜单"""
    try:
        print("[菜单管理] 开始删除微信自定义菜单")
        
        # 检查是否已配置微信
        if not wechat_config.is_configured:
            return jsonify({
                "success": False, 
                "message": "微信配置未完成，请先配置WECHAT_APP_ID和WECHAT_APP_SECRET"
            }), 400
        
        # 删除菜单
        success = wechat_service.delete_custom_menu()
        
        if success:
            print("[菜单管理] 微信自定义菜单删除成功")
            return jsonify({
                "success": True,
                "message": "自定义菜单删除成功，菜单将在24小时内消失"
            })
        else:
            print("[菜单管理] 微信自定义菜单删除失败")
            return jsonify({
                "success": False,
                "message": "删除自定义菜单失败，请检查微信配置和网络连接"
            }), 500
            
    except Exception as e:
        print(f"[菜单管理] 删除微信自定义菜单异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"删除菜单异常: {str(e)}"
        }), 500


@app.route("/wechat/menu")
def wechat_menu_management():
    """微信菜单管理页面"""
    return render_template("wechat_menu.html", 
                         wechat_configured=wechat_config.is_configured)


def save_or_update_user(user_info: Dict[str, Any]) -> int:
    """保存或更新用户信息，返回用户ID"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # 检查用户是否已存在
            cursor = conn.execute(
                "SELECT id FROM users WHERE openid = ?",
                (user_info['openid'],)
            )
            existing_user = cursor.fetchone()
            
            if existing_user:
                # 更新现有用户
                user_id = existing_user[0]
                conn.execute(
                    """
                    UPDATE users 
                    SET nickname = ?, avatar_url = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        user_info.get('nickname', ''),
                        user_info.get('headimgurl', ''),
                        datetime.utcnow().isoformat(),
                        user_id
                    )
                )
            else:
                # 创建新用户
                cursor = conn.execute(
                    """
                    INSERT INTO users (openid, nickname, avatar_url, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        user_info['openid'],
                        user_info.get('nickname', ''),
                        user_info.get('headimgurl', ''),
                        datetime.utcnow().isoformat(),
                        datetime.utcnow().isoformat()
                    )
                )
                user_id = cursor.lastrowid
            
            conn.commit()
            return user_id
            
    except Exception as e:
        print(f"保存用户信息失败: {e}")
        raise


def save_or_update_user_from_openid(openid: str, user_info: Dict[str, Any]) -> int:
    """根据openid保存或更新用户信息，返回用户ID"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # 检查用户是否已存在
            cursor = conn.execute(
                "SELECT id FROM users WHERE openid = ?",
                (openid,)
            )
            existing_user = cursor.fetchone()
            
            if existing_user:
                # 更新现有用户
                user_id = existing_user[0]
                conn.execute(
                    """
                    UPDATE users 
                    SET nickname = ?, avatar_url = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        user_info.get('nickname', ''),
                        user_info.get('headimgurl', ''),
                        datetime.utcnow().isoformat(),
                        user_id
                    )
                )
            else:
                # 创建新用户
                cursor = conn.execute(
                    """
                    INSERT INTO users (openid, nickname, avatar_url, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        openid,
                        user_info.get('nickname', ''),
                        user_info.get('headimgurl', ''),
                        datetime.utcnow().isoformat(),
                        datetime.utcnow().isoformat()
                    )
                )
                user_id = cursor.lastrowid
            
            conn.commit()
            return user_id
            
    except Exception as e:
        print(f"保存用户信息失败: {e}")
        raise


def get_user_profile_by_user_id(user_id: int) -> Dict[str, str]:
    """根据用户ID获取用户档案信息"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(
                "SELECT name, hospital, department FROM user_profiles WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return {
                    "name": row[0],
                    "hospital": row[1],
                    "department": row[2]
                }
            else:
                return {}
                
    except Exception as e:
        print(f"获取用户档案失败: {e}")
        return {}


def get_current_user() -> Optional[Dict[str, Any]]:
    """获取当前登录用户信息 - 新版本"""
    # 优先检查新的会话系统
    if 'session_id' in session and 'openid' in session:
        session_id = session['session_id']
        openid = session['openid']
        
        # 验证会话
        user_info = user_identity_manager.verify_session(session_id)
        if user_info:
            # 从数据库获取或创建用户记录
            user_id = save_or_update_user_from_openid(openid, user_info)
            
            # 获取用户档案信息
            profile_info = get_user_profile_by_user_id(user_id)
            
            return {
                "id": user_id,
                "openid": openid,
                "nickname": user_info.get('nickname', ''),
                "avatar_url": user_info.get('headimgurl', ''),
                "created_at": user_info.get('subscribe_time', ''),
                "name": profile_info.get('name', ''),
                "hospital": profile_info.get('hospital', ''),
                "department": profile_info.get('department', '')
            }
    
    # 兼容旧版本的session系统
    if 'user_id' in session:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.execute(
                    """
                    SELECT u.id, u.openid, u.nickname, u.avatar_url, u.created_at,
                           up.name, up.hospital, up.department
                    FROM users u
                    LEFT JOIN user_profiles up ON u.id = up.user_id
                    WHERE u.id = ?
                    """,
                    (session['user_id'],)
                )
                row = cursor.fetchone()
                
                if row:
                    return {
                        "id": row[0],
                        "openid": row[1],
                        "nickname": row[2],
                        "avatar_url": row[3],
                        "created_at": row[4],
                        "name": row[5],
                        "hospital": row[6],
                        "department": row[7]
                    }
                else:
                    # 用户不存在，清除会话
                    session.clear()
                    return None
                    
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            session.clear()
            return None
    
    return None


def require_login(f):
    """登录验证装饰器"""
    def decorated_function(*args, **kwargs):
        if not get_current_user():
            return redirect(url_for('wechat_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


# ---------- Schedules helpers ----------

def get_current_week_str() -> str:
    iso_year, iso_week, _ = date.today().isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def generate_week_options(num_weeks_back: int = 52, num_weeks_forward: int = 52) -> List[Dict[str, str]]:
    """生成周次选项列表，包括过去和未来的周次
    
    Args:
        num_weeks_back: 向前生成的周数（默认52周，约1年）
        num_weeks_forward: 向后生成的周数（默认52周，约1年）
    
    Returns:
        包含周次信息的字典列表，每个字典包含：
        - value: 周次值，如 "2025-W32"
        - label: 显示标签，如 "2025年第32周 (08月11日-08月17日)"
        - filename: 文件名格式，如 "2025-W32-0811-0817"
    """
    from datetime import timedelta
    
    today = date.today()
    current_iso_year, current_iso_week, _ = today.isocalendar()
    
    week_options = []
    
    # 生成过去的周次
    for i in range(num_weeks_back, 0, -1):
        target_date = today - timedelta(weeks=i)
        iso_year, iso_week, _ = target_date.isocalendar()
        
        # 计算该周的开始和结束日期
        start_of_week = target_date - timedelta(days=target_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        # 生成文件名格式：2025-W32-0811-0817
        start_str = start_of_week.strftime("%m%d")
        end_str = end_of_week.strftime("%m%d")
        filename = f"{iso_year}-W{iso_week:02d}-{start_str}-{end_str}"
        
        # 生成显示标签
        label = f"{iso_year}年第{iso_week:02d}周 ({start_of_week.strftime('%m月%d日')}-{end_of_week.strftime('%m月%d日')})"
        
        week_options.append({
            "value": f"{iso_year}-W{iso_week:02d}",
            "label": label,
            "filename": filename
        })
    
    # 添加当前周
    start_of_current_week = today - timedelta(days=today.weekday())
    end_of_current_week = start_of_current_week + timedelta(days=6)
    start_str = start_of_current_week.strftime("%m%d")
    end_str = end_of_current_week.strftime("%m%d")
    current_filename = f"{current_iso_year}-W{current_iso_week:02d}-{start_str}-{end_str}"
    current_label = f"{current_iso_year}年第{current_iso_week:02d}周 ({start_of_current_week.strftime('%m月%d日')}-{end_of_current_week.strftime('%m月%d日')}) [当前]"
    
    week_options.append({
        "value": f"{current_iso_year}-W{current_iso_week:02d}",
        "label": current_label,
        "filename": current_filename
    })
    
    # 生成未来的周次
    for i in range(1, num_weeks_forward + 1):
        target_date = today + timedelta(weeks=i)
        iso_year, iso_week, _ = target_date.isocalendar()
        
        # 计算该周的开始和结束日期
        start_of_week = target_date - timedelta(days=target_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        # 生成文件名格式：2025-W32-0811-0817
        start_str = start_of_week.strftime("%m%d")
        end_str = end_of_week.strftime("%m%d")
        filename = f"{iso_year}-W{iso_week:02d}-{start_str}-{end_str}"
        
        # 生成显示标签
        label = f"{iso_year}年第{iso_week:02d}周 ({start_of_week.strftime('%m月%d日')}-{end_of_week.strftime('%m月%d日')})"
        
        week_options.append({
            "value": f"{iso_year}-W{iso_week:02d}",
            "label": label,
            "filename": filename
        })
    
    return week_options


def is_valid_week_string(week_str: str) -> bool:
    # HTML input type="week" yields like "2025-W03"
    return bool(re.fullmatch(r"\d{4}-W\d{2}", week_str))


def find_existing_schedule_path(week_str: str) -> Optional[Path]:
    for ext in ALLOWED_IMAGE_EXTENSIONS:
        candidate = SCHEDULES_DIR / f"{week_str}.{ext}"
        if candidate.exists():
            return candidate
    return None


# ---------- Routes ----------

@app.get("/")
def index() -> str:
    user_info = get_current_user()
    return render_template("index.html", user_info=user_info)


@app.get("/about")
def about():
    user_info = get_current_user()
    return render_template("about.html", user_info=user_info)


@app.get("/schedule")
# @require_login
def schedule():
    # 获取用户信息，用于检查是否已设置姓名
    user_info = get_current_user()
    return render_template("schedule.html", user_info=user_info)


# Serve saved schedule images
@app.get("/schedules/<path:filename>")
def serve_schedule_image(filename: str):
    ensure_schedules_dir()
    return send_from_directory(SCHEDULES_DIR, filename)


# Insider page: preview or upload schedule image by week
@app.route("/insider", methods=["GET", "POST"])
# @require_login
def insider():
    ensure_schedules_dir()
    user_info = get_current_user()

    if request.method == "POST":
        week_str = (request.form.get("week") or "").strip()
        image_file = request.files.get("image")

        # 添加调试信息
        print(f"DEBUG: Received week_str: '{week_str}'")
        print(f"DEBUG: week_str type: {type(week_str)}")
        print(f"DEBUG: week_str length: {len(week_str)}")
        print(f"DEBUG: is_valid_week_string result: {is_valid_week_string(week_str)}")

        if not week_str or not is_valid_week_string(week_str):
            error_msg = f"请选择正确的周，例如 2025-W03。当前值: '{week_str}'"
            return render_template("insider.html", error=error_msg, week=week_str or get_current_week_str(), user_info=user_info)

        if not image_file or image_file.filename == "":
            return render_template("insider.html", error="请上传排班表图片", week=week_str, user_info=user_info)

        # Determine extension
        ext = (Path(image_file.filename).suffix or "").lower().lstrip(".")
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            return render_template(
                "insider.html",
                error=f"不支持的图片格式: .{ext}，请上传: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}",
                week=week_str,
                user_info=user_info
            )

        # 根据选择的周次生成文件名
        week_options = generate_week_options()
        selected_week = None
        
        # 查找匹配的周次选项
        for option in week_options:
            if option["value"] == week_str:
                selected_week = option
                break
        
        if not selected_week:
            error_msg = f"无效的周次选择: {week_str}"
            return render_template("insider.html", error=error_msg, week=week_str, user_info=user_info)
        
        # 使用生成的文件名格式保存文件
        filename = selected_week["filename"]
        save_path = SCHEDULES_DIR / f"{filename}.{ext}"
        
        # 删除同名的旧文件（不同扩展名）
        for old_ext in ALLOWED_IMAGE_EXTENSIONS:
            old_path = SCHEDULES_DIR / f"{filename}.{old_ext}"
            if old_path.exists():
                try:
                    old_path.unlink()
                except Exception:
                    pass
        
        image_file.save(save_path)
        print(f"文件已保存为: {save_path}")

        # 发送邮件通知
        try:
            week_info = {
                "label": selected_week["label"],
                "filename": f"{filename}.{ext}",
                "value": week_str
            }
            
            email_sent = email_service.send_schedule_notification(
                week_info=week_info,
                image_path=save_path,
                user_info=user_info
            )
            
            if email_sent:
                print(f"邮件通知发送成功: {week_info['label']}")
            else:
                print(f"邮件通知发送失败: {week_info['label']}")
                
        except Exception as e:
            print(f"发送邮件通知时出错: {e}")

        return redirect(url_for("insider", week=week_str))

    # GET
    week_str = (request.args.get("week") or get_current_week_str()).strip()
    if not is_valid_week_string(week_str):
        week_str = get_current_week_str()

    existing_path = find_existing_schedule_path(week_str)
    image_url: Optional[str] = None
    if existing_path:
        image_url = url_for("serve_schedule_image", filename=existing_path.name)

    return render_template("insider.html", week=week_str, image_url=image_url, user_info=user_info)


def get_available_schedules() -> List[Dict[str, str]]:
    """获取所有可用的排班文件列表，并转换为友好格式"""
    ensure_schedules_dir()
    schedules = []
    
    # 查找所有CSV文件
    for csv_file in SCHEDULES_DIR.glob("*.csv"):
        filename = csv_file.stem  # 获取不带扩展名的文件名
        
        # 解析文件名格式: "2024-W34-0821-0830"
        parts = filename.split('-')
        if len(parts) >= 4 and parts[1].startswith('W'):
            year = parts[0]
            week_num = parts[1][1:]  # 去掉'W'前缀
            start_date = parts[2]
            end_date = parts[3]
            
            # 转换为友好格式: "第34周(0821-0830)"
            display_name = f"第{week_num}周({start_date}-{end_date})"
            
            schedules.append({
                "filename": filename,
                "display_name": display_name,
                "year": year,
                "week": week_num,
                "type": "csv"
            })
    
    # 查找手动填写的排班数据
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(
                "SELECT DISTINCT week FROM manual_schedules ORDER BY week"
            )
            manual_weeks = cursor.fetchall()
            
            for (week_value,) in manual_weeks:
                # 解析周次格式: "2025-W34"
                if '-W' in week_value:
                    parts = week_value.split('-W')
                    if len(parts) == 2:
                        year = parts[0]
                        week_num = parts[1]
                        
                        # 转换为友好格式: "第34周(手动填写)"
                        display_name = f"第{week_num}周(手动填写)"
                        
                        schedules.append({
                            "filename": week_value,
                            "display_name": display_name,
                            "year": year,
                            "week": week_num,
                            "type": "manual"
                        })
    except Exception as e:
        print(f"获取手动排班数据列表失败: {e}")
    
    # 按年份和周数排序
    schedules.sort(key=lambda x: (x["year"], int(x["week"])))
    
    return schedules


@app.get("/api/schedules")
def api_get_schedules():
    """API端点：获取所有可用的排班文件列表"""
    schedules = get_available_schedules()
    return jsonify({"schedules": schedules})


@app.get("/api/week-options")
def api_get_week_options():
    """API端点：获取周次选项列表"""
    week_options = generate_week_options()
    return jsonify({"week_options": week_options})


@app.route("/schedule-table")
def schedule_table():
    """显示排班表数据"""
    week = request.args.get("week", "2024-32")
    user_info = get_current_user()
    
    # 获取排班数据，优先从CSV读取
    schedule_data = get_schedule_data(week)
    
    return render_template("schedule_table.html", schedule_data=schedule_data, user_info=user_info)


@app.get("/api/schedule-data/<week>")
def api_get_schedule_data(week: str):
    """API端点：获取指定周的排班数据"""
    try:
        schedule_data = get_schedule_data(week)
        
        # 转换为JSON格式
        result = {
            "week": schedule_data.week,
            "tables": []
        }
        
        for table in schedule_data.tables:
            table_data = {
                "title": table.title,
                "shifts": [],
                "dates": table.dates
            }
            
            for shift in table.shifts:
                shift_data = {
                    "position": shift.position,
                    "time_range": shift.time_range,
                    "assignments": shift.assignments
                }
                table_data["shifts"].append(shift_data)
            
            result["tables"].append(table_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/manual-schedule", methods=["GET", "POST"])
def manual_schedule():
    """手动填写排班表页面"""
    user_info = get_current_user()
    
    if request.method == "POST":
        # 处理表单提交 - 重定向到API端点
        return redirect(url_for('api_manual_schedule'))
    
    # GET - 显示手动填写页面
    return render_template("manual_schedule.html", user_info=user_info)


@app.route("/api/manual-schedule", methods=["POST"])
def api_manual_schedule():
    """API端点：保存手动填写的排班数据"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "请求数据不能为空"}), 400
        
        week = data.get('week', '').strip()
        weekday_data = data.get('weekday_data', [])
        weekend_data = data.get('weekend_data', [])
        
        if not week:
            return jsonify({"success": False, "error": "请选择排班周次"}), 400
        
        if not is_valid_week_string(week):
            return jsonify({"success": False, "error": "无效的周次格式"}), 400
        
        if not weekday_data and not weekend_data:
            return jsonify({"success": False, "error": "请至少填写一行排班数据"}), 400
        
        # 保存到数据库
        save_manual_schedule_data(week, weekday_data, weekend_data)
        
        return jsonify({"success": True, "message": "排班表保存成功"})
        
    except Exception as e:
        print(f"保存手动排班数据失败: {e}")
        return jsonify({"success": False, "error": "保存失败，请重试"}), 500


@app.get("/health")
def health() -> Tuple[str, int]:
    return "ok", 200


@app.get("/api/email/test")
def api_email_test():
    """测试邮件服务连接"""
    result = email_service.test_connection()
    return jsonify(result)


@app.get("/readme")
def readme() -> str:
    """显示项目README文件内容"""
    readme_path = BASE_DIR / "README.md"
    if readme_path.exists():
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # 简单的Markdown到HTML转换（基础版本）
            html_content = content.replace('\n', '<br>').replace('# ', '<h1>').replace('## ', '<h2>')
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Miss Zhang - README</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    pre {{ background: #f4f4f4; padding: 10px; overflow-x: auto; }}
                    code {{ background: #f4f4f4; padding: 2px 4px; }}
                </style>
            </head>
            <body>
                <h1>MissZhang 项目说明</h1>
                <div>{html_content}</div>
                <hr>
                <p><a href="/">返回首页</a></p>
            </body>
            </html>
            """
        except Exception as e:
            return f"Error reading README: {str(e)}", 500
    else:
        return "README file not found", 404


@app.get("/MP_verify_C1jlF7TZzN4da9le.txt")
def wechat_verify() -> str:
    """微信公众号JS接口安全域名验证文件"""
    return "C1jlF7TZzN4da9le"


@app.get("/profile")
# @require_login
def profile():
    """个人主页"""
    # 从数据库获取用户信息
    user_info = get_current_user()
    return render_template("profile.html", user_info=user_info)


@app.post("/api/profile")
# @require_login
def api_profile():
    """API端点：保存用户个人信息"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"ok": False, "error": "请求数据不能为空"}), 400
        
        name = (data.get("name") or "").strip()
        hospital = (data.get("hospital") or "").strip()
        department = (data.get("department") or "").strip()
        
        # 验证数据
        if not name or not hospital or not department:
            return jsonify({"ok": False, "error": "请填写完整信息"}), 400
        
        if len(name) > 50:
            return jsonify({"ok": False, "error": "姓名过长"}), 400
        
        if len(hospital) > 100:
            return jsonify({"ok": False, "error": "医院名称过长"}), 400
        
        if len(department) > 50:
            return jsonify({"ok": False, "error": "科室名称过长"}), 400
        
        # 保存到数据库
        save_user_profile(name, hospital, department)
        
        return jsonify({"ok": True})
        
    except Exception as e:
        print(f"保存用户信息失败: {e}")
        return jsonify({"ok": False, "error": "保存失败，请重试"}), 500


def get_user_profile() -> Dict[str, str]:
    """从数据库获取用户信息（兼容旧版本，现在使用get_current_user）"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(
                "SELECT name, hospital, department FROM user_profiles ORDER BY updated_at DESC LIMIT 1"
            )
            row = cursor.fetchone()
            
            if row:
                return {
                    "name": row[0],
                    "hospital": row[1],
                    "department": row[2]
                }
            else:
                return {}
                
    except Exception as e:
        print(f"获取用户信息失败: {e}")
        return {}


def save_user_profile(name: str, hospital: str, department: str) -> None:
    """保存用户信息到数据库（支持多用户）"""
    try:
        user_info = get_current_user()
        if not user_info:
            raise Exception("用户未登录")
        
        with sqlite3.connect(DB_PATH) as conn:
            # 检查是否已有该用户的profile记录
            cursor = conn.execute(
                "SELECT id FROM user_profiles WHERE user_id = ?",
                (user_info['id'],)
            )
            existing_profile = cursor.fetchone()
            
            if existing_profile:
                # 更新现有记录
                conn.execute(
                    """
                    UPDATE user_profiles 
                    SET name = ?, hospital = ?, department = ?, updated_at = ?
                    WHERE user_id = ?
                    """,
                    (name, hospital, department, datetime.utcnow().isoformat(), user_info['id'])
                )
            else:
                # 插入新记录
                conn.execute(
                    """
                    INSERT INTO user_profiles (user_id, name, hospital, department, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (user_info['id'], name, hospital, department, 
                     datetime.utcnow().isoformat(), datetime.utcnow().isoformat())
                )
            
            conn.commit()
            
    except Exception as e:
        print(f"保存用户信息到数据库失败: {e}")
        raise


def save_manual_schedule_data(week: str, weekday_data: List[Dict], weekend_data: List[Dict]) -> None:
    """保存手动填写的排班数据到数据库"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # 先删除该周次的现有数据
            conn.execute("DELETE FROM manual_schedules WHERE week = ?", (week,))
            
            current_time = datetime.utcnow().isoformat()
            
            # 保存平日班数据
            for item in weekday_data:
                conn.execute(
                    """
                    INSERT INTO manual_schedules 
                    (week, date, shift, position, staff_name, schedule_type, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (week, item['date'], item['shift'], item['position'], 
                     item['staff'], 'weekday', current_time, current_time)
                )
            
            # 保存周末班数据
            for item in weekend_data:
                conn.execute(
                    """
                    INSERT INTO manual_schedules 
                    (week, date, shift, position, staff_name, schedule_type, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (week, item['date'], item['shift'], None, 
                     item['staff'], 'weekend', current_time, current_time)
                )
            
            conn.commit()
            print(f"成功保存手动排班数据：周次 {week}")
            
    except Exception as e:
        print(f"保存手动排班数据失败: {e}")
        raise


def get_manual_schedule_data(week: str) -> Optional[ScheduleData]:
    """从数据库获取手动填写的排班数据"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(
                """
                SELECT date, shift, position, staff_name, schedule_type 
                FROM manual_schedules 
                WHERE week = ? 
                ORDER BY schedule_type, date, shift, position
                """,
                (week,)
            )
            rows = cursor.fetchall()
            
            if not rows:
                return None
            
            # 组织数据
            weekday_data = {}
            weekend_data = {}
            all_dates = set()
            
            for row in rows:
                date, shift, position, staff_name, schedule_type = row
                all_dates.add(date)
                
                if schedule_type == 'weekday':
                    key = f"{shift}"
                    if key not in weekday_data:
                        weekday_data[key] = {}
                    if position not in weekday_data[key]:
                        weekday_data[key][position] = {}
                    weekday_data[key][position][date] = staff_name
                    
                elif schedule_type == 'weekend':
                    key = f"{shift}"
                    if key not in weekend_data:
                        weekend_data[key] = {}
                    if 'weekend' not in weekend_data[key]:
                        weekend_data[key]['weekend'] = {}
                    weekend_data[key]['weekend'][date] = staff_name
            
            # 转换为ScheduleData格式
            tables = []
            sorted_dates = sorted(list(all_dates))
            
            # 处理平日班数据
            for shift_name, positions in weekday_data.items():
                shifts = []
                for position, assignments in positions.items():
                    shift = ScheduleShift(
                        position=position,
                        time_range=get_time_range_for_shift(shift_name),
                        assignments=assignments,
                        shift=shift_name
                    )
                    shifts.append(shift)
                
                if shifts:
                    table = ScheduleTable(
                        title=f"平日班 - {shift_name}",
                        shifts=shifts,
                        dates=sorted_dates
                    )
                    tables.append(table)
            
            # 处理周末班数据
            for shift_name, positions in weekend_data.items():
                shifts = []
                for position, assignments in positions.items():
                    shift = ScheduleShift(
                        position="周末班",
                        time_range=get_time_range_for_shift(shift_name),
                        assignments=assignments,
                        shift=shift_name
                    )
                    shifts.append(shift)
                
                if shifts:
                    table = ScheduleTable(
                        title=f"周末班 - {shift_name}",
                        shifts=shifts,
                        dates=sorted_dates
                    )
                    tables.append(table)
            
            return ScheduleData(week=week, tables=tables)
            
    except Exception as e:
        print(f"获取手动排班数据失败: {e}")
        return None


def get_time_range_for_shift(shift_name: str) -> str:
    """根据班次名称获取时间范围"""
    time_ranges = {
        '上午': '08:00-12:00',
        '下午': '13:00-17:00',
        '晚班': '18:00-22:00',
        '夜班': '22:00-次日08:00',
        '全天': '全天'
    }
    return time_ranges.get(shift_name, shift_name)


@app.post("/api/contact")
def api_contact() -> Tuple[Any, int]:
    content_type = request.headers.get("Content-Type", "").lower()
    payload: Optional[Dict[str, Any]]
    if "application/json" in content_type:
        payload = request.get_json(silent=True) or {}
    else:
        # Fallback to form data
        payload = {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "message": request.form.get("message"),
        }

    parsed, error = parse_contact_payload(payload)
    if error:
        return jsonify({"ok": False, "error": error}), 400

    ensure_data_dir()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO contact_messages (name, email, message, created_at) VALUES (?, ?, ?, ?)",
            (parsed.name, parsed.email, parsed.message, datetime.utcnow().isoformat()),
        )
        conn.commit()

    return jsonify({"ok": True}), 200


# Initialize database on import
init_db()

if __name__ == "__main__":
    # For local dev only: `python app/main.py`
    app.run(host="0.0.0.0", port=8000, debug=True) 