# -*- coding: utf-8 -*-
"""逐步启动测试"""
import os, sys, traceback

os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '720')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'window_state', 'visible')
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'left', '200')
Config.set('graphics', 'top', '100')
Config.set('kivy', 'exit_on_escape', '0')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

try:
    # 第一步：只测试config和database
    print('Step 1: 导入config...')
    import config
    print('Step 1 OK')
    
    print('Step 2: 导入database...')
    import database
    database.init_db()
    print('Step 2 OK')
    
    print('Step 3: 导入所有screens...')
    from screens.login_screen import LoginScreen
    from screens.customer_screen import CustomerListScreen
    from screens.record_list_screen import RecordListScreen
    from screens.record_form_screen import RecordFormScreen
    from screens.statistics_screen import StatisticsScreen
    from screens.print_preview_screen import PrintPreviewScreen
    from screens.settings_screen import SettingsScreen
    print('Step 3 OK')
    
    print('Step 4: 导入main...')
    import main
    print('Step 4 OK')
    
    print('所有步骤完成！现在是最后测试...')
    
except Exception as e:
    error_msg = f'错误: {type(e).__name__}: {e}\n'
    error_msg += ''.join(traceback.format_tb(e.__traceback__))
    print(error_msg)
    with open('step_error.txt', 'w', encoding='utf-8') as f:
        f.write(error_msg)
    input('按回车退出...')
