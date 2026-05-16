"""
widgets.py — 现代中国风 UI 组件（v3.0）
清新蓝+暖金配色，48dp 触摸目标，大字体系
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock

from config import get_theme, Size


# ──────────────────────────────────────────
# 卡片容器（现代圆角白卡）
# ──────────────────────────────────────────
class Card(BoxLayout):
    """现代圆角卡片 — 12dp 圆角，柔和阴影效果"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(Size.CARD_PAD)
        self.spacing = dp(Size.SPACING_M)
        self.size_hint_y = None
        Clock.schedule_once(self._update_bg, 0)

    def _update_bg(self, *a):
        theme = get_theme()
        draw_bg(self, theme.CARD, Size.CARD_RADIUS)


# ──────────────────────────────────────────
# 顶部导航栏（蓝底白字，现代简洁）
# ──────────────────────────────────────────
class TopBar(BoxLayout):
    """统一顶部栏（56dp，蓝底，宽松文字）"""
    def __init__(self, title='', on_back=None, right_btns=None, back_color=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(Size.HEADER_H)
        self.padding = (dp(8), 0, dp(8), 0)
        self.spacing = dp(4)

        Clock.schedule_once(self._update_bg, 0)

        # 返回按钮（左侧）
        bc = back_color or (1, 1, 1, 1)
        if on_back:
            btn = Button(
                text='‹ 返回',
                font_size=dp(Size.BODY),
                bold=True,
                size_hint_x=None,
                width=dp(72),
                color=bc,
                background_color=(0, 0, 0, 0),
                background_normal='',
            )
            btn.bind(on_release=on_back)
            self.add_widget(btn)

        # 标题（居中，更大字，主题色自适应）
        lbl = Label(
            text=title,
            font_size=dp(Size.TITLE),
            bold=True,
            color=(1, 1, 1, 1),
            halign='center',
        )
        # 浅色模式黑色 / 深色模式白色
        Clock.schedule_once(lambda dt: setattr(lbl, 'color', get_theme().TEXT), 0)
        self.add_widget(lbl)

        # 右侧按钮
        if right_btns:
            for txt, cb in right_btns:
                btn = Button(
                    text=txt,
                    font_size=dp(Size.SMALL),
                    size_hint_x=None,
                    width=dp(64),
                    color=(1, 1, 1, 1),
                    background_color=(0, 0, 0, 0),
                    background_normal='',
                )
                btn.bind(on_release=cb)
                self.add_widget(btn)
        else:
            spacer = Widget(size_hint_x=1)
            self.add_widget(spacer)

    def _update_bg(self, *a):
        theme = get_theme()
        draw_bg(self, theme.HEADER_BG)


# ──────────────────────────────────────────
# 按钮（大尺寸，48dp 标准，12dp 圆角）
# ──────────────────────────────────────────
class BtnPrimary(Button):
    """主按钮（蓝/绿/金，48dp 高，12dp 圆角）"""
    def __init__(self, text='', color_name='ACCENT', **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self._color_name = color_name
        self.font_size = dp(Size.BODY)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(Size.BTN_H)
        self.background_normal = ''
        self.background_down = ''
        Clock.schedule_once(self._update_style, 0)

    def _update_style(self, *a):
        theme = get_theme()
        c = getattr(theme, self._color_name, theme.ACCENT)
        self.background_color = c
        self.color = (1, 1, 1, 1)


class BtnDanger(Button):
    """危险按钮（红色，48dp 高）"""
    def __init__(self, text='', **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = dp(Size.BODY)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(Size.BTN_H)
        self.background_normal = ''
        self.background_down = ''
        Clock.schedule_once(self._update_style, 0)

    def _update_style(self, *a):
        theme = get_theme()
        self.background_color = theme.RED
        self.color = (1, 1, 1, 1)


class BtnOutline(Button):
    """线框按钮（透明底 + 蓝色文字）"""
    def __init__(self, text='', **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = dp(Size.SMALL)
        self.size_hint_y = None
        self.height = dp(Size.BTN_H)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.background_down = ''
        Clock.schedule_once(self._update_style, 0)

    def _update_style(self, *a):
        theme = get_theme()
        self.color = theme.ACCENT


class BtnIcon(Button):
    """图标/文字按钮（透明背景）"""
    def __init__(self, text='', **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size=dp(Size.SMALL)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.background_down = ''
        Clock.schedule_once(self._update_style, 0)

    def _update_style(self, *a):
        theme = get_theme()
        self.color = theme.HEADER_TEXT


# ──────────────────────────────────────────
# 带标签的输入框（48dp 高，暖灰底）
# ──────────────────────────────────────────
class LabelInput(BoxLayout):
    """标签 + 输入框（垂直布局，现代暖灰风格）"""
    def __init__(self, label='', hint='', value='', readonly=False, multiline=False,
                 input_type='text', **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(Size.INPUT_H) + dp(24)
        self.spacing = dp(4)

        # 标签（上方，灰色小字）
        self._label = Label(
            text=label,
            font_size=dp(Size.TINY),
            halign='left',
            size_hint_y=None,
            height=dp(18),
        )
        Clock.schedule_once(lambda dt: setattr(self._label, 'color', get_theme().TEXT_SEC), 0)
        self.add_widget(self._label)

        # 输入框（读取当前主题色）
        t = get_theme()
        self._input = TextInput(
            text=value,
            hint_text=hint,
            multiline=multiline,
            font_size=dp(Size.BODY),
            size_hint_y=None,
            height=dp(Size.INPUT_H),
            padding=(dp(12), dp(10)),
            readonly=readonly,
            background_color=t.INPUT_BG,
            foreground_color=t.TEXT,
            hint_text_color=t.TEXT_SEC,
        )
        self.add_widget(self._input)

    @property
    def text(self):
        return self._input.text

    @text.setter
    def text(self, val):
        self._input.text = str(val)


class LabelSpinner(BoxLayout):
    """标签 + Spinner（垂直布局，暖灰风格）"""
    def __init__(self, label='', values=None, text='', **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(Size.INPUT_H) + dp(24)
        self.spacing = dp(4)

        lbl = Label(
            text=label,
            font_size=dp(Size.TINY),
            halign='left',
            size_hint_y=None,
            height=dp(18),
        )
        Clock.schedule_once(lambda dt: setattr(lbl, 'color', get_theme().TEXT_SEC), 0)
        self.add_widget(lbl)

        t = get_theme()
        self._spinner = Spinner(
            text=text or (values[0] if values else ''),
            values=values or (),
            font_size=dp(Size.BODY),
            size_hint_y=None,
            height=dp(Size.INPUT_H),
            background_color=t.INPUT_BG,
            color=t.TEXT,
        )
        self.add_widget(self._spinner)

    @property
    def text(self):
        return self._spinner.text

    @text.setter
    def text(self, val):
        self._spinner.text = str(val)


# ──────────────────────────────────────────
# 可滚动的列表容器
# ──────────────────────────────────────────
class ScrollList(BoxLayout):
    """内置 ScrollView 的可滚动列表"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self._scroll = ScrollView()
        self._container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(Size.SPACING_S),
            padding=(dp(Size.PAGE_PAD), dp(Size.SPACING_S),
                     dp(Size.PAGE_PAD), dp(Size.SPACING_S)),
        )
        self._container.bind(minimum_height=self._container.setter('height'))
        self._scroll.add_widget(self._container)
        self.add_widget(self._scroll)

    def clear(self):
        self._container.clear_widgets()

    def add_item(self, widget):
        self._container.add_widget(widget)

    @property
    def container(self):
        return self._container

    @property
    def count(self):
        return len(self._container.children)


# ──────────────────────────────────────────
# 空状态提示
# ──────────────────────────────────────────
class EmptyHint(Label):
    """空列表提示"""
    def __init__(self, text='暂无数据', **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size=dp(Size.BODY)
        self.size_hint_y = None
        self.height = dp(80)
        self.halign = 'center'
        Clock.schedule_once(lambda dt: setattr(self, 'color', get_theme().TEXT_DIM), 0)


# ──────────────────────────────────────────
# 确认弹窗
# ──────────────────────────────────────────
from kivy.uix.popup import Popup


class ConfirmPopup:
    """统一确认弹窗"""
    @staticmethod
    def show(title='提示', message='', confirm_text='确定', cancel_text='取消',
             confirm_color='GREEN', on_confirm=None):
        theme = get_theme()
        content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))

        msg = Label(
            text=message,
            font_size=dp(Size.SMALL),
            halign='center',
            size_hint_y=None,
            height=dp(50),
        )
        msg.bind(size=lambda w, *a: setattr(w, 'text_size', (w.width - 20, None)))
        content.add_widget(msg)

        btns = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))

        if cancel_text:
            cb = Button(
                text=cancel_text,
                font_size=dp(Size.SMALL),
                background_color=theme.CARD_ALT,
                background_normal='',
            )
            cb.bind(on_release=popup.dismiss)
            btns.add_widget(cb)

        ok = Button(
            text=confirm_text,
            font_size=dp(Size.SMALL),
            bold=True,
        )
        Clock.schedule_once(lambda dt: setattr(ok, 'background_color',
                            getattr(theme, confirm_color, theme.GREEN)), 0)
        btns.add_widget(ok)

        content.add_widget(btns)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.85, 0.35),
            background='',
            background_color=(0, 0, 0, 0),
            separator_color=(0, 0, 0, 0),
        )
        Clock.schedule_once(lambda dt: draw_bg(popup, theme.POPUP_BG, 12), 0)

        ok.bind(on_release=lambda w: (popup.dismiss(), on_confirm() if on_confirm else None))

        popup.open()


# ──────────────────────────────────────────
# 底部工具栏
# ──────────────────────────────────────────
class BottomToolbar(BoxLayout):
    """底部固定工具栏（64dp 高，白色）"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(Size.TOOLBAR_H)
        self.padding = (dp(Size.SPACING_M), dp(Size.SPACING_S))
        self.spacing = dp(Size.SPACING_M)
        Clock.schedule_once(self._update_bg, 0)

    def _update_bg(self, *a):
        theme = get_theme()
        draw_bg(self, theme.TOOLBAR_BG)


# ──────────────────────────────────────────
# 分割线
# ──────────────────────────────────────────
class Divider(Widget):
    """水平分割线"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(1)
        Clock.schedule_once(self._update_bg, 0)

    def _update_bg(self, *a):
        theme = get_theme()
        draw_bg(self, theme.DIVIDER)


# ──────────────────────────────────────────
# 工具函数：绘制背景
# ──────────────────────────────────────────
def draw_bg(widget, bg_color, radius=0):
    """给 widget 的背景绘制纯色圆角矩形"""
    import sys
    if sys.platform == 'win32':
        return
    widget.canvas.before.clear()
    with widget.canvas.before:
        Color(*bg_color)
        if radius > 0:
            widget._bg_rect = RoundedRectangle(
                size=widget.size, pos=widget.pos, radius=[dp(radius)])
        else:
            widget._bg_rect = Rectangle(size=widget.size, pos=widget.pos)
    widget.bind(size=lambda w, *a: setattr(w._bg_rect, 'size', w.size),
                pos=lambda w, *a: setattr(w._bg_rect, 'pos', w.pos))
