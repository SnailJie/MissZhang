# 🚀 MissZhang 快速启动指南

## 1. 环境准备

确保你的系统已安装：
- Python 3.7+
- pip

## 2. 安装依赖

```bash
pip install -r requirements.txt
```

## 3. 配置微信

### 3.1 获取微信配置
1. 访问 [微信公众平台](https://mp.weixin.qq.com/)
2. 登录你的公众号
3. 在"开发" -> "基本配置"中获取：
   - AppID
   - AppSecret

### 3.2 开启网页授权
1. 在"开发" -> "接口权限"中
2. 找到"网页授权"功能
3. 点击"开启"

### 3.3 配置授权域名
1. 在"开发" -> "基本配置"中
2. 找到"网页授权域名"
3. 添加你的域名（开发时可以是 localhost）

## 4. 创建配置文件

### 方法1：使用配置脚本（推荐）
```bash
bash scripts/setup_env.sh
```

### 方法2：手动配置
复制 `env.example` 为 `.env` 并修改：

```bash
cp env.example .env
```

编辑 `.env` 文件，填入真实的微信配置：

```bash
WECHAT_APP_ID=wx1234567890abcdef
WECHAT_APP_SECRET=abcdef1234567890abcdef1234567890
WECHAT_REDIRECT_URI=http://localhost:5000/wechat/callback
FLASK_SECRET_KEY=your_random_secret_key_here
```

## 5. 启动应用

```bash
python run.py
```

应用将在 `http://localhost:5000` 启动。

## 6. 测试微信登录

1. 在微信中访问你的应用
2. 点击"微信登录"
3. 完成授权流程
4. 查看个人主页

## 常见问题

### Q: 微信登录失败？
A: 检查以下几点：
- AppID 和 AppSecret 是否正确
- 是否开启了网页授权功能
- 回调地址是否配置正确
- 域名是否在授权域名列表中

### Q: 如何检查系统状态？
A: 运行状态检查脚本：
```bash
bash scripts/status.sh
```

### Q: 如何重新配置环境变量？
A: 运行配置脚本：
```bash
bash scripts/setup_env.sh
```

### Q: 应用无法启动？
A: 检查：
- Python 版本是否为 3.7+
- 依赖是否安装完整
- 端口 5000 是否被占用

### Q: 数据库错误？
A: 确保：
- `data` 目录有写入权限
- SQLite 支持正常

## 开发模式

开发时建议：
- 使用 `FLASK_DEBUG=1`
- 在微信开发者工具中测试
- 使用 ngrok 等工具进行外网测试

## 生产部署

生产环境需要：
- 使用真实的域名和HTTPS
- 设置强密钥
- 关闭调试模式
- 使用 gunicorn 等WSGI服务器
