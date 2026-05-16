# -*- coding: utf-8 -*-
"""最小化Kivy测试 - 看看窗口能不能显示"""
import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

from kivy.app import App
from kivy.uix.label import Label
from kivy.config import Config

Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '300')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'window_state', 'visible')
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'left', '200')
Config.set('graphics', 'top', '100')

class TestApp(App):
    def build(self):
        return Label(text='如果能看到这个文字，说明Kivy正常工作！')

TestApp().run()
