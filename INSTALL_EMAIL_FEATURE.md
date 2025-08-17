# 安装邮件通知功能

## 安装步骤

### 1. 安装依赖包

```bash
pip install -r requirements.txt
```

或者单独安装邮件相关的包：

```bash
pip install Flask-Mail==0.10.0
```

### 2. 配置环境变量

复制环境变量模板文件：

```bash
cp env.example .env
```

编辑 `.env` 文件，配置邮件服务参数：

```bash
# 邮件服务配置
SMTP_SERVER=smtp.126.com
SMTP_PORT=587
SMTP_USER=your_email@126.com
SMTP_PASSWORD=your_email_auth_code_here
SENDER_EMAIL=your_email@126.com

# 邮件收件人（多个邮箱用逗号分隔）
EMAIL_RECIPIENTS=admin@hospital.com,manager@hospital.com
```

### 3. 测试邮件服务

启动应用后，访问测试接口：

```bash
curl http://localhost:5000/api/email/test
```

### 4. 功能验证

1. 登录系统
2. 前往内部页面 (`/insider`)
3. 选择周次并上传排班表图片
4. 上传成功后，指定邮箱应该会收到邮件通知

## 功能说明

- **自动触发**: 排班表上传成功后自动发送邮件
- **包含信息**: 
  - 上传的排班表图片（附件）
  - 选择的时间周次信息
  - 上传用户信息（姓名、医院、科室）
  - 上传时间
- **邮件格式**: HTML格式，内容丰富易读
- **多收件人**: 支持同时发送给多个邮箱

## 注意事项

1. 确保网络能访问配置的SMTP服务器
2. 使用Gmail等服务时，建议使用应用密码而不是登录密码
3. 第一次使用建议先测试邮件服务连接
4. 查看应用日志确认邮件发送状态

详细配置说明请参考 `EMAIL_SETUP_GUIDE.md`
