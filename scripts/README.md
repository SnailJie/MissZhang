# 📜 Scripts 脚本使用说明

本目录包含了 MissZhang 排班管理系统的各种管理脚本。

## 🚀 核心脚本

### 1. `start.sh` - 启动应用
启动生产环境的 Flask 应用。

**用法：**
```bash
bash scripts/start.sh
```

**功能：**
- 创建并激活 Python 虚拟环境
- 安装/更新依赖包
- 检查环境配置
- 启动 Gunicorn 服务器
- 健康检查

**注意事项：**
- 首次运行会自动创建虚拟环境
- 需要先配置 `.env` 文件
- 默认使用 80 端口

### 2. `stop.sh` - 停止应用
停止正在运行的 Flask 应用。

**用法：**
```bash
bash scripts/stop.sh
```

**功能：**
- 优雅停止 Gunicorn 进程
- 清理 PID 文件
- 强制终止（如果优雅停止失败）

### 3. `deploy.sh` - 部署应用
将应用部署到生产服务器。

**用法：**
```bash
sudo bash scripts/deploy.sh
```

**功能：**
- 复制项目文件到 `/opt/missZhang`
- 设置文件权限
- 启动应用
- 配置防火墙（可选）
- 健康检查

**注意事项：**
- 需要 root 权限（80端口）
- 需要先配置 `.env` 文件
- 会自动重启应用

## 🔧 配置脚本

### 4. `setup_env.sh` - 环境配置
交互式配置环境变量。

**用法：**
```bash
bash scripts/setup_env.sh
```

**功能：**
- 创建 `.env` 配置文件
- 提示配置微信参数
- 可选择编辑器直接编辑
- 配置验证

**配置参数：**
- `WECHAT_APP_ID`: 微信公众平台 AppID
- `WECHAT_APP_SECRET`: 微信公众平台 AppSecret
- `WECHAT_REDIRECT_URI`: 微信授权回调地址
- `FLASK_SECRET_KEY`: Flask 应用密钥
- `PRODUCTION_HOST`: 生产环境主机地址
- `PRODUCTION_PORT`: 生产环境端口

## 📊 监控脚本

### 5. `status.sh` - 系统状态检查
检查系统运行状态和配置。

**用法：**
```bash
bash scripts/status.sh
```

**功能：**
- 应用运行状态检查
- 环境配置验证
- 数据库状态检查
- 日志文件状态
- 依赖包状态
- 端口占用检查
- 健康检查

## 🛠️ 脚本依赖

### 系统要求
- Bash 4.0+
- Python 3.7+
- curl（用于健康检查）
- netstat（用于端口检查，可选）

### 文件结构
```
scripts/
├── start.sh          # 启动脚本
├── stop.sh           # 停止脚本
├── deploy.sh         # 部署脚本
├── setup_env.sh      # 环境配置脚本
├── status.sh         # 状态检查脚本
└── README.md         # 本说明文档
```

## 🔄 工作流程

### 首次部署
1. 运行 `setup_env.sh` 配置环境变量
2. 运行 `deploy.sh` 部署到服务器
3. 使用 `status.sh` 检查系统状态

### 日常维护
1. 使用 `status.sh` 检查系统状态
2. 使用 `start.sh` 启动应用
3. 使用 `stop.sh` 停止应用

### 更新部署
1. 更新代码
2. 运行 `deploy.sh` 重新部署
3. 使用 `status.sh` 验证更新

## ⚠️ 注意事项

### 权限要求
- `deploy.sh` 需要 root 权限（80端口）
- 其他脚本使用普通用户权限即可

### 环境要求
- 生产环境需要配置 `.env` 文件
- 开发环境可以使用默认配置
- 确保网络访问权限

### 安全考虑
- `.env` 文件包含敏感信息，不要提交到版本控制
- 生产环境使用强密钥
- 定期检查日志文件

## 🐛 故障排除

### 常见问题

**Q: 脚本执行权限错误？**
A: 确保脚本有执行权限：
```bash
chmod +x scripts/*.sh
```

**Q: 端口被占用？**
A: 检查端口占用情况：
```bash
netstat -tlnp | grep :80
```

**Q: 环境变量未生效？**
A: 检查 `.env` 文件格式和内容：
```bash
bash scripts/status.sh
```

**Q: 虚拟环境问题？**
A: 删除并重新创建虚拟环境：
```bash
rm -rf .venv
bash scripts/start.sh
```

### 日志查看
- 应用日志：`logs/gunicorn.error.log`
- 访问日志：`logs/gunicorn.access.log`
- 系统日志：`/var/log/syslog` 或 `/var/log/messages`

## 📚 相关文档

- `../README.md` - 项目总体说明
- `../QUICKSTART.md` - 快速启动指南
- `../IMPLEMENTATION_STATUS.md` - 实现状态总结
- `../env.example` - 环境变量配置示例

---

**维护者**: MissZhang 开发团队  
**更新时间**: 2025年1月  
**版本**: v1.0.0
