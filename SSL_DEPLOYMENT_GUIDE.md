# 🔐 SSL 证书部署指南

## 📋 概述

本指南将帮助你在阿里云 OS 系统上配置 SSL 证书，使你的网站支持 HTTPS 访问。

## ✅ 前置条件

- ✅ 已通过 `certbot --nginx -d wuyinxinghai.cn -d www.wuyinxinghai.cn` 生成 SSL 证书
- ✅ 已安装 Nginx
- ✅ 已安装 certbot
- ✅ 域名 DNS 已正确配置

## 🚀 快速部署步骤

### 1. 上传配置文件到服务器

将项目文件上传到你的服务器，或者直接在服务器上创建配置文件。

### 2. 运行部署脚本

```bash
# 给脚本添加执行权限
chmod +x scripts/deploy_ssl_nginx.sh
chmod +x scripts/ssl_renew.sh

# 运行 SSL 部署脚本
sudo bash scripts/deploy_ssl_nginx.sh
```

### 3. 验证部署结果

脚本运行完成后，检查以下内容：

- ✅ Nginx 服务状态：`systemctl status nginx`
- ✅ 端口监听：`netstat -tlnp | grep nginx`
- ✅ 访问测试：https://wuyinxinghai.cn

## 🔧 手动配置步骤

如果你不想使用自动脚本，可以手动配置：

### 1. 备份当前配置

```bash
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
sudo cp -r /etc/nginx/conf.d /etc/nginx/conf.d.backup
```

### 2. 创建新的配置文件

```bash
sudo nano /etc/nginx/conf.d/wuyinxinghai.cn.conf
```

将 `nginx.conf` 文件的内容复制进去。

### 3. 检查配置语法

```bash
sudo nginx -t
```

### 4. 重启 Nginx

```bash
sudo systemctl restart nginx
```

## 📁 配置文件说明

### nginx.conf

- **HTTP 重定向**：自动将 HTTP 请求重定向到 HTTPS
- **SSL 配置**：使用 Let's Encrypt 生成的证书
- **安全头**：添加 HSTS、X-Frame-Options 等安全头
- **反向代理**：将请求代理到 Flask 应用（端口 8000）

### 关键配置项

```nginx
# SSL 证书路径
ssl_certificate /etc/letsencrypt/live/wuyinxinghai.cn/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/wuyinxinghai.cn/privkey.pem;

# 安全配置
ssl_protocols TLSv1.2 TLSv1.3;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

# HTTP 重定向
return 301 https://$server_name$request_uri;
```

## 🔄 自动续期设置

### 1. 设置定时任务

```bash
# 编辑 crontab
sudo crontab -e

# 添加以下行（每天凌晨 2 点检查续期）
0 2 * * * /opt/missZhang/scripts/ssl_renew.sh
```

### 2. 手动测试续期

```bash
sudo bash scripts/ssl_renew.sh
```

## 🧪 测试验证

### 1. 基本功能测试

```bash
# 检查 Nginx 状态
sudo systemctl status nginx

# 检查端口监听
sudo netstat -tlnp | grep :443
sudo netstat -tlnp | grep :80

# 测试配置语法
sudo nginx -t
```

### 2. SSL 证书测试

```bash
# 检查证书有效期
sudo openssl x509 -in /etc/letsencrypt/live/wuyinxinghai.cn/fullchain.pem -noout -dates

# 测试 SSL 连接
echo | openssl s_client -connect wuyinxinghai.cn:443 -servername wuyinxinghai.cn
```

### 3. 网站访问测试

- 访问 http://wuyinxinghai.cn（应该重定向到 HTTPS）
- 访问 https://wuyinxinghai.cn（应该正常显示）
- 检查浏览器地址栏的锁图标

## 🚨 故障排除

### 常见问题

#### 1. Nginx 启动失败

```bash
# 检查错误日志
sudo tail -f /var/log/nginx/error.log

# 检查配置语法
sudo nginx -t

# 检查端口占用
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

#### 2. SSL 证书问题

```bash
# 检查证书文件权限
sudo ls -la /etc/letsencrypt/live/wuyinxinghai.cn/

# 检查证书有效期
sudo certbot certificates

# 手动续期证书
sudo certbot renew --dry-run
```

#### 3. 防火墙问题

```bash
# 检查防火墙状态
sudo firewall-cmd --list-all

# 开放端口
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

### 恢复备份

如果配置出现问题，可以恢复备份：

```bash
# 恢复 Nginx 配置
sudo cp /etc/nginx/nginx.conf.backup /etc/nginx/nginx.conf
sudo cp -r /etc/nginx/conf.d.backup/* /etc/nginx/conf.d/

# 重启 Nginx
sudo systemctl restart nginx
```

## 📚 相关文档

- [Nginx 官方文档](http://nginx.org/en/docs/)
- [Let's Encrypt 文档](https://letsencrypt.org/docs/)
- [Certbot 文档](https://certbot.eff.org/docs/)

## 🆘 获取帮助

如果遇到问题，可以：

1. 检查脚本输出的错误信息
2. 查看 Nginx 错误日志：`sudo tail -f /var/log/nginx/error.log`
3. 查看 SSL 续期日志：`sudo tail -f /var/log/ssl_renew.log`
4. 运行测试脚本：`sudo bash scripts/test_apache_detection.sh`

## 📝 更新日志

- **v1.0** - 初始版本，支持基本的 SSL 配置
- **v1.1** - 添加自动续期功能
- **v1.2** - 优化错误处理和日志记录
