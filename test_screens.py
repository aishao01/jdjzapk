# -*- coding: utf-8 -*-
"""逐个测试屏幕"""
import os, sys
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'window_state', 'visible')
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'left', '200')
Config.set('graphics', 'top', '100')
Config.set('kivy', 'exit_on_escape', '0')

# 初始化
import config, database
database.init_db()

from kivy.core.text import LabelBase
for fp in ['C:/Windows/Fonts/msyh.ttc', 'C:/Windows/Fonts/simsun.ttc']:
    if os.path.exists(fp):
        try:
            LabelBase.register(name='zh_font', fn_regular=fp)
            break
        except:
            pass

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.label import Label

# 逐个测试import
screens_to_test = [
    ('登录', 'screens.login_screen', 'LoginScreen'),
    ('客户', 'screens.customer_screen', 'CustomerListScreen'),
    ('记录列表', 'screens.record_list_screen', 'RecordListScreen'),
    ('记录表单', 'screens.record_form_screen', 'RecordFormScreen'),
    ('统计', 'screens.statistics_screen', 'StatisticsScreen'),
    ('打印预览', 'screens.print_preview_screen', 'PrintPreviewScreen'),
    ('设置', 'screens.settings_screen', 'SettingsScreen'),
]

errors = []
for name, module_path, cls_name in screens_to_test:
    try:
        import importlib
        mod = importlib.import_module(module_path)
        cls = getattr(mod, cls_name)
        print(f'✅ {name}: {cls_name} 导入成功')
    except Exception as e:
        import traceback
        err = f'❌ {name}: {e}\n{traceback.format_exc()}'
        print(err)
        errors.append(err)

if errors:
    with open('screen_errors.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(errors))
    print(f'\n{len(errors)}个错误，已写入screen_errors.txt')
else:
    print('\n所有屏幕导入成功！')

input('按回车退出...')
