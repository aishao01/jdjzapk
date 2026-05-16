# -*- coding: utf-8 -*-
"""简化版登录 - 含首次注册密码"""
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

import config
import database
database.init_db()

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.core.text import LabelBase

# 注册字体
for fp in ['C:/Windows/Fonts/msyh.ttc', 'C:/Windows/Fonts/simsun.ttc']:
    if os.path.exists(fp):
        try:
            LabelBase.register(name='zh_font', fn_regular=fp)
            break
        except:
            pass

class SimpleLogin(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._register_mode = False  # 是否在注册模式
    
    def build(self):
        root = BoxLayout(orientation='vertical', padding=40)
        
        with root.canvas.before:
            Color(0.15, 0.15, 0.2, 1)
            self.rect = Rectangle(size=root.size, pos=root.pos)
        root.bind(size=lambda w, s: setattr(self.rect, 'size', s))
        root.bind(pos=lambda w, p: setattr(self.rect, 'pos', p))
        
        root.add_widget(Widget(size_hint_y=0.25))
        
        # 标题
        title = Label(text='⛏ 机械施工记账', font_size=24, color=(1,1,1,1),
                      size_hint_y=None, height=40, bold=True, font_name='zh_font')
        root.add_widget(title)
        
        # 副标题/提示
        self.subtitle = Label(text='', font_size=13, color=(0.7,0.7,0.7,1),
                              size_hint_y=None, height=22, font_name='zh_font')
        root.add_widget(self.subtitle)
        
        root.add_widget(Widget(size_hint_y=0.08))
        
        # 密码输入
        self.inp = TextInput(hint_text='输入密码', password=True,
                            size_hint_y=None, height=40,
                            background_color=(0.2,0.2,0.25,1),
                            foreground_color=(1,1,1,1),
                            hint_text_color=(0.6,0.6,0.6,1),
                            font_name='zh_font')
        root.add_widget(self.inp)
        
        # 确认密码（注册时显示）
        self.inp2 = TextInput(hint_text='再次输入密码', password=True,
                             size_hint_y=None, height=40,
                             background_color=(0.2,0.2,0.25,1),
                             foreground_color=(1,1,1,1),
                             hint_text_color=(0.6,0.6,0.6,1),
                             font_name='zh_font')
        self.inp2.opacity = 0
        self.inp2.disabled = True
        root.add_widget(self.inp2)
        
        root.add_widget(Widget(size_hint_y=0.05))
        
        # 解锁/注册按钮
        self.btn = Button(text='🔓 解锁', size_hint_y=None, height=44,
                         background_color=(0.2,0.5,0.8,1),
                         color=(1,1,1,1), font_name='zh_font')
        self.btn.bind(on_release=self._on_action)
        root.add_widget(self.btn)
        
        # 状态提示
        self.status = Label(text='', font_size=12, size_hint_y=None, height=20,
                           color=(0.8,0.8,0.8,1), font_name='zh_font')
        root.add_widget(self.status)
        
        root.add_widget(Widget(size_hint_y=0.35))
        
        # 初始化界面
        self._check_state()
        
        return root
    
    def _check_state(self):
        """检查是否需要注册"""
        from config import _has_password
        if not _has_password():
            # 首次使用 - 注册模式
            self._register_mode = True
            self.subtitle.text = '首次使用，请注册密码'
            self.btn.text = '📝 注册'
            self.inp.hint_text = '设置密码'
            self.inp2.opacity = 1
            self.inp2.disabled = False
            self.status.text = ''
        else:
            # 已有密码 - 登录模式
            self._register_mode = False
            self.subtitle.text = '请输入密码解锁'
            self.btn.text = '🔓 解锁'
            self.inp.hint_text = '输入密码'
            self.inp2.opacity = 0
            self.inp2.disabled = True
            self.status.text = ''
    
    def _on_action(self, *args):
        pw = self.inp.text.strip()
        
        if self._register_mode:
            # 注册模式
            if not pw:
                self.status.text = '⚠️ 密码不能为空'
                return
            pw2 = self.inp2.text.strip()
            if pw != pw2:
                self.status.text = '❌ 两次输入的密码不一致'
                return
            from config import _set_password
            _set_password(pw)
            self.status.text = '✅ 密码设置成功！'
            # 切换到登录模式
            self.inp.text = ''
            self.inp2.text = ''
            self._check_state()
        else:
            # 登录模式
            if not pw:
                self.status.text = '⚠️ 请输入密码'
                return
            from config import _get_password
            stored = _get_password()
            if pw == stored:
                self.status.text = '✅ 解锁成功！'
            else:
                self.status.text = '❌ 密码错误'

if __name__ == '__main__':
    SimpleLogin().run()
