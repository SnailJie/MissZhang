# 🔐 Let's Encrypt SSL 证书配置指南

## 📋 概述

本指南将帮助你使用 Let's Encrypt 为你的 MissZhang 应用配置免费的 SSL 证书，实现 HTTPS 访问。

## 🎯 为什么需要 SSL 证书？

1. **微信要求**: 微信公众平台要求回调地址必须是 HTTPS
2. **安全性**: 保护用户数据传输安全
3. **SEO 优化**: HTTPS 网站在搜索引擎中排名更高
4. **用户信任**: 显示安全锁图标，提升用户信任度

## ⚠️ 前置条件

### 1. 域名要求
- 拥有一个域名（如：example.com）
- 域名已正确解析到服务器 IP
- 域名已备案（中国大陆服务器要求）

### 2. 服务器要求
- 服务器有公网 IP
- 防火墙开放 80 和 443 端口
- 已安装 Nginx 或 Apache

### 3. 网络要求
- 服务器可以访问外网
- 域名可以正常解析

### 4. 系统工具要求
- 已安装 DNS 查询工具（dig, host, nslookup 等）
- CentOS/RHEL 系统：`sudo yum install -y bind-utils`
- Ubuntu/Debian 系统：`sudo apt install -y dnsutils`

## 🚀 快速配置（推荐）

### 使用自动化脚本

```bash
# 1. 确保有 root 权限
sudo su

# 2. 安装 DNS 工具（CentOS 系统）
sudo bash scripts/install_dns_tools.sh

# 3. 运行 SSL 配置脚本
sudo bash scripts/ssl_setup.sh

# 4. 按提示输入域名和邮箱
```

脚本会自动完成：
- 检测系统环境
- 安装 certbot
- 配置 Web 服务器
- 申请 SSL 证书
- 配置自动续期
- 更新项目配置

**注意**: 如果系统缺少 DNS 工具，请先运行 `sudo bash scripts/install_dns_tools.sh`

### CentOS/RHEL 兼容系统特殊说明

以下系统默认可能没有安装 DNS 查询工具，需要先安装：

#### CentOS/RHEL 系统
```bash
# 安装 bind-utils 包（包含 dig, host, nslookup）
sudo yum install -y bind-utils

# 或者使用 dnf（CentOS 8+）
sudo dnf install -y bind-utils
```

#### 阿里云 Linux 系统
```bash
# 阿里云 Linux 3 基于 CentOS 7
sudo yum install -y bind-utils

# 阿里云 Linux 2 基于 CentOS 7
sudo yum install -y bind-utils
```

#### 验证安装
```bash
dig -v
host -V
nslookup -version
```

## 📝 手动配置步骤

### 步骤 1: 安装 certbot

#### Ubuntu/Debian 系统
```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx python3-certbot-apache
```

#### CentOS/RHEL 系统
```bash
# 使用 dnf (CentOS 8+)
sudo dnf install -y certbot python3-certbot-nginx python3-certbot-apache

# 使用 yum (CentOS 7)
sudo yum install -y certbot python3-certbot-nginx python3-certbot-apache
```

#### 其他系统
```bash
# 使用 snap
sudo snap install --classic certbot
sudo ln -sf /snap/bin/certbot /usr/bin/certbot
```

### 步骤 2: 配置 Web 服务器

#### Nginx 配置

