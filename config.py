"""
config.py — 全局配置（移动端优化版 v3.2）
"""

import os
import sys

# ──────────────────────────────────────────────
# 存储路径
# ──────────────────────────────────────────────
def app_storage_path() -> str:
    env_path = os.environ.get("APP_STORAGE")
    if env_path:
        return env_path
    is_android = bool(os.environ.get("ANDROID_ROOT") or os.environ.get("ANDROID_DATA"))
    if is_android:
        home = os.environ.get("HOME", "/data/data/com.example.app/files")
        return os.path.join(home, ".e")
    else:
        base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, "data")


# ─── 密码管理 ───────────────────────────────────────
_PASSWORD_FILE = None

def _get_password_path():
    global _PASSWORD_FILE
    if _PASSWORD_FILE is None:
        _PASSWORD_FILE = os.path.join(app_storage_path(), '.app_password')
    return _PASSWORD_FILE

def _get_password():
    try:
        p = _get_password_path()
        if os.path.exists(p):
            with open(p, 'r') as f:
                return f.read().strip()
    except:
        pass
    return ''

def _set_password(pwd):
    try:
        with open(_get_password_path(), 'w') as f:
            f.write(pwd.strip())
        return True
    except:
        return False

def _has_password():
    return bool(_get_password())


# ──────────────────────────────────────────────
# 颜色 — 正常可读配色
# ──────────────────────────────────────────────
class Color:
    class Light:
        BG          = (0.96, 0.96, 0.95, 1)  # #F5F5F2 暖白
        CARD        = (1.00, 1.00, 1.00, 1)  # #FFFFFF 纯白
        CARD_ALT    = (0.97, 0.97, 0.96, 1)  # #F7F7F5 浅灰

        TEXT        = (0.00, 0.00, 0.00, 1)  # #000000 黑色
        TEXT_SEC    = (0.35, 0.35, 0.35, 1)  # #595959 深灰
        TEXT_DIM    = (0.60, 0.60, 0.60, 1)  # #999999 中灰

        ACCENT      = (0.10, 0.45, 0.91, 1)  # #1A73E8
        BLUE_LIGHT  = (0.20, 0.55, 0.95, 1)
        GREEN       = (0.20, 0.66, 0.33, 1)  # #33A854
        RED         = (0.92, 0.26, 0.21, 1)  # #EA4335
        ORANGE      = (0.96, 0.55, 0.14, 1)  # #F58C23
        GOLD        = (0.80, 0.55, 0.10, 1)  # #CC8C1A

        HEADER_BG   = (0.10, 0.45, 0.91, 1)  # #1A73E8
        HEADER_TEXT = (1.00, 1.00, 1.00, 1)

        INPUT_BG    = (0.94, 0.94, 0.93, 1)  # #F0F0ED 浅灰
        INPUT_BORDER= (0.78, 0.78, 0.78, 1)
        INPUT_FOCUS = (0.10, 0.45, 0.91, 1)

        DIVIDER     = (0.88, 0.88, 0.86, 1)
        TOOLBAR_BG  = (1.00, 1.00, 1.00, 1)
        BADGE_BG    = (0.92, 0.26, 0.21, 1)
        BADGE_TEXT  = (1.00, 1.00, 1.00, 1)

        POPUP_BG    = (1.00, 1.00, 1.00, 1)
        POPUP_OVER  = (0.00, 0.00, 0.00, 0.45)

    class Dark:
        BG          = (0.11, 0.11, 0.13, 1)  # #1C1C21
        CARD        = (0.16, 0.16, 0.19, 1)  # #29292F
        CARD_ALT    = (0.19, 0.19, 0.22, 1)  # #303036

        TEXT        = (0.95, 0.95, 0.95, 1)  # #F2F2F2 白色
        TEXT_SEC    = (0.68, 0.68, 0.70, 1)  # #ADADB3
        TEXT_DIM    = (0.50, 0.50, 0.53, 1)  # #808087

        ACCENT      = (0.30, 0.60, 1.00, 1)
        BLUE_LIGHT  = (0.40, 0.68, 1.00, 1)
        GREEN       = (0.35, 0.75, 0.50, 1)
        RED         = (0.92, 0.40, 0.38, 1)
        ORANGE      = (0.92, 0.60, 0.30, 1)
        GOLD        = (0.88, 0.68, 0.28, 1)

        HEADER_BG   = (0.08, 0.10, 0.14, 1)
        HEADER_TEXT = (1.00, 1.00, 1.00, 1)

        INPUT_BG    = (0.20, 0.20, 0.24, 1)
        INPUT_BORDER= (0.32, 0.32, 0.35, 1)
        INPUT_FOCUS = (0.30, 0.60, 1.00, 1)

        DIVIDER     = (0.24, 0.24, 0.27, 1)
        TOOLBAR_BG  = (0.13, 0.13, 0.15, 1)
        BADGE_BG    = (0.92, 0.40, 0.38, 1)
        BADGE_TEXT  = (0.10, 0.10, 0.12, 1)

        POPUP_BG    = (0.18, 0.18, 0.22, 1)
        POPUP_OVER  = (0.00, 0.00, 0.00, 0.7)


