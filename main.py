"""
main.py — 机械施工记账 v2.0
主入口：全局异常处理、字体注册、主题管理、ScreenManager
"""

import os
import sys
import json

# Android 16 FORTIFY 绕过（SDL2/Android 16 mutex 兼容性）
os.environ['ANDROID_FORTIFY_IGNORE_DESTROYED_MUTEX'] = '1'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform

from config import get_theme, set_theme, Color, Size, AppInfo, Database, \
    _get_password, _set_password, _has_password
from database import init_db

# ─── 应用主类 ────────────────────────────────────────
class MechBookkeepingApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = AppInfo.NAME
        self.current_customer_id = None
        self.current_customer_name = ''
        self.editing_record_id = None
    
    def _detect_system_theme(self):
        """检测系统主题（深色/浅色）"""
        try:
            import sys
            # Android 检测
            if platform == 'android':
                try:
                    from jnius import autoclass
                    Context = autoclass('android.content.Context')
                    UiModeManager = autoclass('android.app.UiModeManager')
                    Configuration = autoclass('android.content.res.Configuration')
                    
                    # 获取 UiModeManager
                    activity = autoclass('org.kivy.android.PythonActivity').mActivity
                    ui_mode_manager = activity.getSystemService(Context.UI_MODE_SERVICE)
                    
                    # 检查当前模式
                    night_mode = ui_mode_manager.getNightMode()
                    if night_mode == UiModeManager.MODE_NIGHT_YES:
                        return 'dark'
                    elif night_mode == UiModeManager.MODE_NIGHT_NO:
                        return 'light'
                except Exception as e:
                    print(f"Android 主题检测失败：{e}")
            
            # Windows 检测（注册表）
            elif sys.platform == 'win32':
                try:
                    import winreg
                    # 读取 Windows 深色模式设置
                    key = winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
                    )
                    apps_use_dark, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
                    winreg.CloseKey(key)
                    
                    # AppsUseLightTheme = 0 表示使用深色模式
                    return 'dark' if apps_use_dark == 0 else 'light'
                except Exception as e:
                    print(f"Windows 主题检测失败：{e}")
            
            # macOS 检测
            elif sys.platform == 'darwin':
                try:
                    import subprocess
                    result = subprocess.run(
                        ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                        capture_output=True, text=True
                    )
                    if 'Dark' in result.stdout:
                        return 'dark'
                except:
                    pass
            
            # iOS 检测
            elif platform == 'ios':
                try:
                    from pyobjus import autoclass
                    from pyobjus.dylib_manager import load_framework
                    load_framework('/System/Library/Frameworks/UIKit.framework')
                    
                    UIScreen = autoclass('UIScreen')
                    screen = UIScreen.mainScreen()
                    trait_collection = screen.traitCollection
                    if trait_collection.userInterfaceStyle == 1:  # UIUserInterfaceStyleDark
                        return 'dark'
                except Exception as e:
                    print(f"iOS 主题检测失败：{e}")
            
        except Exception as e:
            print(f"系统主题检测异常：{e}")
        
        # 默认返回浅色
        return 'light'
    
    def build_config(self, config):
        # 设置应用图标（Windows）
        import sys
        if sys.platform == 'win32':
            self.icon = r'C:\Users\aisha\Documents\xwechat_files\wxid_etzm803tslad22_3255\temp\RWTemp\2026-05\9e20f478899dc29eb19741386f9343c8\71e37ae7775ec21d1fef253cd6059426.png'
        return super().build_config(config)

    def build(self):
        # 全局异常捕获
        sys.excepthook = self._save_crash

        # 自动检测系统主题（如果设置了自动跟随）
        from config import is_auto_theme, set_theme, _auto_theme
        if is_auto_theme():
            system_theme = self._detect_system_theme()
            set_theme(system_theme)
            # print(f"自动跟随系统主题：{'深色' if system_theme == 'dark' else '浅色'}")

        # 加载主题偏好
        self._load_theme_pref()

        # 中文全局字体
        self._setup_font()

        # 确保数据目录
        os.makedirs(Database.DB_DIR, exist_ok=True)
        init_db()

        # 桌面窗口尺寸
        if platform not in ('android', 'ios'):
            Window.size = (400, 720)

        # 屏幕管理
        sm = self._build_screen_manager()

        # Android 返回键
        if platform == 'android' or sys.platform == 'win32':
            Window.bind(on_keyboard=self._on_keyboard)

        return sm

    def _build_screen_manager(self):
        """构建所有屏幕"""
        sm = ScreenManager(transition=SlideTransition())

        # 导入所有 Screen 类（延迟导入避免循环）
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

        # 给每个页面传入 app 引用
        for s in sm.screens:
            s.app_ref = self

        return sm

    def _setup_font(self):
        """注册中文字体"""
        from kivy.core.text import LabelBase
        from kivy.lang import Builder

        font_registered = False

        if sys.platform == 'win32':
            font_paths = [
                'C:/Windows/Fonts/msyh.ttc',      # 微软雅黑
                'C:/Windows/Fonts/simsun.ttc',     # 宋体
                'C:/Windows/Fonts/simhei.ttf',     # 黑体
                'C:/Windows/Fonts/msyhbd.ttc',     # 微软雅黑粗体
            ]
            for fp in font_paths:
                if os.path.exists(fp):
                    try:
                        LabelBase.register(name='zh_font', fn_regular=fp)
                        font_registered = True
                        break
                    except Exception as e:
                        print(f"字体注册失败 {fp}: {e}")
                        pass
        elif platform == 'android':
            android_fonts = [
                '/system/fonts/NotoSansCJK-Regular.ttc',
                '/system/fonts/DroidSansFallback.ttf',
                '/system/fonts/NotoSansSC-Regular.otf',
                '/system/fonts/NotoSansSC-Regular.ttf',
            ]
            for fp in android_fonts:
                if os.path.exists(fp):
                    try:
                        LabelBase.register(name='zh_font', fn_regular=fp)
                        font_registered = True
                        break
                    except:
                        pass
        else:
            # macOS/Linux
            font_paths = [
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
            ]
            for fp in font_paths:
                if os.path.exists(fp):
                    try:
                        LabelBase.register(name='zh_font', fn_regular=fp)
                        font_registered = True
                        break
                    except:
                        pass

        if font_registered:
            try:
                Builder.load_string('''
<Label>:
    font_name: 'zh_font'
<Button>:
    font_name: 'zh_font'
<TextInput>:
    font_name: 'zh_font'
''')
            except Exception as e:
                print(f"KV加载失败: {e}")
                pass

    def _load_theme_pref(self):
        """从文件加载主题偏好"""
        try:
            pref_path = os.path.join(Database.STORAGE_ROOT, '.theme_pref.json')
            if os.path.exists(pref_path):
                with open(pref_path, 'r') as f:
                    pref = json.load(f)
                    mode = 'dark' if pref.get('dark_mode', True) else 'light'
                    set_theme(mode)
        except:
            set_theme('dark')

    def _save_crash(self, tp, val, tb):
        """保存崩溃日志到 Download"""
        try:
            import traceback
            log_path = '/storage/emulated/0/Download/crash_log.txt'
            with open(log_path, 'w') as f:
                traceback.print_exception(tp, val, tb, file=f)
        except:
            pass

    def _on_keyboard(self, window, key, scancode, codepoint, modifier):
        """拦截返回键"""
        sm = self.root
        if key == 27:  # ESC / Android back
            if sm.current in ('login', 'customer_list'):
                return False
            back_map = {
                'record_list': 'customer_list',
                'record_form': 'record_list',
                'statistics': 'record_list',
                'print_preview': 'record_list',
                'settings': 'customer_list',
            }
            if sm.current in back_map:
                sm.current = back_map[sm.current]
                return True
        return False


if __name__ == '__main__':
    MechBookkeepingApp().run()
