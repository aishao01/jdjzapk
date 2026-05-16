"""
config_theme.py — 可变的主题对象（v3.2 正常配色）
"""
from kivy.clock import Clock


class ThemeColors:
    def __init__(self, dark=False):
        self._dark = dark
        self._set_colors()

    def _set_colors(self):
        if self._dark:
            self.BG          = (0.11, 0.11, 0.13, 1)
            self.CARD        = (0.16, 0.16, 0.19, 1)
            self.CARD_ALT    = (0.19, 0.19, 0.22, 1)
            self.TEXT        = (0.95, 0.95, 0.95, 1)
            self.TEXT_SEC    = (0.68, 0.68, 0.70, 1)
            self.TEXT_DIM    = (0.50, 0.50, 0.53, 1)
            self.ACCENT      = (0.30, 0.60, 1.00, 1)
            self.BLUE_LIGHT  = (0.40, 0.68, 1.00, 1)
            self.GREEN       = (0.35, 0.75, 0.50, 1)
            self.RED         = (0.92, 0.40, 0.38, 1)
            self.ORANGE      = (0.92, 0.60, 0.30, 1)
            self.GOLD        = (0.88, 0.68, 0.28, 1)
            self.HEADER_BG   = (0.08, 0.10, 0.14, 1)
            self.HEADER_TEXT = (1.00, 1.00, 1.00, 1)
            self.INPUT_BG    = (0.20, 0.20, 0.24, 1)
            self.INPUT_BORDER= (0.32, 0.32, 0.35, 1)
            self.DIVIDER     = (0.24, 0.24, 0.27, 1)
            self.TOOLBAR_BG  = (0.13, 0.13, 0.15, 1)
            self.BADGE_BG    = (0.92, 0.40, 0.38, 1)
            self.BADGE_TEXT  = (0.10, 0.10, 0.12, 1)
            self.POPUP_BG    = (0.18, 0.18, 0.22, 1)
            self.POPUP_OVER  = (0.00, 0.00, 0.00, 0.7)
        else:
            self.BG          = (0.96, 0.96, 0.95, 1)
            self.CARD        = (1.00, 1.00, 1.00, 1)
            self.CARD_ALT    = (0.97, 0.97, 0.96, 1)
            self.TEXT        = (0.00, 0.00, 0.00, 1)
            self.TEXT_SEC    = (0.35, 0.35, 0.35, 1)
            self.TEXT_DIM    = (0.60, 0.60, 0.60, 1)
            self.ACCENT      = (0.10, 0.45, 0.91, 1)
            self.BLUE_LIGHT  = (0.20, 0.55, 0.95, 1)
            self.GREEN       = (0.20, 0.66, 0.33, 1)
            self.RED         = (0.92, 0.26, 0.21, 1)
            self.ORANGE      = (0.96, 0.55, 0.14, 1)
            self.GOLD        = (0.80, 0.55, 0.10, 1)
            self.HEADER_BG   = (0.10, 0.45, 0.91, 1)
            self.HEADER_TEXT = (1.00, 1.00, 1.00, 1)
            self.INPUT_BG    = (0.94, 0.94, 0.93, 1)
            self.INPUT_BORDER= (0.78, 0.78, 0.78, 1)
            self.DIVIDER     = (0.88, 0.88, 0.86, 1)
            self.TOOLBAR_BG  = (1.00, 1.00, 1.00, 1)
            self.BADGE_BG    = (0.92, 0.26, 0.21, 1)
            self.BADGE_TEXT  = (1.00, 1.00, 1.00, 1)
            self.POPUP_BG    = (1.00, 1.00, 1.00, 1)
            self.POPUP_OVER  = (0.00, 0.00, 0.00, 0.45)


_active_theme = ThemeColors(dark=False)


def set_theme(mode: str):
    _active_theme._dark = (mode == 'dark')
    _active_theme._set_colors()


def get_theme():
    return _active_theme
