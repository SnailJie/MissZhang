# Token配置快速参考

## 🚀 快速开始

### 1. 设置环境变量
在项目根目录创建 `.env` 文件：
```bash
WECHAT_TOKEN=your_custom_token_here
```

### 2. 配置微信公众号后台
- 登录：https://mp.weixin.qq.com/
- 路径：设置与开发 → 基本配置 → 服务器配置
- Token：填入与 `.env` 文件完全相同的值

## 📝 Token格式要求

| 项目 | 要求 | 示例 |
|------|------|------|
| 长度 | 3-32个字符 | ✅ `abc123` |
| 字符 | 字母、数字、下划线 | ✅ `my_token_2025` |
| 格式 | 不能以数字开头 | ❌ `123token` |

## 🔐 推荐Token示例

### 简单格式
```bash
WECHAT_TOKEN=mytoken123
WECHAT_TOKEN=auth_key_2025
WECHAT_TOKEN=wechat_login
```

### 项目标识格式
```bash
WECHAT_TOKEN=misszhang_auth_2025
WECHAT_TOKEN=hospital_schedule_token
WECHAT_TOKEN=medical_app_key
```

### 随机安全格式
```bash
WECHAT_TOKEN=aB3x9Kp2mN8qR5vL7
WECHAT_TOKEN=Kj8mN2pQ9xL5vR3wE7
WECHAT_TOKEN=Ht6nP4qW8yM7vS2xF9
```

## ⚠️ 重要注意事项

### 1. 一致性要求
- `.env` 文件中的Token
- 微信公众号后台的Token
- 必须**完全一致**，包括大小写

### 2. 安全建议
- 不要使用常见词汇
- 避免使用个人信息
- 定期更换Token
- 不要提交到代码仓库

### 3. 常见错误
```bash
# ❌ 错误：Token不一致
.env: WECHAT_TOKEN=mytoken123
微信后台: mytoken456

# ❌ 错误：Token格式不正确
WECHAT_TOKEN=123token
WECHAT_TOKEN=my-token
WECHAT_TOKEN=my token

# ✅ 正确：Token一致且格式正确
.env: WECHAT_TOKEN=mytoken123
微信后台: mytoken123
```

## 🔍 配置验证

### 1. 检查环境变量
```bash
# 查看Token是否设置
echo $WECHAT_TOKEN

# 检查应用配置
python -c "from app.wechat_config import WeChatConfig; print(WeChatConfig().token)"
```

### 2. 运行测试
```bash
python test_wechat_simple.py
```

### 3. 验证输出
成功配置应该看到：
```
✅ 配置测试 通过
✅ 会话管理测试 通过
✅ 服务基础功能测试 通过
```

## 🛠️ 故障排除

### Token验证失败
1. 检查Token是否一致
2. 确认Token格式正确
3. 重启应用
4. 检查微信后台配置

### 配置不生效
1. 确认 `.env` 文件位置正确
2. 检查环境变量名称
3. 重启应用
4. 查看应用日志

## 📚 相关文档

- [完整配置说明](CONFIGURATION.md)
- [项目总结](PROJECT_SUMMARY.md)
- [技术说明](WECHAT_LOGIN_README.md)

---

*配置完成后，请运行测试脚本验证系统是否正常工作。*