创建配置文件 `/etc/nginx/sites-available/yourdomain.com`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Let's Encrypt 验证
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # 重定向到 HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL 配置（certbot 会自动配置）
    
    # 应用代理
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 静态文件
    location /static/ {
        alias /path/to/your/project/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

启用站点：
```bash
sudo ln -sf /etc/nginx/sites-available/yourdomain.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Apache 配置

创建配置文件 `/etc/apache2/sites-available/yourdomain.com.conf`:

```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com
    DocumentRoot /var/www/html
    
    # Let's Encrypt 验证
    Alias /.well-known/acme-challenge/ /var/www/html/.well-known/acme-challenge/
    
    # 重定向到 HTTPS
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
</VirtualHost>

<VirtualHost *:443>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com
    
    # SSL 配置（certbot 会自动配置）
    
    # 应用代理
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
    
    # 静态文件
    Alias /static/ /path/to/your/project/app/static/
    <Directory "/path/to/your/project/app/static/">
        Require all granted
        ExpiresActive On
        ExpiresDefault "access plus 1 year"
    </Directory>
</VirtualHost>
```

启用模块和站点：
```bash
sudo a2enmod ssl
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod rewrite
sudo a2ensite yourdomain.com.conf
sudo apache2ctl configtest
sudo systemctl reload apache2
```

### 步骤 3: 申请 SSL 证书

#### 使用 Nginx 插件
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com --email your-email@example.com --agree-tos --non-interactive
```

#### 使用 Apache 插件
```bash
sudo certbot --apache -d yourdomain.com -d www.yourdomain.com --email your-email@example.com --agree-tos --non-interactive
```

#### 使用独立模式（如果上述方法失败）
```bash
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com --email your-email@example.com --agree-tos --non-interactive
```

### 步骤 4: 配置自动续期

Let's Encrypt 证书有效期为 90 天，需要定期续期：

```bash
# 测试续期
sudo certbot renew --dry-run

# 添加到 crontab（每天中午 12 点检查续期）
sudo crontab -e

# 添加以下行：
0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔧 常见问题解决

### 1. 证书申请失败

**问题**: `Challenge failed for domain yourdomain.com`

**解决方案**:
- 检查域名是否正确解析到服务器
- 确保 80 端口开放
- 检查 Web 服务器配置
- 查看 certbot 日志：`sudo certbot logs`

### 2. 证书续期失败

**问题**: 自动续期失败

**解决方案**:
```bash
# 手动续期
sudo certbot renew

# 检查续期状态
sudo certbot certificates

# 查看续期日志
sudo journalctl -u certbot.timer
```

### 3. Web 服务器配置错误

**问题**: Nginx/Apache 配置语法错误

**解决方案**:
```bash
# Nginx 配置测试
sudo nginx -t

# Apache 配置测试
sudo apache2ctl configtest
```

### 4. 权限问题

**问题**: certbot 无法访问文件

**解决方案**:
```bash
# 检查 certbot 权限
sudo ls -la /etc/letsencrypt/

# 修复权限
sudo chown -R root:root /etc/letsencrypt/
sudo chmod -R 755 /etc/letsencrypt/
```

## 📊 配置验证

### 1. 检查证书状态
```bash
sudo certbot certificates
```

### 2. 测试 HTTPS 访问
```bash
curl -I https://yourdomain.com
```

### 3. 检查 SSL 配置
```bash
# 使用 SSL Labs 测试
# 访问: https://www.ssllabs.com/ssltest/
```

### 4. 检查自动续期
```bash
sudo certbot renew --dry-run
```

## 🔒 安全最佳实践

### 1. 文件权限
```bash
# 设置 .env 文件权限
chmod 600 .env

# 设置 SSL 证书权限
sudo chmod 755 /etc/letsencrypt/
sudo chmod 600 /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

### 2. 防火墙配置
```bash
# 只开放必要端口
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 3. 定期更新
```bash
# 更新系统
sudo apt update && sudo apt upgrade

# 更新 certbot
sudo certbot update
```

## 📚 相关资源

- [Let's Encrypt 官网](https://letsencrypt.org/)
- [Certbot 文档](https://certbot.eff.org/)
- [SSL Labs 测试工具](https://www.ssllabs.com/ssltest/)
- [Mozilla SSL 配置生成器](https://ssl-config.mozilla.org/)

## 🎉 完成后的效果

配置完成后，你的应用将具备：

1. ✅ 免费的 SSL 证书
2. ✅ 自动 HTTPS 重定向
3. ✅ 自动证书续期
4. ✅ 符合微信要求
5. ✅ 提升安全性
6. ✅ 改善 SEO 排名

## 📞 技术支持

如果遇到问题，可以：

1. 查看 certbot 日志：`sudo certbot logs`
2. 检查 Web 服务器日志
3. 参考官方文档
4. 在社区论坛寻求帮助

---

**注意**: 本指南基于 Ubuntu/Debian 系统编写，其他系统可能需要调整命令。
