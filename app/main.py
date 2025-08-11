from __future__ import annotations

import json
import sqlite3
import re
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from flask import Flask, jsonify, render_template, request, redirect, url_for, send_from_directory

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

        if not week_str or not is_valid_week_string(week_str):
            return render_template("insider.html", error="请选择正确的周，例如 2025-W03", week=week_str or get_current_week_str())

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