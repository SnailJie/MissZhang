# 域名配置指南

## 腾讯云域名解析设置

1. **登录腾讯云控制台**
   - 访问 https://console.cloud.tencent.com/
   - 进入"域名与网站" → "域名管理"

2. **找到你的域名**
   - 点击域名进入管理页面
   - 选择"解析"选项卡

3. **添加解析记录**
   - 点击"添加记录"
   - 填写以下信息：
     - **记录类型**: A
     - **主机记录**: @ (或者 www，或者你想要的子域名)
     - **记录值**: 172.31.73.92
     - **TTL**: 600 (或默认值)
   - 点击"确定"保存

4. **验证解析**
   - 等待几分钟让解析生效
   - 使用 `nslookup yourdomain.com` 或 `ping yourdomain.com` 验证

## 阿里云服务器配置

### 1. 安全组设置
在阿里云控制台配置安全组，开放以下端口：
- **80端口** (HTTP)
- **443端口** (HTTPS，如果需要SSL)
- **8000端口** (当前应用端口)

### 2. 修改应用端口
将应用改为使用80端口（标准HTTP端口）：

```bash
# 编辑 gunicorn.conf.py
bind = "0.0.0.0:80"  # 改为80端口
```

### 3. 防火墙设置
在服务器上配置防火墙：

```bash
# Ubuntu/Debian
sudo ufw allow 80
sudo ufw allow 443

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

## 部署步骤

1. **上传项目到服务器**
   ```bash
   scp -r /path/to/missZhang root@172.31.73.92:/opt/
   ```

2. **SSH连接到服务器**
   ```bash
   ssh root@172.31.73.92
   ```

3. **修改端口配置**
   ```bash
   cd /opt/missZhang
   # 编辑 gunicorn.conf.py，将 bind 改为 "0.0.0.0:80"
   ```

4. **启动应用**
   ```bash
   bash scripts/start.sh
   ```

5. **验证访问**
   - 浏览器访问: http://yourdomain.com
   - 或直接访问: http://172.31.73.92

## 可选：配置Nginx反向代理

如果需要更好的性能和SSL支持，可以配置Nginx：

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 故障排除

1. **域名无法访问**
   - 检查域名解析是否正确
   - 检查服务器防火墙设置
   - 检查阿里云安全组配置

2. **应用无法启动**
   - 检查端口是否被占用
   - 查看日志文件: `logs/gunicorn.error.log`

3. **权限问题**
   - 确保脚本有执行权限: `chmod +x scripts/*.sh`
   - 确保目录有写入权限 