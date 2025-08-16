#!/usr/bin/env bash
set -euo pipefail

# Resolve project root (this script is in scripts/)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"
REQ_FILE="$PROJECT_ROOT/requirements.txt"
LOG_DIR="$PROJECT_ROOT/logs"
RUN_DIR="$PROJECT_ROOT/run"

mkdir -p "$LOG_DIR" "$RUN_DIR" "$PROJECT_ROOT/data"

PY_BIN="$(command -v python3 || command -v python)"
if [ -z "$PY_BIN" ]; then
  echo "Python is required but not found. Please install Python 3.9+." >&2
  exit 1
fi

# Create venv if needed
if [ ! -d "$VENV_DIR" ]; then
  "$PY_BIN" -m venv "$VENV_DIR"
fi

# Activate and install deps
source "$VENV_DIR/bin/activate"
pip install -U pip wheel
pip install -r "$REQ_FILE"

# Check for environment configuration
if [ ! -f "$PROJECT_ROOT/.env" ]; then
  echo "⚠️  警告: 未找到 .env 配置文件"
  echo "请运行以下命令配置环境变量："
  echo "bash scripts/setup_env.sh"
  echo ""
  echo "或者手动复制并编辑："
  echo "cp env.example .env"
  echo ""
  echo "继续启动应用（使用默认配置）..."
else
  echo "✅ 环境配置文件已找到"
  # 加载环境变量
  export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
fi

# Start Gunicorn (daemonized via gunicorn.conf.py)
GUNICORN_BIN="$VENV_DIR/bin/gunicorn"

# If already running, stop first
if [ -f "$RUN_DIR/gunicorn.pid" ] && kill -0 "$(cat "$RUN_DIR/gunicorn.pid")" 2>/dev/null; then
  echo "Gunicorn already running (PID $(cat "$RUN_DIR/gunicorn.pid")). Restarting..."
  bash "$PROJECT_ROOT/scripts/stop.sh" || true
fi

"$GUNICORN_BIN" -c "$PROJECT_ROOT/gunicorn.conf.py" app.main:app

# Small wait and health check
sleep 1
STATUS=$(curl -fsS "http://127.0.0.1:80/health" || true)
if [ "$STATUS" = "ok" ]; then
  echo "App started successfully: http://<server-ip>:80"
  echo "Logs: $LOG_DIR"
else
  echo "App started, but health check failed. Check logs in $LOG_DIR" >&2
fi 