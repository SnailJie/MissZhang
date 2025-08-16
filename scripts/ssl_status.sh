#!/bin/bash

# SSL 状态检查脚本
# 用于检查 SSL 证书状态和配置

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔐 SSL 状态检查"
echo "================"

# 检查是否为 root 用户
if [ "$EUID" -eq 0 ]; then
    echo -e "${BLUE}🔑 检测到 root 权限${NC}"
else
    echo -e "${YELLOW}⚠️  建议使用 root 权限运行以获得完整信息${NC}"
fi

# 检查 certbot 是否安装
echo ""
echo -e "${BLUE}📦 检查 certbot 安装状态...${NC}"
if command -v certbot &> /dev/null; then
    CERTBOT_VERSION=$(certbot --version)
    echo -e "${GREEN}✅ certbot 已安装: $CERTBOT_VERSION${NC}"
else
    echo -e "${RED}❌ certbot 未安装${NC}"
    echo "请运行: sudo bash scripts/ssl_setup.sh"
    exit 1
fi

# 检查 SSL 证书状态
echo ""
echo -e "${BLUE}🔐 检查 SSL 证书状态...${NC}"
if [ "$EUID" -eq 0 ]; then
    CERTBOT_CERTS=$(certbot certificates 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$CERTBOT_CERTS" ]; then
        echo -e "${GREEN}✅ 找到 SSL 证书:${NC}"
        echo "$CERTBOT_CERTS"
    else
        echo -e "${YELLOW}⚠️  未找到 SSL 证书${NC}"
        echo "请运行: sudo bash scripts/ssl_setup.sh"
    fi
else
    echo -e "${YELLOW}⚠️  需要 root 权限查看证书状态${NC}"
    echo "请使用: sudo bash scripts/ssl_status.sh"
fi

# 检查 Web 服务器状态
echo ""
echo -e "${BLUE}🌐 检查 Web 服务器状态...${NC}"

# 检查 Nginx
if command -v nginx &> /dev/null; then
    if systemctl is-active --quiet nginx; then
        echo -e "${GREEN}✅ Nginx 正在运行${NC}"
        NGINX_STATUS="running"
    else
        echo -e "${YELLOW}⚠️  Nginx 未运行${NC}"
        NGINX_STATUS="stopped"
    fi
else
    echo -e "${YELLOW}⚠️  Nginx 未安装${NC}"
    NGINX_STATUS="not_installed"
fi

# 检查 Apache
if command -v apache2 &> /dev/null || command -v httpd &> /dev/null; then
    if systemctl is-active --quiet apache2 2>/dev/null || systemctl is-active --quiet httpd 2>/dev/null; then
        echo -e "${GREEN}✅ Apache 正在运行${NC}"
        APACHE_STATUS="running"
    else
        echo -e "${YELLOW}⚠️  Apache 未运行${NC}"
        APACHE_STATUS="stopped"
    fi
else
    echo -e "${YELLOW}⚠️  Apache 未安装${NC}"
    APACHE_STATUS="not_installed"
fi

# 检查端口状态
echo ""
echo -e "${BLUE}🔌 检查端口状态...${NC}"

# 检查 80 端口
if netstat -tlnp 2>/dev/null | grep -q ":80 "; then
    echo -e "${GREEN}✅ 端口 80 (HTTP) 已开放${NC}"
    HTTP_PORT_OPEN=true
else
    echo -e "${RED}❌ 端口 80 (HTTP) 未开放${NC}"
    HTTP_PORT_OPEN=false
fi

# 检查 443 端口
if netstat -tlnp 2>/dev/null | grep -q ":443 "; then
    echo -e "${GREEN}✅ 端口 443 (HTTPS) 已开放${NC}"
    HTTPS_PORT_OPEN=true
else
    echo -e "${RED}❌ 端口 443 (HTTPS) 未开放${NC}"
    HTTPS_PORT_OPEN=false
fi

# 检查防火墙状态
echo ""
echo -e "${BLUE}🔥 检查防火墙状态...${NC}"

# 检查 UFW
if command -v ufw &> /dev/null; then
    UFW_STATUS=$(ufw status 2>/dev/null | head -1)
    if echo "$UFW_STATUS" | grep -q "Status: active"; then
        echo -e "${GREEN}✅ UFW 防火墙已启用${NC}"
        echo "UFW 状态: $UFW_STATUS"
    else
        echo -e "${YELLOW}⚠️  UFW 防火墙未启用${NC}"
    fi
fi

# 检查 iptables
if command -v iptables &> /dev/null; then
    IPTABLES_RULES=$(iptables -L -n 2>/dev/null | wc -l)
    if [ "$IPTABLES_RULES" -gt 8 ]; then
        echo -e "${GREEN}✅ iptables 规则已配置${NC}"
        echo "规则数量: $IPTABLES_RULES"
    else
        echo -e "${YELLOW}⚠️  iptables 规则较少${NC}"
    fi
fi

# 检查域名解析
echo ""
echo -e "${BLUE}🌍 检查域名解析...${NC}"

# 从 .env 文件读取域名
if [ -f ".env" ]; then
    DOMAIN=$(grep "WECHAT_REDIRECT_URI" .env | sed 's/.*https:\/\///' | sed 's/\/.*//')
    if [ -n "$DOMAIN" ]; then
        echo "检测到域名: $DOMAIN"
        
        # 检查域名解析
        # 检测可用的 DNS 查询工具
        DNS_TOOL=""
        if command -v dig &> /dev/null; then
            DNS_TOOL="dig"
        elif command -v host &> /dev/null; then
            DNS_TOOL="host"
        elif command -v nslookup &> /dev/null; then
            DNS_TOOL="nslookup"
        fi
        
        if [ -n "$DNS_TOOL" ]; then
            if [ "$DNS_TOOL" = "dig" ]; then
                RESOLVED_IP=$(dig +short "$DOMAIN" | head -1)
                if [ -n "$RESOLVED_IP" ]; then
                    echo -e "${GREEN}✅ 域名解析正常${NC}"
                    echo "解析到 IP: $RESOLVED_IP"
                    
                    # 获取服务器公网 IP
                    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "unknown")
                    if [ "$SERVER_IP" != "unknown" ]; then
                        if [ "$RESOLVED_IP" = "$SERVER_IP" ]; then
                            echo -e "${GREEN}✅ 域名正确解析到服务器${NC}"
                        else
                            echo -e "${YELLOW}⚠️  域名解析的 IP 与服务器 IP 不匹配${NC}"
                            echo "域名解析 IP: $RESOLVED_IP"
                            echo "服务器公网 IP: $SERVER_IP"
                        fi
                    fi
                else
                    echo -e "${RED}❌ 域名解析失败${NC}"
                fi
            elif [ "$DNS_TOOL" = "host" ]; then
                RESOLVED_IP=$(host "$DOMAIN" | grep "has address" | awk '{print $NF}' | head -1)
                if [ -n "$RESOLVED_IP" ]; then
                    echo -e "${GREEN}✅ 域名解析正常${NC}"
                    echo "解析到 IP: $RESOLVED_IP"
                    
                    # 获取服务器公网 IP
                    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "unknown")
                    if [ "$SERVER_IP" != "unknown" ]; then
                        if [ "$RESOLVED_IP" = "$SERVER_IP" ]; then
                            echo -e "${GREEN}✅ 域名正确解析到服务器${NC}"
                        else
                            echo -e "${YELLOW}⚠️  域名解析的 IP 与服务器 IP 不匹配${NC}"
                            echo "域名解析 IP: $RESOLVED_IP"
                            echo "服务器公网 IP: $SERVER_IP"
                        fi
                    fi
                else
                    echo -e "${RED}❌ 域名解析失败${NC}"
                fi
            elif [ "$DNS_TOOL" = "nslookup" ]; then
                if nslookup "$DOMAIN" &> /dev/null; then
                    echo -e "${GREEN}✅ 域名解析正常${NC}"
                    
                    # 获取解析的 IP
                    RESOLVED_IP=$(nslookup "$DOMAIN" | grep "Address:" | tail -1 | awk '{print $2}')
                    if [ -n "$RESOLVED_IP" ]; then
                        echo "解析到 IP: $RESOLVED_IP"
                        
                        # 获取服务器公网 IP
                        SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "unknown")
                        if [ "$SERVER_IP" != "unknown" ]; then
                            if [ "$RESOLVED_IP" = "$SERVER_IP" ]; then
                                echo -e "${GREEN}✅ 域名正确解析到服务器${NC}"
                            else
                                echo -e "${YELLOW}⚠️  域名解析的 IP 与服务器 IP 不匹配${NC}"
                                echo "域名解析 IP: $RESOLVED_IP"
                                echo "服务器公网 IP: $SERVER_IP"
                            fi
                        fi
                    fi
                else
                    echo -e "${RED}❌ 域名解析失败${NC}"
                fi
            fi
        else
            echo -e "${YELLOW}⚠️  未找到 DNS 查询工具${NC}"
            echo "请安装 bind-utils 包: sudo yum install -y bind-utils"
        fi
    else
        echo -e "${YELLOW}⚠️  未在 .env 文件中找到域名配置${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  未找到 .env 配置文件${NC}"
