# -*- coding: utf-8 -*-
"""测试所有屏幕 - 带字体"""
import os, sys
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'window_state', 'visible')
Config.set('graphics', 'borderless', '0')
Config.set('graphics', 'fullscreen', '0')
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'left', '200')
Config.set('graphics', 'top', '100')
Config.set('kivy', 'exit_on_escape', '0')

import config, database
database.init_db()

# 读取已保存的主题偏好
try:
    _theme_pref = os.path.join(config.Database.STORAGE_ROOT, '.theme_pref.json')
    if os.path.exists(_theme_pref):
        with open(_theme_pref, 'r', encoding='utf-8') as f:
            _pref = __import__('json').load(f)
            if _pref.get('theme') in ('light', 'dark'):
                config.set_theme(_pref['theme'])
                # 同步新主题系统
                from config_theme import set_theme as ct_set
                ct_set(_pref['theme'])
except Exception:
    pass

from kivy.core.text import LabelBase
for fp in ['C:/Windows/Fonts/msyh.ttc', 'C:/Windows/Fonts/simsun.ttc']:
    if os.path.exists(fp):
        try:
            LabelBase.register(name='zh_font', fn_regular=fp)
            break
        except:
            pass

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.lang import Builder

# 全局字体设置
Builder.load_string('''
<Label>:
    font_name: 'zh_font'
<Button>:
    font_name: 'zh_font'
<TextInput>:
    font_name: 'zh_font'
''')

class TestApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = '机械施工记账'
        self.current_customer_id = None
        self.current_customer_name = ''
        self.editing_record_id = None
        self.print_mode = 'all'
        self.print_selected_ids = set()

    def build(self):
        sm = ScreenManager(transition=SlideTransition())
        
        # 设置窗口背景色
        from kivy.core.window import Window
        from config_theme import get_theme as ct_get
        Window.clearcolor = ct_get().BG
        
        from screens.login_screen import LoginScreen
        from screens.customer_screen import CustomerListScreen
        from screens.record_list_screen import RecordListScreen
        from screens.record_form_screen import RecordFormScreen
        from screens.statistics_screen import StatisticsScreen
        from screens.print_preview_screen import PrintPreviewScreen
        from screens.settings_screen import SettingsScreen

        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(CustomerListScreen(name='customer_list'))
        sm.add_widget(RecordListScreen(name='record_list'))
        sm.add_widget(RecordFormScreen(name='record_form'))
        sm.add_widget(StatisticsScreen(name='statistics'))
        sm.add_widget(PrintPreviewScreen(name='print_preview'))
        sm.add_widget(SettingsScreen(name='settings'))
        
        for s in sm.screens:
            s.app_ref = self
        
        # 键盘事件
        from kivy.core.window import Window
        Window.bind(on_keyboard=self._on_keyboard)
        
        sm.current = 'login'
        return sm

    def _on_keyboard(self, window, key, scancode, codepoint, modifier):
        sm = self.root
        if key == 27:
            if sm.current in ('login', 'customer_list'):
                return False
            back_map = {
                'record_list': 'customer_list', 'record_form': 'record_list',
                'statistics': 'record_list', 'print_preview': 'record_list',
                'settings': 'customer_list',
            }
            if sm.current in back_map:
                sm.current = back_map[sm.current]
                return True
        return False

    def rebuild_ui(self):
        """主题切换时安全重建所有UI"""
        import config
        print(f'[REBUILD] rebuild_ui called, current_theme={config._current_theme}')
        sm = ScreenManager(transition=SlideTransition())
        from screens.login_screen import LoginScreen
        from screens.customer_screen import CustomerListScreen
        from screens.record_list_screen import RecordListScreen
        from screens.record_form_screen import RecordFormScreen
        from screens.statistics_screen import StatisticsScreen
        from screens.print_preview_screen import PrintPreviewScreen
        from screens.settings_screen import SettingsScreen

        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(CustomerListScreen(name='customer_list'))
        sm.add_widget(RecordListScreen(name='record_list'))
        sm.add_widget(RecordFormScreen(name='record_form'))
        sm.add_widget(StatisticsScreen(name='statistics'))
        sm.add_widget(PrintPreviewScreen(name='print_preview'))
        sm.add_widget(SettingsScreen(name='settings'))
        for s in sm.screens:
            s.app_ref = self
        from kivy.core.window import Window
        Window.bind(on_keyboard=self._on_keyboard)
        print(f'[REBUILD] before root swap, theme={config._current_theme}')
        sm.current = 'customer_list'
        self.root = sm
        print(f'[REBUILD] root swapped, theme={config._current_theme}')

if __name__ == '__main__':
    TestApp().run()
