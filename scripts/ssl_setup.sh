#!/bin/bash

# Let's Encrypt SSL 证书申请和配置脚本
# 支持 Nginx 和 Apache 配置

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🔐 Let's Encrypt SSL 证书配置脚本"
echo "=================================="

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ 错误: 此脚本需要 root 权限${NC}"
    echo "请使用: sudo bash scripts/ssl_setup.sh"
    exit 1
fi

# 检查系统环境
echo -e "${BLUE}🔍 检查系统环境...${NC}"

# 检测操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    OS=$(uname -s)
    VER=$(uname -r)
fi

echo "操作系统: $OS $VER"

# 检测 Web 服务器
if command -v nginx &> /dev/null; then
    WEB_SERVER="nginx"
    echo -e "${GREEN}✅ 检测到 Nginx${NC}"
elif command -v apache2 &> /dev/null; then
    WEB_SERVER="apache2"
    echo -e "${GREEN}✅ 检测到 Apache${NC}"
elif command -v httpd &> /dev/null; then
    WEB_SERVER="httpd"
    echo -e "${GREEN}✅ 检测到 Apache (httpd)${NC}"
else
    echo -e "${YELLOW}⚠️  未检测到 Web 服务器${NC}"
    echo "请先安装 Nginx 或 Apache"
    exit 1
fi

# 获取用户输入
echo ""
echo -e "${BLUE}请输入域名信息:${NC}"

read -p "🌐 请输入你的域名 (例如: example.com): " DOMAIN_NAME
if [ -z "$DOMAIN_NAME" ]; then
    echo -e "${RED}❌ 域名不能为空${NC}"
    exit 1
fi

read -p "📧 请输入邮箱地址 (用于证书过期通知): " EMAIL_ADDRESS
if [ -z "$EMAIL_ADDRESS" ]; then
    echo -e "${RED}❌ 邮箱地址不能为空${NC}"
    exit 1
fi

# 检查域名解析
echo ""
echo -e "${YELLOW}🔍 检查域名解析...${NC}"
if ! nslookup "$DOMAIN_NAME" &> /dev/null; then
    echo -e "${RED}❌ 域名 $DOMAIN_NAME 无法解析${NC}"
    echo "请确保域名已正确解析到服务器 IP"
    exit 1
fi

SERVER_IP=$(curl -s ifconfig.me)
echo "服务器公网 IP: $SERVER_IP"
echo "域名解析检查: 通过"

# 安装 certbot
echo ""
echo -e "${YELLOW}📦 安装 certbot...${NC}"

case $OS in
    *"Ubuntu"*|*"Debian"*)
        echo "检测到 Ubuntu/Debian 系统"
        apt update
        apt install -y certbot python3-certbot-nginx python3-certbot-apache
        ;;
    *"CentOS"*|*"Red Hat"*|*"Rocky"*|*"Alma"*)
        echo "检测到 CentOS/RHEL 系统"
        if command -v dnf &> /dev/null; then
            dnf install -y certbot python3-certbot-nginx python3-certbot-apache
        else
            yum install -y certbot python3-certbot-nginx python3-certbot-apache
        fi
        ;;
    *)
        echo "检测到其他系统，尝试使用 snap 安装"
        if command -v snap &> /dev/null; then
            snap install --classic certbot
            ln -sf /snap/bin/certbot /usr/bin/certbot
        else
            echo -e "${RED}❌ 无法自动安装 certbot${NC}"
            echo "请手动安装 certbot: https://certbot.eff.org/"
            exit 1
        fi
        ;;
esac

echo -e "${GREEN}✅ certbot 安装完成${NC}"

# 创建 Web 服务器配置
echo ""
echo -e "${YELLOW}📝 创建 Web 服务器配置...${NC}"

