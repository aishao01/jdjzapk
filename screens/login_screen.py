"""
login_screen.py — 登录/解锁页面（v3.0 现代风格）
暖色渐变背景，蓝调卡片，大输入框
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.window import Window

from config import get_theme, set_theme, Size, AppInfo
from config import _has_password, _get_password, _set_password
from widgets import BtnPrimary, draw_bg


class LoginScreen(Screen):
    """登录/解锁页面 — 暖灰背景，蓝调卡片居中"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._bg_rects = []

        outer = BoxLayout(
            orientation='vertical',
            padding=[dp(24), dp(80), dp(24), dp(60)],
        )

        # 白色圆角卡片（蓝色背景）
        card = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            width=dp(320),
            padding=[dp(28), dp(28), dp(28), dp(28)],
            spacing=dp(16),
        )
        card.bind(minimum_height=card.setter('height'))
        Clock.schedule_once(lambda dt: draw_bg(card, get_theme().HEADER_BG))

        # ── 标题（主题色自适应）──
        title = Label(
            text='机械施工记账',
            font_size=dp(26),
            bold=True,
            size_hint_y=None,
            height=dp(38),
            halign='center',
            color=(1, 1, 1, 1),
        )
        # 浅色黑色 / 深色白色
        Clock.schedule_once(lambda dt: setattr(title, 'color', get_theme().TEXT), 0)
        card.add_widget(title)

        # ── 密码输入框（hint_text 显示"请输入密码"）──
        t = get_theme()
        self._input = TextInput(
            password=True,
            font_size=dp(18),
            size_hint_y=None,
            height=dp(50),
            multiline=False,
            write_tab=False,
            hint_text='请输入密码',
            padding=(dp(14), dp(12)),
            background_color=t.INPUT_BG,
            foreground_color=t.TEXT,
            hint_text_color=(0.6, 0.6, 0.6, 1),  # 灰色
        )
        self._input.bind(on_text_validate=self._on_unlock)
        card.add_widget(self._input)

        # ── 解锁按钮 ──
        self._btn = BtnPrimary(text='解锁', color_name='GREEN')
        self._btn.bind(on_release=self._on_unlock)
        card.add_widget(self._btn)

        # ── 提示 ──
        self._hint = Label(
            text='首次使用直接输入密码即可设置',
            font_size=dp(Size.TINY),
            size_hint_y=None,
            height=dp(18),
            halign='center',
            color=(0.62, 0.62, 0.65, 1),
        )
        card.add_widget(self._hint)

        outer.add_widget(Widget(size_hint_y=1))
        outer.add_widget(card)
        outer.add_widget(Widget(size_hint_y=2))

        self.add_widget(outer)

    def on_enter(self, *a):
        Clock.schedule_once(lambda dt: self._do_focus(), 0.1)
        has_pw = False
        try:
            has_pw = _has_password()
        except NameError:
            pass
        if has_pw:
            self._hint.text = ''
        else:
            self._hint.text = '首次使用直接输入密码即可设置'

    def _do_focus(self):
        if self._input and self._input.get_root_window():
            self._input.focus = True

    def _on_unlock(self, *a):
        pw = self._input.text.strip()
        if not pw:
            self._hint.text = '⚠️ 密码不能为空'
            self._hint.color = (0.92, 0.26, 0.21, 1)
            return

        try:
            has_pw = _has_password()
        except NameError:
            has_pw = False

        if not has_pw:
            try:
                _set_password(pw)
            except NameError:
                self._hint.text = '⚠️ 密码设置失败（请重启应用）'
                self._hint.color = (0.92, 0.26, 0.21, 1)
                return
            self._goto_main()
        else:
            try:
                stored = _get_password()
            except NameError:
                self._hint.text = '⚠️ 无法读取密码'
                self._hint.color = (0.92, 0.26, 0.21, 1)
                return
            if pw == stored:
                self._goto_main()
            else:
                self._hint.text = '❌ 密码错误，请重试'
                self._hint.color = (0.92, 0.26, 0.21, 1)
                self._input.text = ''
                Clock.schedule_once(lambda dt: self._do_focus(), 0.1)

    def _goto_main(self):
        self._input.text = ''
        self._hint.text = ''
        if self.manager and hasattr(self.manager, 'current'):
            self.manager.current = 'customer_list'
