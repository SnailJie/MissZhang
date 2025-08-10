# MissZhang - Simple Python Web Service (Flask)

A cheerful, mobile-friendly landing site with a Python backend. One command to deploy and run on a server.

## Features
- Responsive H5 front-end (mobile first)
- Contact form posting to backend (`/api/contact`)
- SQLite storage (file: `data/app.db`)
- Health check at `/health`
- Gunicorn config with daemon mode, logs, PID file
- **Production ready**: Uses port 80 for standard HTTP access

## Prerequisites
- Python 3.9+ on the server
- Root access (for port 80)
- Domain name (optional, for custom domain access)

## Quick Start (one command)
```bash
bash scripts/start.sh
```

- Once started, visit: `http://<your-server-ip>`
- To stop:
```bash
bash scripts/stop.sh
```

## Domain Setup (腾讯云域名 + 阿里云服务器)

### 1. 腾讯云域名解析
1. 登录腾讯云控制台 → 域名管理
2. 添加解析记录：
   - **记录类型**: A
   - **主机记录**: @ (或 www)
   - **记录值**: 172.31.73.92
   - **TTL**: 600

### 2. 阿里云服务器配置
1. **安全组设置**: 开放80端口
2. **上传项目**:
   ```bash
   scp -r /path/to/missZhang root@172.31.73.92:/opt/
   ```
3. **部署应用**:
   ```bash
   ssh root@172.31.73.92
   cd /opt/missZhang
   sudo bash scripts/deploy.sh
   ```

### 3. 验证访问
- 直接访问: `http://172.31.73.92`
- 域名访问: `http://yourdomain.com`

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
├── docs
│   └── domain-setup.md
├── gunicorn.conf.py
├── requirements.txt
├── scripts
│   ├── start.sh
│   ├── stop.sh
│   └── deploy.sh
└── README.md
```

## Changing the Port or Workers
- Edit `gunicorn.conf.py` (`bind`, `workers`, `threads`).
- For development, change `bind = "0.0.0.0:8000"`

## Logs and PID
- Logs: `logs/gunicorn.access.log`, `logs/gunicorn.error.log`
- PID: `run/gunicorn.pid`

## Notes
- Database file is created on first run.
- Application runs on port 80 for production (standard HTTP).
- If you prefer foreground mode, set `daemon = False` in `gunicorn.conf.py` and run `bash scripts/start.sh` in a screen/tmux session. 