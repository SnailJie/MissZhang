#!/bin/bash

# SSL 证书自动续期脚本
# 适用于阿里云 OS 系统

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志文件
LOG_FILE="/var/log/ssl_renew.log"
DOMAIN="wuyinxinghai.cn"

echo "$(date): 开始 SSL 证书续期检查" | tee -a "$LOG_FILE"

# 检查证书是否即将过期（30天内）
check_cert_expiry() {
    local cert_file="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
    
    if [ ! -f "$cert_file" ]; then
        echo "$(date): 错误: 证书文件不存在: $cert_file" | tee -a "$LOG_FILE"
        return 1
    fi
    
    # 获取证书过期时间
    local expiry_date=$(openssl x509 -in "$cert_file" -noout -enddate | cut -d= -f2)
    local expiry_timestamp=$(date -d "$expiry_date" +%s)
    local current_timestamp=$(date +%s)
    local days_until_expiry=$(( (expiry_timestamp - current_timestamp) / 86400 ))
    
    echo "$(date): 证书将在 $days_until_expiry 天后过期" | tee -a "$LOG_FILE"
    
    if [ $days_until_expiry -le 30 ]; then
        echo "$(date): 警告: 证书将在 30 天内过期，需要续期" | tee -a "$LOG_FILE"
        return 0
    else
        echo "$(date): 证书有效期充足，无需续期" | tee -a "$LOG_FILE"
        return 1
    fi
}

# 续期证书
renew_cert() {
    echo "$(date): 开始续期 SSL 证书..." | tee -a "$LOG_FILE"
    
    # 停止 Nginx 服务（certbot 需要）
    echo "$(date): 停止 Nginx 服务..." | tee -a "$LOG_FILE"
    if systemctl is-active --quiet nginx; then
        systemctl stop nginx
        echo "$(date): Nginx 服务已停止" | tee -a "$LOG_FILE"
    fi
    
    # 运行 certbot 续期
    echo "$(date): 运行 certbot renew..." | tee -a "$LOG_FILE"
    if certbot renew --quiet --agree-tos --email admin@$DOMAIN; then
        echo "$(date): 证书续期成功" | tee -a "$LOG_FILE"
        
        # 启动 Nginx 服务
        echo "$(date): 启动 Nginx 服务..." | tee -a "$LOG_FILE"
        if systemctl start nginx; then
            echo "$(date): Nginx 服务启动成功" | tee -a "$LOG_FILE"
        else
            echo "$(date): 错误: Nginx 服务启动失败" | tee -a "$LOG_FILE"
            return 1
        fi
        
        # 检查 Nginx 配置
        echo "$(date): 检查 Nginx 配置..." | tee -a "$LOG_FILE"
        if nginx -t; then
            echo "$(date): Nginx 配置检查通过" | tee -a "$LOG_FILE"
        else
            echo "$(date): 错误: Nginx 配置检查失败" | tee -a "$LOG_FILE"
            return 1
        fi
        
        # 重新加载 Nginx 配置
        echo "$(date): 重新加载 Nginx 配置..." | tee -a "$LOG_FILE"
        if nginx -s reload; then
            echo "$(date): Nginx 配置重新加载成功" | tee -a "$LOG_FILE"
        else
            echo "$(date): 错误: Nginx 配置重新加载失败" | tee -a "$LOG_FILE"
            return 1
        fi
        
        echo "$(date): SSL 证书续期完成" | tee -a "$LOG_FILE"
        return 0
    else
        echo "$(date): 错误: 证书续期失败" | tee -a "$LOG_FILE"
        
        # 启动 Nginx 服务（即使续期失败）
        echo "$(date): 启动 Nginx 服务..." | tee -a "$LOG_FILE"
        systemctl start nginx
        
        return 1
    fi
}

# 发送通知（可选）
send_notification() {
    local message="$1"
    local status="$2"
    
    # 这里可以添加邮件、短信或其他通知方式
    # 例如：发送邮件到管理员
    if command -v mail &> /dev/null; then
        echo "$message" | mail -s "SSL 证书续期 $status" admin@$DOMAIN
    fi
    
    # 或者记录到系统日志
    logger "SSL 证书续期: $message"
}

# 主函数
main() {
    echo "$(date): ========================================" | tee -a "$LOG_FILE"
    echo "$(date): SSL 证书续期脚本开始执行" | tee -a "$LOG_FILE"
    
    # 检查是否以 root 权限运行
    if [ "$EUID" -ne 0 ]; then
        echo "$(date): 错误: 此脚本需要 root 权限" | tee -a "$LOG_FILE"
        exit 1
    fi
    
    # 检查 certbot 是否安装
    if ! command -v certbot &> /dev/null; then
        echo "$(date): 错误: certbot 未安装" | tee -a "$LOG_FILE"
        exit 1
    fi
    
    # 检查证书是否需要续期
    if check_cert_expiry; then
        echo "$(date): 证书需要续期，开始续期流程..." | tee -a "$LOG_FILE"
        
        if renew_cert; then
            echo "$(date): 证书续期成功完成" | tee -a "$LOG_FILE"
            send_notification "SSL 证书续期成功完成" "成功"
        else
            echo "$(date): 证书续期失败" | tee -a "$LOG_FILE"
            send_notification "SSL 证书续期失败，请手动检查" "失败"
            exit 1
        fi
    else
        echo "$(date): 证书无需续期" | tee -a "$LOG_FILE"
    fi
    
    echo "$(date): SSL 证书续期脚本执行完成" | tee -a "$LOG_FILE"
    echo "$(date): ========================================" | tee -a "$LOG_FILE"
}

# 执行主函数
main "$@"
