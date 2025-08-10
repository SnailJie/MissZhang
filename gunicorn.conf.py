import multiprocessing
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"
RUN_DIR = BASE_DIR / "run"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
RUN_DIR.mkdir(parents=True, exist_ok=True)

# Networking
bind = "0.0.0.0:8000"

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