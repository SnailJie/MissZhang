# MissZhang 项目部署指南 (Nginx版本)

## 🚀 快速部署步骤

### 1. 环境准备
确保你的阿里云OS服务器已安装以下软件：
- Python 3.9+
- nginx
- git

```bash
# 安装nginx (CentOS/RHEL)
sudo yum install nginx -y

# 安装nginx (Ubuntu/Debian)
sudo apt update && sudo apt install nginx -y

# 启动并设置开机自启
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 2. 克隆项目
```bash
cd /opt
sudo git clone <your-repo-url> missZhang
cd missZhang
```

### 3. 配置环境变量
```bash
# 运行环境配置脚本
sudo bash scripts/setup_env.sh

# 编辑配置文件
sudo nano .env
```

**重要配置项：**
```bash
# 微信配置
WECHAT_APP_ID=your_real_app_id
WECHAT_APP_SECRET=your_real_app_secret
WECHAT_REDIRECT_URI=http://www.wuyinxinghai.cn/wechat/callback

# 生产环境配置
PRODUCTION_HOST=0.0.0.0
PRODUCTION_PORT=8000
```

### 4. 一键部署
```bash
sudo bash scripts/deploy_with_nginx.sh
```

## 🔧 手动配置步骤

### 1. 配置nginx
将项目根目录的 `nginx.conf` 文件复制到nginx配置目录：

```bash
sudo cp nginx.conf /etc/nginx/conf.d/misszhang.conf
sudo nginx -t  # 测试配置
sudo systemctl restart nginx
```

### 2. 启动Flask应用
```bash
cd /opt/missZhang
sudo bash scripts/start.sh
```

### 3. 配置防火墙
```bash
# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload

# Ubuntu/Debian
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

## 📁 目录结构

```
/opt/missZhang/
├── app/                    # Flask应用代码
├── static/                 # 静态文件
├── templates/              # HTML模板
├── logs/                   # 应用日志
├── run/                    # PID文件
├── .env                    # 环境配置
└── scripts/                # 部署脚本
```

## 🌐 访问地址

- **网站**: http://www.wuyinxinghai.cn
- **健康检查**: http://www.wuyinxinghai.cn/health
- **微信验证**: http://www.wuyinxinghai.cn/MP_verify_C1jlF7TZzN4da9le.txt

## 📊 日志位置

- **应用日志**: `/opt/missZhang/logs/`
- **nginx访问日志**: `/var/log/nginx/misszhang_access.log`
- **nginx错误日志**: `/var/log/nginx/misszhang_error.log`

## 🛠️ 常用管理命令

```bash
# 检查服务状态
sudo systemctl status nginx
cd /opt/missZhang && sudo bash scripts/status.sh

# 重启服务
sudo systemctl restart nginx
cd /opt/missZhang && sudo bash scripts/stop.sh && sudo bash scripts/start.sh

# 查看日志
sudo tail -f /opt/missZhang/logs/gunicorn.error.log
sudo tail -f /var/log/nginx/misszhang_error.log

# 停止应用
cd /opt/missZhang && sudo bash scripts/stop.sh
```

## 🔍 故障排除

### 1. 应用无法启动
```bash
# 检查日志
sudo tail -f /opt/missZhang/logs/gunicorn.error.log

# 检查端口占用
sudo netstat -tlnp | grep :8000

# 检查权限
sudo ls -la /opt/missZhang/
```

### 2. nginx无法启动
```bash
# 检查配置语法
sudo nginx -t

# 检查端口占用
sudo netstat -tlnp | grep :80

# 查看nginx错误日志
sudo tail -f /var/log/nginx/error.log
```

### 3. 域名无法访问
```bash
# 检查DNS解析
nslookup www.wuyinxinghai.cn

# 检查防火墙
sudo firewall-cmd --list-ports

# 检查SELinux (CentOS)
sudo setsebool -P httpd_can_network_connect 1
```

## 🔒 安全建议

1. **定期更新系统**: `sudo yum update` 或 `sudo apt update`
2. **配置SSL证书**: 使用Let's Encrypt免费证书
3. **限制访问**: 配置防火墙规则
4. **监控日志**: 定期检查访问和错误日志
5. **备份数据**: 定期备份应用数据和配置

## 📞 技术支持

如果遇到问题，请检查：
1. 系统日志: `sudo journalctl -u nginx`
2. 应用日志: `/opt/missZhang/logs/`
3. nginx配置: `/etc/nginx/conf.d/misszhang.conf`
4. 环境变量: `/opt/missZhang/.env`