if [ "$WEB_SERVER" = "nginx" ]; then
    # Nginx 配置
    NGINX_CONF="/etc/nginx/sites-available/$DOMAIN_NAME"
    NGINX_ENABLED="/etc/nginx/sites-enabled/$DOMAIN_NAME"
    
    cat > "$NGINX_CONF" << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;
    
    # 临时重定向到 HTTPS（证书申请后）
    location / {
        return 301 https://\$server_name\$request_uri;
    }
    
    # Let's Encrypt 验证
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;
    
    # SSL 配置（证书申请后自动配置）
    # ssl_certificate /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem;
    
    # 应用配置
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # 静态文件
    location /static/ {
        alias $PROJECT_ROOT/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

    # 启用站点
    ln -sf "$NGINX_CONF" "$NGINX_ENABLED"
    
    # 测试配置
    nginx -t
    systemctl reload nginx
    
    echo -e "${GREEN}✅ Nginx 配置创建完成${NC}"
    
elif [ "$WEB_SERVER" = "apache2" ] || [ "$WEB_SERVER" = "httpd" ]; then
    # Apache 配置
    APACHE_CONF="/etc/apache2/sites-available/$DOMAIN_NAME.conf"
    
    cat > "$APACHE_CONF" << EOF
<VirtualHost *:80>
    ServerName $DOMAIN_NAME
    ServerAlias www.$DOMAIN_NAME
    DocumentRoot /var/www/html
    
    # Let's Encrypt 验证
    Alias /.well-known/acme-challenge/ /var/www/html/.well-known/acme-challenge/
    
    # 重定向到 HTTPS
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
</VirtualHost>

<VirtualHost *:443>
    ServerName $DOMAIN_NAME
    ServerAlias www.$DOMAIN_NAME
    
    # SSL 配置（证书申请后自动配置）
    # SSLEngine on
    # SSLCertificateFile /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem
    # SSLCertificateKeyFile /etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem
    
    # 应用配置
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
    
    # 静态文件
    Alias /static/ $PROJECT_ROOT/app/static/
    <Directory "$PROJECT_ROOT/app/static/">
        Require all granted
        ExpiresActive On
        ExpiresDefault "access plus 1 year"
    </Directory>
</VirtualHost>
EOF

    # 启用必要的模块
    a2enmod ssl
    a2enmod proxy
    a2enmod proxy_http
    a2enmod rewrite
    
    # 启用站点
    a2ensite "$DOMAIN_NAME.conf"
    
    # 测试配置
    apache2ctl configtest
    systemctl reload apache2
    
    echo -e "${GREEN}✅ Apache 配置创建完成${NC}"
fi

# 申请 SSL 证书
echo ""
echo -e "${YELLOW}🔐 申请 Let's Encrypt SSL 证书...${NC}"

if [ "$WEB_SERVER" = "nginx" ]; then
    certbot --nginx -d "$DOMAIN_NAME" -d "www.$DOMAIN_NAME" --email "$EMAIL_ADDRESS" --agree-tos --non-interactive
elif [ "$WEB_SERVER" = "apache2" ] || [ "$WEB_SERVER" = "httpd" ]; then
    certbot --apache -d "$DOMAIN_NAME" -d "www.$DOMAIN_NAME" --email "$EMAIL_ADDRESS" --agree-tos --non-interactive
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ SSL 证书申请成功！${NC}"
else
    echo -e "${RED}❌ SSL 证书申请失败${NC}"
    echo "请检查域名解析和 Web 服务器配置"
    exit 1
fi

# 配置自动续期
echo ""
echo -e "${YELLOW}🔄 配置自动续期...${NC}"

# 创建续期脚本
cat > /usr/local/bin/renew-ssl.sh << 'EOF'
#!/bin/bash
# SSL 证书自动续期脚本

DOMAIN="$1"
if [ -z "$DOMAIN" ]; then
    echo "用法: $0 <域名>"
    exit 1
fi

# 尝试续期
certbot renew --quiet

# 检查是否需要重启 Web 服务器
if [ $? -eq 0 ]; then
    # 重启 Web 服务器
    if systemctl is-active --quiet nginx; then
        systemctl reload nginx
        echo "$(date): SSL 证书续期成功，Nginx 已重载"
    elif systemctl is-active --quiet apache2; then
        systemctl reload apache2
        echo "$(date): SSL 证书续期成功，Apache 已重载"
    elif systemctl is-active --quiet httpd; then
        systemctl reload httpd
        echo "$(date): SSL 证书续期成功，Apache 已重载"
    fi
else
    echo "$(date): SSL 证书续期失败"
fi
EOF

chmod +x /usr/local/bin/renew-ssl.sh

# 添加到 crontab
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/local/bin/renew-ssl.sh $DOMAIN_NAME") | crontab -

echo -e "${GREEN}✅ 自动续期配置完成${NC}"

# 测试 HTTPS 访问
echo ""
echo -e "${YELLOW}🧪 测试 HTTPS 访问...${NC}"

sleep 5  # 等待证书生效

if curl -s -I "https://$DOMAIN_NAME" | grep -q "HTTP/2\|HTTP/1.1"; then
    echo -e "${GREEN}✅ HTTPS 访问正常${NC}"
else
    echo -e "${YELLOW}⚠️  HTTPS 访问测试失败，可能需要等待几分钟${NC}"
fi

# 显示证书信息
echo ""
echo -e "${GREEN}📋 SSL 证书信息:${NC}"
echo "=================="
certbot certificates

# 更新项目配置
echo ""
echo -e "${YELLOW}📝 更新项目配置...${NC}"

# 更新 .env 文件中的微信回调地址
if [ -f "$PROJECT_ROOT/.env" ]; then
    sed -i.bak "s|WECHAT_REDIRECT_URI=.*|WECHAT_REDIRECT_URI=https://$DOMAIN_NAME/wechat/callback|" "$PROJECT_ROOT/.env"
    echo -e "${GREEN}✅ 已更新微信回调地址为 HTTPS${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Let's Encrypt SSL 证书配置完成！${NC}"
echo ""
echo -e "${BLUE}📚 配置摘要:${NC}"
echo "域名: $DOMAIN_NAME"
echo "Web 服务器: $WEB_SERVER"
echo "SSL 证书: Let's Encrypt"
echo "自动续期: 已配置 (每天中午 12 点)"
echo ""
echo -e "${YELLOW}⚠️  重要提醒:${NC}"
echo "1. 证书有效期为 90 天，会自动续期"
echo "2. 确保服务器防火墙开放 80 和 443 端口"
echo "3. 在微信公众平台更新授权回调域名"
echo "4. 运行 'bash scripts/status.sh' 检查配置"
echo "5. 运行 'sudo bash scripts/deploy.sh' 部署应用"
echo ""
echo -e "${BLUE}🔗 访问地址:${NC}"
echo "HTTP:  http://$DOMAIN_NAME (自动重定向到 HTTPS)"
echo "HTTPS: https://$DOMAIN_NAME"
