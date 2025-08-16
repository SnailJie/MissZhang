# MissZhang 排班管理系统

一个支持微信登录的医院排班管理系统，基于Flask构建。

## 功能特性

- 🔐 微信网页授权登录
- 👥 多用户支持
- 📅 排班表管理
- 🖼️ 排班表图片上传和预览
- 📊 排班数据CSV导入导出
- 📱 响应式设计

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置微信

创建 `.env` 文件并配置以下环境变量：

```bash
# 微信配置
WECHAT_APP_ID=your_app_id_here
WECHAT_APP_SECRET=your_app_secret_here
WECHAT_REDIRECT_URI=http://localhost:5000/wechat/callback

# Flask配置
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_PORT=5000
```

### 3. 获取微信配置

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 创建或选择公众号
3. 在"开发" -> "基本配置"中获取 `AppID` 和 `AppSecret`
4. 在"开发" -> "接口权限"中开启"网页授权"

### 4. 运行应用

```bash
python run.py
```

应用将在 `http://localhost:5000` 启动。

## 使用说明

### 微信登录流程

1. 用户访问系统首页
2. 点击"微信登录"按钮
3. 跳转到微信授权页面
4. 用户确认授权后返回系统
5. 系统创建或更新用户信息
6. 跳转到个人主页

### 功能页面

- **首页** (`/`): 系统介绍和登录入口
- **排班表** (`/schedule`): 查看排班信息（需登录）
- **个人主页** (`/profile`): 管理个人信息（需登录）
- **排班管理** (`/insider`): 上传和管理排班表（需登录）

## 技术架构

- **后端**: Flask + SQLite
- **前端**: HTML + CSS + JavaScript
- **认证**: 微信网页授权
- **数据库**: SQLite（支持多用户）

## 数据库结构

### users 表
- `id`: 用户ID
- `openid`: 微信OpenID
- `nickname`: 微信昵称
- `avatar_url`: 头像URL
- `created_at`: 创建时间
- `updated_at`: 更新时间

### user_profiles 表
- `id`: 档案ID
- `user_id`: 关联用户ID
- `name`: 真实姓名
- `hospital`: 医院名称
- `department`: 科室名称
- `updated_at`: 更新时间

## 开发说明

### 添加新路由

```python
@app.route("/new-route")
@require_login  # 需要登录验证
def new_route():
    user_info = get_current_user()
    return render_template("new_template.html", user_info=user_info)
```

### 用户验证装饰器

```python
from app.main import require_login

@app.route("/protected")
@require_login
def protected_route():
    # 只有登录用户才能访问
    pass
```

## 部署说明

### 生产环境

1. 设置 `FLASK_ENV=production`
2. 使用 `gunicorn` 或 `uwsgi` 部署
3. 配置反向代理（Nginx）
4. 使用环境变量管理敏感配置

### Docker 部署

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "run.py"]
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！ 