"""
theme_refresh.py — 不重建 ScreenManager 的主题刷新方案

思路：遍历所有 screen 及其子控件，刷新颜色属性。
每个 screen 需要实现 apply_theme() 方法。
"""

from kivy.clock import Clock
from kivy.app import App


def apply_theme_to_all():
    """刷新所有 screen 的主题（不重建）"""
    app = App.get_running_app()
    if not app or not hasattr(app, 'root'):
        return
    sm = app.root
    for s in sm.screens:
        if hasattr(s, 'apply_theme'):
            Clock.schedule_once(lambda dt, scr=s: scr.apply_theme(), 0)


def apply_theme_to_current():
    """刷新当前可见 screen 的主题"""
    app = App.get_running_app()
    if not app or not hasattr(app, 'root'):
        return
    sm = app.root
    current = sm.current_screen
    if current and hasattr(current, 'apply_theme'):
        current.apply_theme()