# ──────────────────────────────────────────────
# 主题状态
# ──────────────────────────────────────────────
_current_theme = 'light'
_auto_theme = True

def set_theme(mode: str):
    global _current_theme, _auto_theme
    _current_theme = mode
    _auto_theme = False

def get_theme():
    return Color.Light if _current_theme == 'light' else Color.Dark

def toggle_theme():
    global _current_theme, _auto_theme
    _current_theme = 'dark' if _current_theme == 'light' else 'light'
    _auto_theme = False
    return _current_theme

def is_auto_theme():
    return _auto_theme

def set_auto_theme(auto: bool):
    global _auto_theme
    _auto_theme = auto


# ──────────────────────────────────────────────
# 尺寸 & 间距
# ──────────────────────────────────────────────
class Size:
    PAGE_PAD     = 16
    CARD_PAD     = 16
    CARD_RADIUS  = 12
    BTN_RADIUS   = 12
    INPUT_RADIUS = 12

    HEADER_H     = 56
    TOOLBAR_H    = 64
    CARD_MIN_H   = 76
    INPUT_H      = 48
    BTN_H        = 48
    LIST_ITEM_H  = 76
    BADGE_SIZE   = 24

    TITLE     = 22
    HEADING   = 18
    BODY      = 16
    SMALL     = 14
    TINY      = 13
    BADGE     = 12

    SPACING_S = 10
    SPACING_M = 14
    SPACING_L = 18
    SPACING_XL= 26


# ──────────────────────────────────────────────
# 数据库
# ──────────────────────────────────────────────
class Database:
    STORAGE_ROOT = app_storage_path()
    DB_DIR       = os.path.join(STORAGE_ROOT, "db")
    DB_NAME      = "app.db"
    DB_PATH      = os.path.join(DB_DIR, DB_NAME)


# ──────────────────────────────────────────────
# 应用信息
# ──────────────────────────────────────────────
class AppInfo:
    NAME     = "机械施工记账"
    VERSION  = "3.0"
    DEBUG    = False
    BACKUP_DIR_NAME = "机械施工记账备份"

    @classmethod
    def get_backup_dir(cls):
        import sys as _sys
        is_android = bool(os.environ.get("ANDROID_ROOT") or os.environ.get("ANDROID_DATA"))
        if is_android:
            return f"/storage/emulated/0/{cls.BACKUP_DIR_NAME}"
        if _sys.platform == 'win32':
            return f"C:\\{cls.BACKUP_DIR_NAME}"
        return os.path.join(os.path.expanduser("~"), cls.BACKUP_DIR_NAME)
