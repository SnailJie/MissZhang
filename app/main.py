from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from flask import Flask, jsonify, render_template, request

BASE_DIR: Path = Path(__file__).resolve().parents[1]
DATA_DIR: Path = BASE_DIR / "data"
DB_PATH: Path = DATA_DIR / "app.db"

app = Flask(
    __name__,
    template_folder=str((Path(__file__).parent / "templates")),
    static_folder=str((Path(__file__).parent / "static")),
)


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


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


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.get("/health")
def health() -> Tuple[str, int]:
    return "ok", 200


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