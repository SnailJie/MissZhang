# 网易126邮箱配置详细步骤

## 1. 登录126邮箱

前往 [网易126邮箱](https://mail.126.com/) 并登录您的账号。

## 2. 开启SMTP服务

1. 点击邮箱页面上方的 **"设置"** 
2. 选择 **"POP3/SMTP/IMAP"** 选项
3. 找到 **"SMTP服务"** 并选择 **"开启"**
4. 可能需要验证手机号码或其他身份验证

## 3. 获取授权码

1. 在SMTP服务开启后，系统会提示设置授权码
2. 按照提示完成手机验证或其他身份验证步骤
3. 记录下生成的授权码（这不是您的邮箱登录密码）

## 4. 配置环境变量

在 `.env` 文件中配置以下参数：

```bash
# 网易126邮箱配置
SMTP_SERVER=smtp.126.com
SMTP_PORT=587
SMTP_USER=your_email@126.com        # 替换为您的126邮箱
SMTP_PASSWORD=your_auth_code_here    # 替换为步骤3获取的授权码
SENDER_EMAIL=your_email@126.com      # 替换为您的126邮箱

# 收件人邮箱
EMAIL_RECIPIENTS=admin@hospital.com,manager@hospital.com
```

## 5. 测试配置

启动应用后，访问测试接口验证配置：

```bash
curl http://localhost:5000/api/email/test
```

成功返回示例：
```json
{
  "success": true,
  "message": "邮件服务连接成功",
  "config": {
    "smtp_server": "smtp.126.com",
    "smtp_port": 587,
    "sender": "your_email@126.com",
    "recipients": ["admin@hospital.com", "manager@hospital.com"]
  }
}
```

## 常见问题

### Q: 提示"授权失败"或"用户名密码错误"
A: 确认以下几点：
- 使用的是授权码，不是邮箱登录密码
- 已经开启了SMTP服务
- 邮箱地址和授权码都正确无误

### Q: 连接超时
A: 检查网络连接和防火墙设置，确保能访问smtp.126.com:587

### Q: 如何重新获取授权码？
A: 在邮箱设置的POP3/SMTP/IMAP页面可以重新生成授权码

## 网易126邮箱优势

- 🇨🇳 国内服务器，连接稳定
- 📧 免费邮箱服务
- 🔐 支持授权码安全机制
- 🚀 发送速度快
- 📱 支持多种客户端

## 注意事项

1. **保密授权码**: 授权码相当于密码，请妥善保管
2. **定期更新**: 建议定期更换授权码
3. **发送限制**: 126邮箱可能有每日发送数量限制
4. **垃圾邮件**: 初次使用可能被识别为垃圾邮件，建议先发送测试邮件

配置完成后，您的排班表系统就可以通过126邮箱发送通知了！
