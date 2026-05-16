"""
customer_screen.py — 客户列表页面（v3.0 现代风格）
搜索栏 + 圆角卡片列表 + 底部大按钮
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.clock import Clock
from config import get_theme, Size
from database import get_db
from widgets import Card, TopBar, BtnPrimary, BtnDanger, BtnOutline, BtnIcon, LabelInput, ScrollList, EmptyHint, ConfirmPopup, Divider, draw_bg


class CustomerListScreen(Screen):
    """客户列表页面"""

    app_ref = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'customer_list'
        self._customers = []
        self._filtered = []
        self._search_text = ''

        self._build_ui()

    def on_enter(self, *args):
        super().on_enter(*args)
        Clock.schedule_once(lambda dt: self.refresh_list(), 0)

    def _build_ui(self):
        theme = get_theme()
        draw_bg(self, theme.BG)

        root = BoxLayout(orientation='vertical', spacing=0)

        # ── 顶部导航栏 ──
        topbar = TopBar(
            title='客户列表',
            right_btns=[('⚙ 设置', lambda w: setattr(self.manager, 'current', 'settings'))],
        )
        root.add_widget(topbar)

        # ── 搜索栏（大号圆角输入框，读取主题色）──
        search_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(Size.INPUT_H + dp(16)),
            padding=(dp(Size.PAGE_PAD), dp(8), dp(Size.PAGE_PAD), dp(8)),
        )
        t = get_theme()
        self._search_input = TextInput(
            hint_text='🔍 搜索客户名称...',
            font_size=dp(Size.SMALL),
            size_hint_y=None,
            height=dp(Size.INPUT_H),
            padding=(dp(12), dp(10)),
            background_color=t.INPUT_BG,
            foreground_color=t.TEXT,
            hint_text_color=t.TEXT_SEC,
        )
        self._search_input.bind(text=self._on_search_text)
        search_box.add_widget(self._search_input)
        root.add_widget(search_box)

        # ── 客户列表 ──
        self._scroll_list = ScrollList()
        root.add_widget(self._scroll_list)

        # ── 底部新增按钮 ──
        bottom = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(Size.TOOLBAR_H),
            padding=(dp(Size.PAGE_PAD), dp(Size.SPACING_S)),
        )
        add_btn = BtnPrimary(text='+ 新增客户', color_name='GREEN', size_hint_x=1)
        add_btn.bind(on_release=self._show_add_popup)
        bottom.add_widget(add_btn)
        root.add_widget(bottom)

        self.add_widget(root)

    # ──────────────────────────────────────────
    # 搜索过滤
    # ──────────────────────────────────────────

    def _on_search_text(self, instance, value):
        self._search_text = value.strip()
        self._apply_filter()

    def _apply_filter(self):
        if not self._search_text:
            self._filtered = list(self._customers)
        else:
            kw = self._search_text.lower()
            self._filtered = [
                c for c in self._customers
                if kw in c['name'].lower()
            ]
        self._render_list()

    # ──────────────────────────────────────────
    # 列表渲染
    # ──────────────────────────────────────────

    def refresh_list(self):
        with get_db() as db:
            rows = db.execute(
                "SELECT id, name, phone, address, "
                "(SELECT COUNT(*) FROM records WHERE customer_id = customers.id) AS record_count "
                "FROM customers ORDER BY name ASC"
            ).fetchall()
        self._customers = [dict(r) for r in rows]
        self._apply_filter()

    def _render_list(self):
        self._scroll_list.clear()

        if not self._filtered:
            self._scroll_list.add_item(EmptyHint(text='暂无客户数据'))
            return

        for row in self._filtered:
            card = self._build_customer_card(row)
            self._scroll_list.add_item(card)

    def _build_customer_card(self, row):
        theme = get_theme()

        card = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(76),
            padding=(dp(Size.CARD_PAD), dp(10)),
            spacing=dp(Size.SPACING_M),
        )
        draw_bg(card, theme.CARD, Size.CARD_RADIUS)

        # ── 左侧：客户信息 ──
        info_box = BoxLayout(
            orientation='vertical',
            size_hint_x=0.55,
            spacing=dp(3),
        )

        # 客户名称（粗体，大号）
        name_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(24),
            spacing=dp(8),
        )
        name_lbl = Label(
            text=row['name'],
            font_size=dp(17),
            bold=True,
            halign='left',
            valign='middle',
            size_hint_x=0.7,
            color=theme.TEXT,
        )
        name_lbl.bind(size=lambda w, *a: setattr(w, 'text_size', (w.width, None)))
        name_box.add_widget(name_lbl)

        # 记录条数角标（蓝色圆角）
        badge = Label(
            text=f"{row['record_count']} 条",
            font_size=dp(Size.SMALL),
            bold=True,
            size_hint=(None, None),
            size=(dp(60), dp(22)),
            halign='center',
            valign='middle',
            color=(1, 1, 1, 1),
        )
        Clock.schedule_once(lambda dt, b=badge: draw_bg(b, theme.ACCENT, 10), 0)
        name_box.add_widget(badge)

        info_box.add_widget(name_box)

        # 电话
        if row['phone']:
            phone_lbl = Label(
                text=f"📞 {row['phone']}",
                font_size=dp(12),
                halign='left',
                valign='middle',
                size_hint_y=None,
                height=dp(18),
                color=theme.TEXT_SEC,
            )
            phone_lbl.bind(size=lambda w, *a: setattr(w, 'text_size', (w.width, None)))
            info_box.add_widget(phone_lbl)

        # 地址
        if row['address']:
            addr_lbl = Label(
                text=f"📍 {row['address']}",
                font_size=dp(12),
                halign='left',
                valign='middle',
                size_hint_y=None,
                height=dp(18),
                color=theme.TEXT_SEC,
            )
            addr_lbl.bind(size=lambda w, *a: setattr(w, 'text_size', (w.width, None)))
            info_box.add_widget(addr_lbl)

        card.add_widget(info_box)

        # ── 右侧：操作按钮 ──
        btn_box = BoxLayout(
            orientation='horizontal',
            size_hint_x=0.45,
            spacing=dp(8),
        )

        enter_btn = BtnPrimary(text='进入', color_name='GREEN')
        enter_btn.bind(on_release=lambda w, r=row: self._enter_customer(r))
        btn_box.add_widget(enter_btn)

        delete_btn = BtnDanger(text='删除')
        delete_btn.bind(on_release=lambda w, r=row: self._confirm_delete(r))
        btn_box.add_widget(delete_btn)

        card.add_widget(btn_box)

        return card

    # ──────────────────────────────────────────
    # 操作：进入客户
    # ──────────────────────────────────────────

    def _enter_customer(self, row):
        if self.app_ref:
            self.app_ref.current_customer_id = row['id']
            self.app_ref.current_customer_name = row['name']
        self.manager.current = 'record_list'
        record_screen = self.manager.get_screen('record_list')
        if hasattr(record_screen, 'load_customer'):
            record_screen.load_customer(row['id'], row['name'])
        if hasattr(record_screen, 'refresh_list'):
            record_screen.refresh_list()

    # ──────────────────────────────────────────
    # 操作：新增客户
    # ──────────────────────────────────────────

    def _show_add_popup(self, *args):
        theme = get_theme()

        content = BoxLayout(
            orientation='vertical',
            spacing=dp(14),
            padding=dp(20),
            size_hint_y=None,
            height=dp(340),
        )

        title = Label(
            text='新增客户',
            font_size=dp(Size.HEADING),
            bold=True,
            size_hint_y=None,
            height=dp(32),
            color=theme.TEXT,
        )
        content.add_widget(title)

        name_input = LabelInput(label='客户名称', hint='请输入客户名称')
        content.add_widget(name_input)

        phone_input = LabelInput(label='电话', hint='请输入电话号码')
        content.add_widget(phone_input)

        addr_input = LabelInput(label='地址', hint='请输入地址')
        content.add_widget(addr_input)

        btn_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(48),
            spacing=dp(12),
        )

        cancel_btn = Button(
            text='取消',
            font_size=dp(Size.SMALL),
            background_color=theme.CARD_ALT,
            background_normal='',
            color=theme.TEXT_SEC,
        )
        btn_row.add_widget(cancel_btn)

        save_btn = Button(
            text='保存',
            font_size=dp(Size.SMALL),
            bold=True,
            background_color=theme.GREEN,
            background_normal='',
            color=(1, 1, 1, 1),
        )
        btn_row.add_widget(save_btn)

        content.add_widget(btn_row)

        popup = Popup(
            title='',
            content=content,
            size_hint=(0.88, None),
            height=dp(340),
            background='',
            background_color=(0, 0, 0, 0),
            separator_color=(0, 0, 0, 0),
        )
        Clock.schedule_once(lambda dt: draw_bg(popup, theme.POPUP_BG, 14), 0)

        cancel_btn.bind(on_release=popup.dismiss)
        save_btn.bind(
            on_release=lambda w: self._save_customer(
                name_input.text.strip(),
                phone_input.text.strip(),
                addr_input.text.strip(),
                popup,
            )
        )

        popup.open()

    def _save_customer(self, name, phone, address, popup):
        if not name:
            return
        with get_db() as db:
            db.execute(
                "INSERT INTO customers (name, phone, address) VALUES (?, ?, ?)",
                (name, phone, address),
            )
        popup.dismiss()
        self.refresh_list()

    # ──────────────────────────────────────────
    # 操作：删除客户
    # ──────────────────────────────────────────

    def _confirm_delete(self, row):
        ConfirmPopup.show(
            title='删除客户',
            message=f'确定要删除客户「{row["name"]}」吗？\n相关记录也将被删除。',
            confirm_text='删除',
            confirm_color='RED',
            on_confirm=lambda: self._delete_customer(row),
        )

    def _delete_customer(self, row):
        with get_db() as db:
            db.execute("DELETE FROM records WHERE customer_id = ?", (row['id'],))
            db.execute("DELETE FROM customers WHERE id = ?", (row['id'],))
        self.refresh_list()
