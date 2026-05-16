# -*- coding: utf-8 -*-
"""调试启动器 - 捕获所有异常"""
import os, sys, traceback

os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main import MechBookkeepingApp
    app = MechBookkeepingApp()
    app.run()
except SystemExit as e:
    msg = f'SystemExit 被捕获: {e}'
    print(msg)
    with open('debug_exit.txt', 'w', encoding='utf-8') as f:
        f.write(msg)
except Exception as e:
    msg = f'异常: {type(e).__name__}: {e}\n'
    msg += ''.join(traceback.format_tb(e.__traceback__))
    print(msg)
    with open('debug_exit.txt', 'w', encoding='utf-8') as f:
        f.write(msg)
finally:
    input('按回车退出...')