fi

# 检查 SSL 配置
echo ""
echo -e "${BLUE}🔒 检查 SSL 配置...${NC}"

if [ -n "$DOMAIN" ]; then
    # 测试 HTTP 访问
    if [ "$HTTP_PORT_OPEN" = true ]; then
        HTTP_RESPONSE=$(curl -s -I "http://$DOMAIN" 2>/dev/null | head -1)
        if [ -n "$HTTP_RESPONSE" ]; then
            echo -e "${GREEN}✅ HTTP 访问正常${NC}"
            echo "HTTP 响应: $HTTP_RESPONSE"
        else
            echo -e "${RED}❌ HTTP 访问失败${NC}"
        fi
    fi
    
    # 测试 HTTPS 访问
    if [ "$HTTPS_PORT_OPEN" = true ]; then
        HTTPS_RESPONSE=$(curl -s -I "https://$DOMAIN" 2>/dev/null | head -1)
        if [ -n "$HTTPS_RESPONSE" ]; then
            echo -e "${GREEN}✅ HTTPS 访问正常${NC}"
            echo "HTTPS 响应: $HTTPS_RESPONSE"
            
            # 检查证书信息
            if command -v openssl &> /dev/null; then
                CERT_INFO=$(echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
                if [ -n "$CERT_INFO" ]; then
                    echo "证书信息: $CERT_INFO"
                fi
            fi
        else
            echo -e "${RED}❌ HTTPS 访问失败${NC}"
        fi
    fi
fi

# 检查自动续期配置
echo ""
echo -e "${BLUE}🔄 检查自动续期配置...${NC}"

if [ "$EUID" -eq 0 ]; then
    # 检查 crontab 中的续期任务
    CRON_RENEWAL=$(crontab -l 2>/dev/null | grep -i "certbot\|renew")
    if [ -n "$CRON_RENEWAL" ]; then
        echo -e "${GREEN}✅ 自动续期任务已配置${NC}"
        echo "续期任务: $CRON_RENEWAL"
    else
        echo -e "${YELLOW}⚠️  自动续期任务未配置${NC}"
    fi
    
    # 检查 certbot 定时器
    if systemctl list-timers | grep -q "certbot"; then
        echo -e "${GREEN}✅ certbot 定时器已启用${NC}"
    else
        echo -e "${YELLOW}⚠️  certbot 定时器未启用${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  需要 root 权限检查续期配置${NC}"
fi

# 总结和建议
echo ""
echo -e "${BLUE}📋 检查总结:${NC}"
echo "=================="

# 计算检查项目
TOTAL_CHECKS=0
PASSED_CHECKS=0

# certbot 安装
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if command -v certbot &> /dev/null; then
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi

# 端口开放
TOTAL_CHECKS=$((TOTAL_CHECKS + 2))
if [ "$HTTP_PORT_OPEN" = true ]; then
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi
if [ "$HTTPS_PORT_OPEN" = true ]; then
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi

# Web 服务器
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if [ "$NGINX_STATUS" = "running" ] || [ "$APACHE_STATUS" = "running" ]; then
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi

echo "检查项目: $PASSED_CHECKS/$TOTAL_CHECKS 通过"

# 提供建议
echo ""
echo -e "${BLUE}💡 建议和下一步:${NC}"

if [ "$PASSED_CHECKS" -eq "$TOTAL_CHECKS" ]; then
    echo -e "${GREEN}🎉 SSL 配置状态良好！${NC}"
    echo "建议:"
    echo "1. 定期检查证书状态: sudo certbot certificates"
    echo "2. 测试自动续期: sudo certbot renew --dry-run"
    echo "3. 监控证书过期时间"
else
    echo -e "${YELLOW}⚠️  发现一些问题需要解决${NC}"
    echo "建议:"
    
    if ! command -v certbot &> /dev/null; then
        echo "1. 安装 certbot: sudo bash scripts/ssl_setup.sh"
    fi
    
    if [ "$HTTP_PORT_OPEN" = false ]; then
        echo "2. 开放 HTTP 端口 (80): sudo ufw allow 80"
    fi
    
    if [ "$HTTPS_PORT_OPEN" = false ]; then
        echo "3. 开放 HTTPS 端口 (443): sudo ufw allow 443"
    fi
    
    if [ "$NGINX_STATUS" != "running" ] && [ "$APACHE_STATUS" != "running" ]; then
        echo "4. 启动 Web 服务器或安装 Web 服务器"
    fi
    
    echo "5. 运行完整配置: sudo bash scripts/ssl_setup.sh"
fi

echo ""
echo -e "${BLUE}📚 更多信息:${NC}"
echo "- 查看详细指南: docs/ssl-setup-guide.md"
echo "- 运行配置脚本: sudo bash scripts/ssl_setup.sh"
echo "- 检查部署状态: bash scripts/status.sh"
