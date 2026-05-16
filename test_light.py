# -*- coding: utf-8 -*-
"""调试版启动器 - 跳过字体注册和复杂UI"""
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

# 先初始化数据库
import config
import database
database.init_db()

# 直接用简单的登录界面
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

class SimpleLogin(App):
    def build(self):
        # 注册中文字体
        from kivy.core.text import LabelBase
        for fp in ['C:/Windows/Fonts/msyh.ttc', 'C:/Windows/Fonts/simsun.ttc']:
            if os.path.exists(fp):
                try:
                    LabelBase.register(name='zh_font', fn_regular=fp)
                    break
                except:
                    pass
        
        root = BoxLayout(orientation='vertical', padding=40)
        
        # 用简单纯色背景代替渐变
        with root.canvas.before:
            Color(0.15, 0.15, 0.2, 1)
            self.rect = Rectangle(size=root.size, pos=root.pos)
        root.bind(size=lambda w, s: setattr(self.rect, 'size', s))
        root.bind(pos=lambda w, p: setattr(self.rect, 'pos', p))
        
        # 占位
        root.add_widget(Widget(size_hint_y=0.3))
        
        # 标题
        title = Label(text='机械施工记账', font_size=24, color=(1,1,1,1), 
                      size_hint_y=None, height=40, bold=True,
                      font_name='zh_font')
        root.add_widget(title)
        
        # 密码输入
        root.add_widget(Widget(size_hint_y=0.1))
        inp = TextInput(hint_text='输入密码', password=True,
                       size_hint_y=None, height=40,
                       background_color=(0.2,0.2,0.25,1),
                       foreground_color=(1,1,1,1),
                       hint_text_color=(0.6,0.6,0.6,1),
                       font_name='zh_font')
        root.add_widget(inp)
        
        # 解锁按钮
        btn = Button(text='解锁', size_hint_y=None, height=44,
                    background_color=(0.2,0.5,0.8,1),
                    color=(1,1,1,1),
                    font_name='zh_font')
        btn.bind(on_release=lambda x: self._unlock(inp.text))
        root.add_widget(btn)
        
        # 状态
        self.status = Label(text='', font_size=12, size_hint_y=None, height=20,
                           color=(0.8,0.8,0.8,1),
                           font_name='zh_font')
        root.add_widget(self.status)
        
        root.add_widget(Widget(size_hint_y=0.4))
        return root
    
    def _unlock(self, pw):
        from config import _has_password, _set_password, _get_password
        if not _has_password():
            _set_password(pw)
            self.status.text = '✅ 密码已设置'
        elif pw == _get_password():
            self.status.text = '✅ 解锁成功！'
        else:
            self.status.text = '❌ 密码错误'

if __name__ == '__main__':
    SimpleLogin().run()
