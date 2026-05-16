# -*- coding: utf-8 -*-
"""简化启动器 - 跳过复杂UI，只显示一个按钮"""
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

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

class TestApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        layout.add_widget(Label(text='⛏ 机械施工记账 v2.0', font_size=24))
        layout.add_widget(Label(text='简易测试版', font_size=14))
        inp = TextInput(hint_text='输入密码', size_hint_y=None, height=40)
        layout.add_widget(inp)
        btn = Button(text='🔓 解锁', size_hint_y=None, height=50)
        layout.add_widget(btn)
        # 在按钮下方加一个状态文本
        self.status = Label(text='就绪', font_size=12, size_hint_y=None, height=30)
        layout.add_widget(self.status)
        return layout

if __name__ == '__main__':
    TestApp().run()
