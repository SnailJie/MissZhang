"""
邮件服务模块
用于发送排班表上传通知邮件
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


class EmailService:
    """邮件发送服务"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.sender_email = os.getenv('SENDER_EMAIL', self.smtp_user)
        self.recipient_emails = self._parse_recipients()
        
    def _parse_recipients(self) -> List[str]:
        """解析收件人邮箱列表"""
        recipients_str = os.getenv('EMAIL_RECIPIENTS', '')
        if not recipients_str:
            return []
        
        # 支持逗号分隔的多个邮箱
        return [email.strip() for email in recipients_str.split(',') if email.strip()]
    
    def is_configured(self) -> bool:
        """检查邮件服务是否已配置"""
        return bool(
            self.smtp_user and 
            self.smtp_password and 
            self.recipient_emails
        )
    
    def send_schedule_notification(
        self, 
        week_info: Dict[str, str],
        image_path: Path,
        user_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        发送排班表上传通知邮件
        
        Args:
            week_info: 包含周次信息的字典
            image_path: 上传的图片路径
            user_info: 上传用户的信息
            
        Returns:
            bool: 发送是否成功
        """
        if not self.is_configured():
            print("邮件服务未配置完成")
            return False
            
        if not image_path.exists():
            print(f"图片文件不存在: {image_path}")
            return False
        
        try:
            # 创建邮件对象
            msg = MIMEMultipart('related')
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.recipient_emails)
            msg['Subject'] = f"排班表上传通知 - {week_info.get('label', '未知周次')}"
            
            # 构建邮件内容
            body = self._build_email_body(week_info, user_info)
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # 添加图片附件
            with open(image_path, 'rb') as f:
                img_data = f.read()
                img = MIMEImage(img_data)
                img.add_header('Content-Disposition', 
                              f'attachment; filename="{image_path.name}"')
                msg.attach(img)
            
            # 发送邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            print(f"邮件发送成功: {week_info.get('label', '未知周次')}")
            return True
            
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False
    
    def _build_email_body(
        self, 
        week_info: Dict[str, str], 
        user_info: Optional[Dict[str, Any]]
    ) -> str:
        """构建邮件正文内容"""
        current_time = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        
        # 用户信息部分
        user_section = ""
        if user_info:
            user_name = user_info.get('name', '未知用户')
            hospital = user_info.get('hospital', '未知医院')
            department = user_info.get('department', '未知科室')
            user_section = f"""
            <p><strong>上传用户信息：</strong></p>
            <ul>
                <li>姓名：{user_name}</li>
                <li>医院：{hospital}</li>
                <li>科室：{department}</li>
            </ul>
            """
        
        body = f"""
        <html>
        <head>
            <meta charset="utf-8">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2c3e50;">排班表上传通知</h2>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="color: #495057; margin-top: 0;">排班信息</h3>
                <p><strong>周次：</strong>{week_info.get('label', '未知周次')}</p>
                <p><strong>文件名：</strong>{week_info.get('filename', '未知文件')}</p>
                <p><strong>上传时间：</strong>{current_time}</p>
            </div>
            
            {user_section}
            
            <div style="background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0;"><strong>提示：</strong>排班表图片已作为附件发送，请查看邮件附件。</p>
            </div>
            
            <hr style="border: none; border-top: 1px solid #dee2e6; margin: 30px 0;">
            <p style="font-size: 12px; color: #6c757d; text-align: center;">
                此邮件由 Miss Zhang 排班管理系统自动发送<br>
                如有问题，请联系系统管理员
            </p>
        </body>
        </html>
        """
        
        return body
    
    def test_connection(self) -> Dict[str, Any]:
        """测试邮件服务连接"""
        if not self.is_configured():
            return {
                "success": False,
                "message": "邮件服务未配置完成",
                "details": {
                    "smtp_user": bool(self.smtp_user),
                    "smtp_password": bool(self.smtp_password),
                    "recipients": bool(self.recipient_emails)
                }
            }
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                
            return {
                "success": True,
                "message": "邮件服务连接成功",
                "config": {
                    "smtp_server": self.smtp_server,
                    "smtp_port": self.smtp_port,
                    "sender": self.sender_email,
                    "recipients": self.recipient_emails
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"邮件服务连接失败: {str(e)}"
            }
