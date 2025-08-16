# 微信登录系统配置说明

## 环境变量配置

创建 `.env` 文件在项目根目录，包含以下配置：

```bash
# 微信公众号配置
WECHAT_APP_ID=your_app_id_here
WECHAT_APP_SECRET=your_app_secret_here

# 服务器安全配置
WECHAT_TOKEN=your_custom_token_here
WECHAT_ENCODING_AES_KEY=your_encoding_aes_key_here
WECHAT_ENCRYPT_MODE=plain

# 登录配置
WECHAT_LOGIN_KEYWORD=登录
WECHAT_SESSION_TIMEOUT=3600

# Flask配置
FLASK_SECRET_KEY=your_secret_key_here
```

## Token配置详解

### 1. Token的作用
Token是微信公众号服务器配置中的安全验证参数，用于：
- 验证微信服务器发送的请求是否合法
- 防止恶意请求攻击你的服务器
- 确保消息来源的可靠性

### 2. Token设置要求
```
WECHAT_TOKEN=your_custom_token_here
```
- **长度限制**: 3-32个字符
- **字符要求**: 只能包含字母、数字、下划线
- **建议格式**: 有意义的字符串，便于记忆和管理

### 3. 推荐Token示例
```bash
# 简单格式
WECHAT_TOKEN=mytoken123

# 带项目标识
WECHAT_TOKEN=misszhang_auth_2025

# 带时间戳
WECHAT_TOKEN=wechat_login_202501

# 随机字符串
WECHAT_TOKEN=aB3x9Kp2mN8qR5vL7
```

### 4. Token安全建议
- 使用强随机字符串
- 避免使用常见词汇
- 定期更换Token
- 不要将Token提交到代码仓库

## 微信公众号后台配置

### 1. 服务器配置
- 登录微信公众平台 (https://mp.weixin.qq.com/)
- 进入"设置与开发" → "基本配置"
- 配置服务器地址：
  - **URL**: `https://yourdomain.com/wechat/message`
  - **Token**: 与 `.env` 文件中的 `WECHAT_TOKEN` 保持一致
  - **EncodingAESKey**: 自动生成或手动设置
  - **消息加解密方式**: 建议选择"明文模式"（开发阶段）

### 2. 配置步骤详解
1. **填写服务器地址**
   ```
   https://yourdomain.com/wechat/message
   ```

2. **填写Token**
   ```
   必须与 .env 文件中的 WECHAT_TOKEN 完全一致
   ```

3. **选择消息加解密方式**
   - **明文模式**: 消息不加密，开发测试推荐
   - **兼容模式**: 支持明文和加密消息
   - **安全模式**: 所有消息都加密

4. **点击"提交"**
   - 微信会自动验证服务器地址
   - 验证通过后配置生效

## 域名配置要求

### 必须条件
- 域名必须已备案（中国大陆）
- 必须使用HTTPS协议
- 端口必须是80或443

### 推荐配置
- 使用CDN加速
- 配置SSL证书
- 设置域名解析

## 测试配置

### 1. 本地测试
```bash
# 运行测试脚本
python test_wechat_simple.py

# 启动应用
python app/main.py
```

### 2. 生产环境测试
1. 配置真实域名
2. 设置SSL证书
3. 配置微信公众号回调
4. 测试登录流程

## 常见配置问题

### 1. 配置未生效
- 检查 `.env` 文件是否在正确位置
- 确认环境变量名称正确
- 重启应用使配置生效

### 2. 域名验证失败
- 检查域名是否已备案
- 确认SSL证书有效
- 验证域名解析正确

### 3. 微信API调用失败
- 检查APP_ID和APP_SECRET
- 确认公众号已认证
- 验证服务器配置正确

### 4. Token验证失败
- 确认Token在微信公众号后台和 `.env` 文件中完全一致
- 检查Token长度和字符是否符合要求
- 验证消息加解密方式设置

## 安全配置建议

### 1. 密钥管理
- 使用强随机密钥
- 定期更换密钥
- 避免密钥泄露

### 2. 访问控制
- 限制API访问频率
- 监控异常登录
- 记录操作日志

### 3. 数据保护
- 加密敏感数据
- 定期备份数据
- 设置访问权限

## 性能优化配置

### 1. 缓存配置
- 启用access_token缓存
- 配置会话存储
- 优化数据库查询

### 2. 并发配置
- 设置连接池
- 配置工作进程
- 优化资源使用

## 监控和日志

### 1. 日志配置
- 记录API调用
- 记录用户操作
- 记录错误信息

### 2. 监控指标
- 登录成功率
- API响应时间
- 系统资源使用

## 故障排除

### 1. 检查清单
- [ ] 环境变量配置正确
- [ ] 微信公众号配置完成
- [ ] Token配置一致
- [ ] 域名解析正常
- [ ] SSL证书有效
- [ ] 服务器可访问

### 2. 调试方法
- 查看应用日志
- 检查微信API返回
- 验证网络连接
- 测试配置参数

### 3. Token相关调试
```bash
# 检查环境变量
echo $WECHAT_TOKEN

# 检查应用配置
python -c "from app.wechat_config import WeChatConfig; print(WeChatConfig().token)"

# 验证Token一致性
# 微信公众号后台的Token必须与 .env 文件中的完全一致
```

## 配置验证脚本

运行以下命令验证配置：
```bash
python test_wechat_simple.py
```

成功输出应该包含：
```
✅ 配置测试 通过
✅ 会话管理测试 通过
✅ 服务基础功能测试 通过
```

---

*配置完成后，请运行测试脚本验证系统是否正常工作。*
