# MissZhang - Simple Python Web Service (Flask)

A cheerful, mobile-friendly landing site with a Python backend. One command to deploy and run on a server.

## Features
- Responsive H5 front-end (mobile first)
- Contact form posting to backend (`/api/contact`)
- SQLite storage (file: `data/app.db`)
- Health check at `/health`
- Gunicorn config with daemon mode, logs, PID file

## Prerequisites
- Python 3.9+ on the server
- Port 8000 open (or change in `gunicorn.conf.py`)

## Quick Start (one command)
```bash
bash scripts/start.sh
```

- Once started, visit: `http://<your-server-ip>:8000`
- To stop:
```bash
bash scripts/stop.sh
```

## Project Structure
```
.
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── static
│   │   ├── css
│   │   │   └── style.css
│   │   └── js
│   │       └── main.js
│   └── templates
│       ├── base.html
│       └── index.html
├── data
│   └── .gitkeep
├── gunicorn.conf.py
├── requirements.txt
├── scripts
│   ├── start.sh
│   └── stop.sh
└── README.md
```

## Changing the Port or Workers
- Edit `gunicorn.conf.py` (`bind`, `workers`, `threads`).

## Logs and PID
- Logs: `logs/gunicorn.access.log`, `logs/gunicorn.error.log`
- PID: `run/gunicorn.pid`

## Notes
- Database file is created on first run.
- If you prefer foreground mode, set `daemon = False` in `gunicorn.conf.py` and run `bash scripts/start.sh` in a screen/tmux session. 