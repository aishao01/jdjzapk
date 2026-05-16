import sys
import os

# 强制让Config在import kivy之前加载
os.environ['KIVY_WINDOW'] = 'sdl2'

from kivy.config import Config
Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'borderless', '0')
Config.set('graphics', 'fullscreen', '0')
Config.set('graphics', 'window_state', 'visible')
Config.set('kivy', 'exit_on_escape', '0')
Config.set('kivy', 'window_icon', '')
Config.write()  # 写入配置文件

print("配置已写入，现在运行主程序...")
print("请运行: python main.py")
