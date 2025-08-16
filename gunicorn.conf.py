import multiprocessing
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

LOGS_DIR = BASE_DIR / "logs"
RUN_DIR = BASE_DIR / "run"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
RUN_DIR.mkdir(parents=True, exist_ok=True)

# Networking - 从环境变量获取配置，默认使用8000端口（nginx反向代理）
bind = f"{os.getenv('PRODUCTION_HOST', '0.0.0.0')}:{os.getenv('PRODUCTION_PORT', '8000')}"

# Processes
workers = max(2, multiprocessing.cpu_count() // 2 or 1)
threads = 2
worker_class = "gthread"

# Reliability
timeout = 60
keepalive = 5

# Daemonize and manage PID
pidfile = str(RUN_DIR / "gunicorn.pid")
daemon = True

# Logging
accesslog = str(LOGS_DIR / "gunicorn.access.log")
errorlog = str(LOGS_DIR / "gunicorn.error.log")
loglevel = "info" 