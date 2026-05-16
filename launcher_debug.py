# -*- coding: utf-8 -*-
"""机械施工记账 v2.0 - Windows调试启动器"""
import os
import sys
import traceback

# 错误日志
error_log = open('error_log.txt', 'w', encoding='utf-8')
sys.stderr = error_log

try:
    # 必须放在import kivy之前
    os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
    
    from kivy.config import Config
    Config.set('graphics', 'width', '480')
    Config.set('graphics', 'height', '800')
    Config.set('graphics', 'resizable', '0')
    Config.set('graphics', 'window_state', 'visible')
    Config.set('graphics', 'borderless', '0')
    Config.set('graphics', 'fullscreen', '0')
    Config.set('graphics', 'position', 'custom')
    Config.set('graphics', 'left', '200')
    Config.set('graphics', 'top', '100')
    Config.set('kivy', 'exit_on_escape', '0')
    
    print('配置已设置', file=error_log)
    error_log.flush()
    
    # 捕获main中的所有异常
    import main as main_module
    
except SystemExit:
    error_log.write('SystemExit 被捕获\n')
    traceback.print_exc()
except Exception:
    error_log.write('异常被捕获:\n')
    traceback.print_exc()
finally:
    error_log.flush()
    error_log.close()
