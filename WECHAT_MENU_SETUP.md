# 微信公众号自定义菜单配置指南

本指南将帮助您配置并发布微信公众号自定义菜单"放射小张"，点击后跳转到网站 `www.wuyinxinghai.cn`。

## ✅ 功能已完成

以下功能已经实现并可以使用：

1. **后端API**：
   - `POST /wechat/menu/create` - 创建自定义菜单
   - `GET /wechat/menu/get` - 获取当前菜单
   - `POST /wechat/menu/delete` - 删除自定义菜单

2. **网页管理界面**：
   - `/wechat/menu` - 菜单管理页面

3. **测试脚本**：
   - `test_wechat_menu.py` - 完整的功能测试

## 🔧 配置步骤

### 1. 获取微信公众号凭据

您需要从微信公众平台获取以下信息：

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入"开发" > "基本配置"
3. 获取：
   - **AppID** (应用ID)
   - **AppSecret** (应用密钥)

### 2. 设置环境变量

将获取到的凭据设置到环境变量中：

```bash
# 方法1: 临时设置（当前会话有效）
export WECHAT_APP_ID=你的微信AppID
export WECHAT_APP_SECRET=你的微信AppSecret

# 方法2: 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export WECHAT_APP_ID=你的微信AppID' >> ~/.bashrc
echo 'export WECHAT_APP_SECRET=你的微信AppSecret' >> ~/.bashrc
source ~/.bashrc
```

**或者修改 `.env` 文件：**

```bash
# 编辑项目根目录的 .env 文件
cp env.example .env
nano .env

# 修改以下行：
WECHAT_APP_ID=你的微信AppID
WECHAT_APP_SECRET=你的微信AppSecret
```

### 3. 验证配置

运行测试脚本验证配置是否正确：

```bash
cd /Users/renjie/work/misszhang/MissZhang
python test_wechat_menu.py
```

如果配置正确，您会看到类似输出：
```
==================================================
微信公众号自定义菜单测试
==================================================
1. 检查微信配置...
   APP_ID: wx1234567890abcdef
   APP_SECRET: 已配置
   配置完整性: ✅ 完整

2. 测试获取access_token...
   ✅ 成功获取access_token: AT_abc123...
```

## 🚀 使用方法

### 方法1: 使用网页界面（推荐）

1. 启动应用：
   ```bash
   python run.py
   ```

2. 访问菜单管理页面：
   ```
   http://localhost:5000/wechat/menu
   ```

3. 点击"创建/更新菜单"按钮

### 方法2: 使用API接口

```bash
# 创建菜单
curl -X POST http://localhost:5000/wechat/menu/create \
     -H "Content-Type: application/json" \
     -d '{}'

# 获取当前菜单
curl http://localhost:5000/wechat/menu/get

# 删除菜单
curl -X POST http://localhost:5000/wechat/menu/delete \
     -H "Content-Type: application/json" \
     -d '{}'
```

### 方法3: 使用测试脚本

```bash
python test_wechat_menu.py
```

## 📱 菜单配置详情

创建的自定义菜单包含：

- **菜单名称**：放射小张
- **菜单类型**：view（网页跳转）
- **跳转链接**：https://www.wuyinxinghai.cn

菜单结构（JSON格式）：
```json
{
  "button": [
    {
      "type": "view",
      "name": "放射小张",
      "url": "https://www.wuyinxinghai.cn"
    }
  ]
}
```

## ⚠️ 重要注意事项

### 1. 公众号类型要求
- **只有已认证的服务号**才能使用自定义菜单功能
- 测试号和未认证公众号无法使用此功能

### 2. 菜单生效时间
- 菜单创建或删除后，需要**24小时**才能在微信客户端生效
- 在生效前，用户可能看不到菜单或看到旧菜单

### 3. 菜单限制
- 最多支持3个一级菜单
- 每个一级菜单最多5个子菜单
- 菜单名称最长4个汉字
- URL必须以http://或https://开头

## 🔍 故障排除

### 常见错误及解决方案

1. **"access_token获取失败"**
   - 检查AppID和AppSecret是否正确
   - 检查网络连接是否正常

2. **"创建菜单失败，错误码40013"**
   - 公众号类型不支持，需要认证的服务号

3. **"创建菜单失败，错误码40035"**
   - AppSecret不正确

4. **"菜单创建成功但看不到"**
   - 正常情况，需要等待24小时生效

## 📋 文件说明

- `app/wechat_config.py` - 微信配置管理
- `app/wechat_service.py` - 微信API服务
- `app/main.py` - 路由接口（已添加菜单管理路由）
- `app/templates/wechat_menu.html` - 菜单管理网页界面
- `test_wechat_menu.py` - 功能测试脚本
- `WECHAT_MENU_SETUP.md` - 本配置指南

## 🎯 下一步

1. 按照上述步骤完成配置
2. 使用任意方法创建菜单
3. 等待24小时后在微信客户端查看效果
4. 根据需要调整菜单配置

如果有任何问题，请查看控制台日志或联系技术支持。
