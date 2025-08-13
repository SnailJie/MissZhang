from __future__ import annotations

import json
import sqlite3
import re
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List

from flask import Flask, jsonify, render_template, request, redirect, url_for, send_from_directory

# 导入排班表数据结构
from app.schedule_data import get_mock_schedule_data, ScheduleData

# 排班表数据结构定义
@dataclass
class ScheduleShift:
    """排班班次"""
    position: str  # 岗位，如 "MR1", "MR2" 等
    time_range: str  # 时间范围，如 "07:30-13:00"
    assignments: Dict[str, str]  # 日期到人员姓名的映射

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


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def ensure_schedules_dir() -> None:
    ensure_data_dir()
    SCHEDULES_DIR.mkdir(parents=True, exist_ok=True)


def init_db() -> None:
    ensure_data_dir()
    with sqlite3.connect(DB_PATH) as conn:
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


# ---------- Schedules helpers ----------

def get_current_week_str() -> str:
    iso_year, iso_week, _ = date.today().isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


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
    return render_template("index.html")


@app.get("/about")
def about():
    return render_template("about.html")


@app.get("/schedule")
def schedule():
    return render_template("schedule.html")


# Serve saved schedule images
@app.get("/schedules/<path:filename>")
def serve_schedule_image(filename: str):
    ensure_schedules_dir()
    return send_from_directory(SCHEDULES_DIR, filename)


# Insider page: preview or upload schedule image by week
@app.route("/insider", methods=["GET", "POST"])
def insider():
    ensure_schedules_dir()

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
            return render_template("insider.html", error=error_msg, week=week_str or get_current_week_str())

        if not image_file or image_file.filename == "":
            return render_template("insider.html", error="请上传排班表图片", week=week_str)

        # Determine extension
        ext = (Path(image_file.filename).suffix or "").lower().lstrip(".")
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            return render_template(
                "insider.html",
                error=f"不支持的图片格式: .{ext}，请上传: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}",
                week=week_str,
            )

        # Save as {week}.{ext}
        # Remove any old files for this week to keep a single source of truth
        for old_ext in ALLOWED_IMAGE_EXTENSIONS:
            old_path = SCHEDULES_DIR / f"{week_str}.{old_ext}"
            if old_path.exists():
                try:
                    old_path.unlink()
                except Exception:
                    pass
        save_path = SCHEDULES_DIR / f"{week_str}.{ext}"
        image_file.save(save_path)

        return redirect(url_for("insider", week=week_str))

    # GET
    week_str = (request.args.get("week") or get_current_week_str()).strip()
    if not is_valid_week_string(week_str):
        week_str = get_current_week_str()

    existing_path = find_existing_schedule_path(week_str)
    image_url: Optional[str] = None
    if existing_path:
        image_url = url_for("serve_schedule_image", filename=existing_path.name)

    return render_template("insider.html", week=week_str, image_url=image_url)


@app.route("/schedule-table")
def schedule_table():
    """显示排班表数据"""
    week = request.args.get("week", "2024-32")
    
    # 获取mock数据
    schedule_data = get_mock_schedule_data(week)
    
    return render_template("schedule_table.html", schedule_data=schedule_data)


@app.get("/health")
def health() -> Tuple[str, int]:
    return "ok", 200


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