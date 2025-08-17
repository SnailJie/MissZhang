#!/usr/bin/env python3
"""
邮件服务测试脚本
直接从 env.example 文件读取配置进行测试
"""

import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from datetime import datetime

def load_env_config(config_file='env.example'):
    """从配置文件加载配置"""
    env_file = Path(__file__).parent / config_file
    if not env_file.exists():
        print(f"❌ 配置文件不存在: {env_file}")
        return None
    
    config = {}
    print(f"📖 正在读取配置文件: {env_file}")
    with open(env_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
                # 调试：显示读取的配置项
                if key.strip().startswith('SMTP_') or key.strip().startswith('EMAIL_') or key.strip() == 'SENDER_EMAIL':
                    print(f"  第{line_num}行: {key.strip()} = {value.strip()}")
    
    return config

def parse_recipients(recipients_str):
    """解析收件人邮箱列表"""
    if not recipients_str:
        return []
    return [email.strip() for email in recipients_str.split(',') if email.strip()]

def test_smtp_connection(config):
    """测试SMTP连接"""
    print("🔧 测试SMTP连接...")
    
    smtp_server = config.get('SMTP_SERVER')
    smtp_port = int(config.get('SMTP_PORT', '587'))
    smtp_user = config.get('SMTP_USER')
    smtp_password = config.get('SMTP_PASSWORD')
    
    if not smtp_server or not smtp_user or not smtp_password:
        print("❌ SMTP配置不完整")
        return False
    
    try:
        print(f"📡 连接到 {smtp_server}:{smtp_port}")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print("🔒 启动TLS加密...")
            server.starttls()
            print("🔑 验证登录凭据...")
            server.login(smtp_user, smtp_password)
            print("✅ SMTP连接测试成功")
            return True
    except Exception as e:
        print(f"❌ SMTP连接测试失败: {e}")
        return False

def send_test_email(config):
    """发送测试邮件"""
    print("📧 发送测试邮件...")
    
    smtp_server = config.get('SMTP_SERVER')
    smtp_port = int(config.get('SMTP_PORT', '587'))
    smtp_user = config.get('SMTP_USER')
    smtp_password = config.get('SMTP_PASSWORD')
    sender_email = config.get('SENDER_EMAIL', smtp_user)
    recipients = parse_recipients(config.get('EMAIL_RECIPIENTS', ''))
    
    if not recipients:
        print("❌ 未配置收件人邮箱")
        return False
    
    try:
        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = f"Miss Zhang 邮件服务测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 邮件正文
        body = f"""
        <html>
        <head>
            <meta charset="utf-8">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2c3e50;">📧 Miss Zhang 邮件服务测试</h2>
            
            <div style="background-color: #d4edda; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745; margin: 20px 0;">
                <h3 style="color: #155724; margin-top: 0;">✅ 测试成功</h3>
                <p style="margin: 5px 0;"><strong>测试时间：</strong>{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
                <p style="margin: 5px 0;"><strong>发送邮箱：</strong>{sender_email}</p>
                <p style="margin: 5px 0;"><strong>SMTP服务器：</strong>{smtp_server}:{smtp_port}</p>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h4 style="color: #495057; margin-top: 0;">📋 配置信息</h4>
                <ul>
                    <li><strong>SMTP服务器：</strong> {smtp_server}</li>
                    <li><strong>SMTP端口：</strong> {smtp_port}</li>
                    <li><strong>发件人：</strong> {sender_email}</li>
                    <li><strong>收件人：</strong> {', '.join(recipients)}</li>
                </ul>
            </div>
            
            <div style="background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0;"><strong>🎉 恭喜！</strong> 如果您收到这封邮件，说明邮件服务配置正确，可以正常发送邮件。</p>
            </div>
            
            <hr style="border: none; border-top: 1px solid #dee2e6; margin: 30px 0;">
            <p style="font-size: 12px; color: #6c757d; text-align: center;">
                此邮件由 Miss Zhang 排班管理系统邮件服务测试自动发送<br>
                测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        # 发送邮件
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        print(f"✅ 测试邮件发送成功")
        print(f"📬 收件人: {', '.join(recipients)}")
        return True
        
    except Exception as e:
        print(f"❌ 测试邮件发送失败: {e}")
        return False

def is_example_config(config):
    """检查是否为示例配置"""
    example_values = [
        'your_email@126.com',
        'your_email_password_here', 
        'admin@hospital.com',
        'manager@hospital.com'
    ]
    
    smtp_user = config.get('SMTP_USER', '')
    smtp_password = config.get('SMTP_PASSWORD', '')
    recipients = config.get('EMAIL_RECIPIENTS', '')
    
    return any(val in [smtp_user, smtp_password, recipients] for val in example_values)

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Miss Zhang 邮件服务测试")
    print("=" * 60)
    
    # 检查是否有测试配置文件
    test_file = Path(__file__).parent / 'env.test'
    if test_file.exists():
        print("📖 检测到 env.test 文件，使用真实配置进行测试...")
        config = load_env_config('env.test')
    else:
        print("📖 从 env.example 加载配置...")
        config = load_env_config('env.example')
    
    if not config:
        print("❌ 配置加载失败")
        return False
    
    print("✅ 配置加载成功")
    
    # 显示配置信息
    print("\n📋 当前配置:")
    print(f"  SMTP服务器: {config.get('SMTP_SERVER', '未配置')}")
    print(f"  SMTP端口: {config.get('SMTP_PORT', '未配置')}")
    print(f"  发件人: {config.get('SENDER_EMAIL', config.get('SMTP_USER', '未配置'))}")
    recipients = parse_recipients(config.get('EMAIL_RECIPIENTS', ''))
    print(f"  收件人: {', '.join(recipients) if recipients else '未配置'}")
    
    # 检查是否为示例配置
    if is_example_config(config):
        print("\n⚠️  检测到示例配置")
        print("=" * 60)
        print("📋 配置说明:")
        print("  env.example 文件包含的是示例配置，不是真实的邮箱凭据")
        print("  要进行实际的邮件服务测试，请：")
        print("  1. 复制 env.example 为 .env 文件")
        print("  2. 在 .env 文件中填入真实的邮箱配置")
        print("  3. 或直接修改 env.example 文件中的配置")
        print("\n📧 需要修改的配置项:")
        print("  • SMTP_USER: 改为真实邮箱地址")
        print("  • SMTP_PASSWORD: 改为邮箱授权码")
        print("  • SENDER_EMAIL: 改为发件人邮箱")
        print("  • EMAIL_RECIPIENTS: 改为接收邮件的邮箱")
        print("\n🔍 当前示例配置诊断:")
        
        # 尝试连接以获得更详细的错误信息
        print("\n" + "─" * 40)
        print("🔧 尝试连接测试（预期会失败）...")
        test_smtp_connection(config)
        
        print("\n💡 解决方案:")
        print("  对于126邮箱，请：")
        print("  1. 登录 mail.126.com")
        print("  2. 设置 → POP3/SMTP/IMAP")
        print("  3. 开启SMTP服务")
        print("  4. 获取授权码（不是登录密码）")
        print("  5. 使用授权码作为 SMTP_PASSWORD")
        
        return False
    
    # 检查必需配置
    required_fields = ['SMTP_SERVER', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASSWORD', 'EMAIL_RECIPIENTS']
    missing_fields = [field for field in required_fields if not config.get(field)]
    
    if missing_fields:
        print(f"\n❌ 缺少必需配置: {', '.join(missing_fields)}")
        return False
    
    print("\n" + "─" * 40)
    
    # 测试SMTP连接
    if not test_smtp_connection(config):
        return False
    
    print("\n" + "─" * 40)
    
    # 发送测试邮件
    if not send_test_email(config):
        return False
    
    print("\n" + "=" * 60)
    print("🎉 所有测试完成！邮件服务工作正常")
    print("💡 请检查收件箱（包括垃圾邮件文件夹）确认是否收到测试邮件")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
