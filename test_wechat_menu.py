#!/usr/bin/env python3
"""
微信公众号自定义菜单测试脚本

使用方法：
1. 确保已配置环境变量：WECHAT_APP_ID 和 WECHAT_APP_SECRET
2. 运行：python test_wechat_menu.py

功能：
- 测试获取 access_token
- 测试创建自定义菜单（放射小张按钮，跳转到 www.wuyinxinghai.cn）
- 测试获取当前菜单
- 测试删除菜单（可选）
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("警告: 未安装python-dotenv，请确保已设置环境变量")

from app.wechat_service import WeChatService
from app.wechat_config import WeChatConfig

def test_wechat_menu():
    """测试微信菜单功能"""
    print("=" * 50)
    print("微信公众号自定义菜单测试")
    print("=" * 50)
    
    # 初始化服务
    config = WeChatConfig()
    service = WeChatService()
    
    # 检查配置
    print(f"1. 检查微信配置...")
    print(f"   APP_ID: {config.app_id}")
    print(f"   APP_SECRET: {'已配置' if config.app_secret else '未配置'}")
    print(f"   配置完整性: {'✅ 完整' if config.is_configured else '❌ 不完整'}")
    print()
    
    if not config.is_configured:
        print("❌ 微信配置不完整，请设置环境变量：")
        print("   export WECHAT_APP_ID=your_app_id")
        print("   export WECHAT_APP_SECRET=your_app_secret")
        return False
    
    # 测试获取access_token
    print("2. 测试获取access_token...")
    access_token = service.get_access_token()
    if access_token:
        print(f"   ✅ 成功获取access_token: {access_token[:10]}...")
    else:
        print("   ❌ 获取access_token失败")
        return False
    print()
    
    # 测试获取当前菜单（如果存在）
    print("3. 获取当前菜单...")
    current_menu = service.get_custom_menu()
    if current_menu:
        print("   ✅ 当前存在自定义菜单:")
        print(f"   {json.dumps(current_menu, ensure_ascii=False, indent=2)}")
    else:
        print("   ℹ️  当前没有自定义菜单或获取失败")
    print()
    
    # 测试创建菜单
    print("4. 创建自定义菜单（放射小张）...")
    success = service.create_custom_menu()
    if success:
        print("   ✅ 菜单创建成功！")
        print("   📱 菜单内容：")
        print("      - 名称：放射小张")
        print("      - 类型：view（网页跳转）")
        print("      - 链接：https://www.wuyinxinghai.cn")
        print("   ⏰ 菜单将在24小时内生效")
    else:
        print("   ❌ 菜单创建失败")
        return False
    print()
    
    # 再次获取菜单确认
    print("5. 确认菜单创建结果...")
    updated_menu = service.get_custom_menu()
    if updated_menu:
        print("   ✅ 菜单已更新:")
        print(f"   {json.dumps(updated_menu, ensure_ascii=False, indent=2)}")
    else:
        print("   ℹ️  菜单可能还在处理中")
    print()
    
    # 询问是否删除菜单
    print("6. 是否删除刚创建的菜单？")
    user_input = input("   输入 'yes' 删除菜单，其他任意键跳过: ")
    if user_input.lower() == 'yes':
        print("   正在删除菜单...")
        delete_success = service.delete_custom_menu()
        if delete_success:
            print("   ✅ 菜单删除成功！将在24小时内生效")
        else:
            print("   ❌ 菜单删除失败")
    else:
        print("   ⏭️  跳过删除操作")
    print()
    
    print("=" * 50)
    print("测试完成！")
    print()
    print("🔍 注意事项：")
    print("1. 菜单创建/删除后需要24小时才能在微信客户端生效")
    print("2. 只有已认证的服务号才能使用自定义菜单功能")
    print("3. 如果是测试号，菜单功能可能不可用")
    print("4. 可以通过网页管理界面继续管理菜单: /wechat/menu")
    print("=" * 50)
    
    return True

def main():
    """主函数"""
    try:
        success = test_wechat_menu()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
