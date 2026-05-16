"""
theme_utils.py — 主题刷新工具

不重建 ScreenManager，直接遍历 widget 树更新颜色。
每个 Screen 需要实现 _apply_theme() 方法来刷新其子控件颜色。
"""

from kivy.clock import Clock
from kivy.app import App
from config import get_theme


def refresh_current_screen():
    """刷新当前可见 Screen 的主题颜色"""
    app = App.get_running_app()
    if not app or not hasattr(app, 'root'):
        return
    sm = app.root
    current = sm.current_screen
    if current and hasattr(current, 'apply_theme'):
        current.apply_theme()


def refresh_all_screens():
    """刷新所有已添加 Screen 的主题颜色"""
    app = App.get_running_app()
    if not app or not hasattr(app, 'root'):
        return
    sm = app.root
    for s in sm.screens:
        if hasattr(s, 'apply_theme'):
            Clock.schedule_once(lambda dt, scr=s: scr.apply_theme(), 0)
