# -*- coding: utf-8 -*-
"""
功能测试脚本 - 测试记账应用各个模块
"""
import os
import sys

# 设置环境变量
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("机械施工记账 v2.0 - 功能测试")
print("=" * 50)

# 1. 测试配置模块
print("\n[1/7] 测试配置模块...")
try:
    from config import (
        get_theme, set_theme, toggle_theme, Color, Size, 
        Database, AppInfo, _get_password, _set_password, _has_password, _get_password_path
    )
    print("  [OK] config.py 导入成功")
    
    # 测试主题切换
    set_theme('light')
    theme = get_theme()
    print(f"  [OK] 浅色主题加载成功，背景色：{theme.BG}")
    
    set_theme('dark')
    theme = get_theme()
    print(f"  [OK] 深色主题加载成功，背景色：{theme.BG}")
    
    # 测试密码功能
    has_pwd = _has_password()
    print(f"  [OK] 密码检查：{'已设置' if has_pwd else '未设置'}")
    
except Exception as e:
    print(f"  [FAIL] config.py 测试失败：{e}")

# 2. 测试数据库模块
print("\n[2/7] 测试数据库模块...")
try:
    from database import init_db, get_db, get_connection
    init_db()
    print(f"  [OK] 数据库初始化成功：{Database.DB_PATH}")
    
    # 测试连接
    with get_db() as db:
        cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"  [OK] 数据表：{tables}")
    
except Exception as e:
    print(f"  [FAIL] database.py 测试失败：{e}")

# 3. 测试工具函数
print("\n[3/7] 测试工具函数...")
try:
    from utils import (
        parse_time, time_diff_min, time_diff_hours, 
        calc_total_hours, calc_amount, get_now_str
    )
    
    # 测试时间解析
    mins = parse_time("08:30")
    print(f"  [OK] 时间解析 08:30 = {mins} 分钟")
    
    # 测试时间差
    hours = time_diff_hours("08:00", "12:00")
    print(f"  [OK] 时间差 08:00-12:00 = {hours} 小时")
    
    # 测试金额计算
    amount = calc_amount(8, 1000, "台/班")
    print(f"  [OK] 金额计算 8 小时×1000 元/台班 = {amount} 元")
    
    # 测试日期格式
    now = get_now_str()
    print(f"  [OK] 当前日期：{now}")
    
except Exception as e:
    print(f"  [FAIL] utils.py 测试失败：{e}")

# 4. 测试 UI 组件
print("\n[4/7] 测试 UI 组件...")
try:
    from widgets import (
        Card, TopBar, BtnPrimary, BtnDanger, BtnOutline,
        LabelInput, LabelSpinner, ScrollList, EmptyHint,
        ConfirmPopup, BottomToolbar, Divider
    )
    print("  [OK] 所有 UI 组件导入成功")
    
    # 测试创建组件
    card = Card()
    print(f"  [OK] Card 组件创建成功")
    
    btn = BtnPrimary(text="测试按钮")
    print(f"  [OK] BtnPrimary 组件创建成功")
    
except Exception as e:
    print(f"  [FAIL] widgets.py 测试失败：{e}")

# 5. 测试屏幕模块
print("\n[5/7] 测试屏幕模块...")
screens_to_test = [
    ("login_screen", "LoginScreen"),
    ("customer_screen", "CustomerListScreen"),
    ("record_list_screen", "RecordListScreen"),
    ("record_form_screen", "RecordFormScreen"),
    ("statistics_screen", "StatisticsScreen"),
    ("print_preview_screen", "PrintPreviewScreen"),
    ("settings_screen", "SettingsScreen"),
]

for module_name, class_name in screens_to_test:
    try:
        module = __import__(f"screens.{module_name}", fromlist=[class_name])
        screen_class = getattr(module, class_name)
        print(f"  [OK] {class_name} 导入成功")
    except Exception as e:
        print(f"  [FAIL] {class_name} 导入失败：{e}")

# 6. 测试数据存储
print("\n[6/7] 测试数据存储...")
try:
    import os
    data_dir = Database.DB_DIR
    os.makedirs(data_dir, exist_ok=True)
    print(f"  [OK] 数据目录：{data_dir}")
    
    # 检查文件
    if os.path.exists(Database.DB_PATH):
        size = os.path.getsize(Database.DB_PATH)
        print(f"  [OK] 数据库文件存在，大小：{size} 字节")
    
    pwd_file = _get_password_path()
    if os.path.exists(pwd_file):
        print(f"  [OK] 密码文件存在")
    
except Exception as e:
    print(f"  [FAIL] 数据存储测试失败：{e}")

# 7. 应用信息
print("\n[7/7] 应用信息...")
try:
    print(f"  应用名称：{AppInfo.NAME}")
    print(f"  版本号：{AppInfo.VERSION}")
    print(f"  备份目录：{AppInfo.get_backup_dir()}")
except Exception as e:
    print(f"  ✗ 应用信息获取失败：{e}")

print("\n" + "=" * 50)
print("[OK] 所有模块测试完成！")
print("=" * 50)
print("\n正在启动应用界面...")

# 启动应用
from main import MechBookkeepingApp
app = MechBookkeepingApp()
app.run()
