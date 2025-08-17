# 邮件服务配置指南

## 功能说明

系统现已集成邮件通知功能，当用户上传排班表成功后，会自动发送邮件通知到指定邮箱，包含以下信息：
- 上传的排班表图片（作为附件）
- 选择的时间周次信息
- 上传用户的基本信息（姓名、医院、科室）
- 上传时间

## 邮件服务配置

### 1. 环境变量配置

在 `.env` 文件中添加以下配置（参考 `env.example`）：

```bash
# 邮件服务配置
SMTP_SERVER=smtp.126.com            # SMTP服务器地址
SMTP_PORT=587                       # SMTP端口
SMTP_USER=your_email@126.com        # 发送邮箱账号
SMTP_PASSWORD=your_auth_code        # 发送邮箱授权码
SENDER_EMAIL=your_email@126.com     # 发件人邮箱（通常与SMTP_USER相同）

# 收件人邮箱（支持多个，用逗号分隔）
EMAIL_RECIPIENTS=admin@hospital.com,manager@hospital.com
```

### 2. 不同邮件服务商配置

#### Gmail
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

**注意**: Gmail 需要使用应用密码，不是普通登录密码。
1. 前往 [Google账户设置](https://myaccount.google.com/)
2. 安全性 → 两步验证（需先启用）
3. 应用密码 → 生成新的应用密码

#### 网易126邮箱 (推荐)
```bash
SMTP_SERVER=smtp.126.com
SMTP_PORT=587
SMTP_USER=your_email@126.com
SMTP_PASSWORD=your_auth_code
```

**注意**: 126邮箱需要使用授权码，不是普通登录密码。
1. 登录 [网易126邮箱](https://mail.126.com/)
2. 设置 → POP3/SMTP/IMAP → 开启SMTP服务
3. 获取授权码（按提示完成身份验证）
4. 使用授权码作为SMTP_PASSWORD

#### 163邮箱
```bash
SMTP_SERVER=smtp.163.com
SMTP_PORT=587
SMTP_USER=your_email@163.com
SMTP_PASSWORD=your_auth_code
```

#### QQ邮箱
```bash
SMTP_SERVER=smtp.qq.com
SMTP_PORT=587
SMTP_USER=your_email@qq.com
SMTP_PASSWORD=your_auth_code
```

#### 企业邮箱
```bash
SMTP_SERVER=smtp.exmail.qq.com      # 腾讯企业邮箱
SMTP_PORT=587
SMTP_USER=your_email@company.com
SMTP_PASSWORD=your_password
```

### 3. 配置验证

访问以下接口测试邮件服务配置：
```
GET /api/email/test
```

返回示例：
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

## 邮件内容模板

邮件将包含以下内容：

**主题**: 排班表上传通知 - [周次信息]

**正文内容**:
- 排班信息（周次、文件名、上传时间）
- 上传用户信息（姓名、医院、科室）
- 排班表图片作为附件

## 故障排除

### 1. 邮件发送失败
- 检查环境变量配置是否正确
- 确认SMTP服务器和端口
- 验证邮箱账号和密码
- 检查网络连接

### 2. Gmail 认证失败
- 确保启用了两步验证
- 使用应用密码而不是登录密码
- 检查账户安全设置

### 3. 收不到邮件
- 检查垃圾邮件文件夹
- 确认收件人邮箱地址正确
- 检查邮件服务商的发送限制

## 安全注意事项

1. **不要在代码中硬编码邮箱密码**
2. **使用应用密码而不是主密码**
3. **定期更换邮箱密码**
4. **限制收件人列表，避免信息泄露**

## 测试步骤

1. 配置环境变量
2. 重启应用
3. 访问 `/api/email/test` 测试连接
4. 上传一个排班表文件进行实际测试

## 功能扩展

未来可以考虑添加：
- 邮件模板自定义
- 发送状态记录
- 邮件发送重试机制
- 邮件内容国际化
