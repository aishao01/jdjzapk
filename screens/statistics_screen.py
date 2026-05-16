"""
statistics_screen.py — 统计汇总页面（v3.0 现代风格）
卡片式数据概览，分组统计表格
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from config import get_theme, Size
from database import get_db
from widgets import TopBar, Card, Divider, EmptyHint, draw_bg


def draw_simple_card(widget, color, radius=8):
    """绘制简单卡片背景"""
    import sys
    if sys.platform == 'win32':
        widget.canvas.before.clear()
        with widget.canvas.before:
            Color(*color)
            RoundedRectangle(size=widget.size, pos=widget.pos, radius=[dp(radius)])


class StatisticsScreen(Screen):
    """统计汇总页面"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'statistics'
        self.customer_id = None
        self.customer_name = ''
        self._build_ui()

    def _build_ui(self):
        self._theme = get_theme()
        main = BoxLayout(orientation='vertical', spacing=0)
        self.add_widget(main)

        top = TopBar(
            title='📊 统计汇总',
            on_back=lambda w: self._go_back()
        )
        main.add_widget(top)

        sv = ScrollView()
        self._container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(Size.SPACING_M),
            padding=(dp(Size.PAGE_PAD), dp(Size.SPACING_M),
                     dp(Size.PAGE_PAD), dp(Size.SPACING_XL)),
        )
        self._container.bind(minimum_height=self._container.setter('height'))
        sv.add_widget(self._container)
        main.add_widget(sv)

        self._title_label = Label(
            text='',
            font_size=dp(20),
            bold=True,
            size_hint_y=None,
            height=dp(32),
            halign='left',
        )
        self._title_label.bind(size=lambda w, *a: setattr(w, 'text_size', (w.width, None)))
        self._container.add_widget(self._title_label)

        self._content_area = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(Size.SPACING_M),
        )
        self._content_area.bind(minimum_height=self._content_area.setter('height'))
        self._container.add_widget(self._content_area)

    def _go_back(self):
        if self.manager and self.manager.has_screen('record_list'):
            self.manager.current = 'record_list'

    def refresh(self, cid, cname):
        self.customer_id = cid
        self.customer_name = cname
        Clock.schedule_once(lambda dt: self._do_refresh(), 0)

    def load_customer(self, cid, name):
        self.refresh(cid, name)

    def _do_refresh(self):
        theme = get_theme()
        Clock.schedule_once(lambda dt: setattr(self._title_label, 'color', theme.TEXT), 0)

        if not self.customer_id:
            self._title_label.text = '请先选择客户'
            self._content_area.clear_widgets()
            return

        self._title_label.text = f'📈 {self.customer_name}'
        self._content_area.clear_widgets()

        with get_db() as db:
            rows = db.execute(
                'SELECT * FROM records WHERE customer_id = ? ORDER BY date DESC',
                (self.customer_id,)
            ).fetchall()
            records = [dict(r) for r in rows]

        if not records:
            hint = EmptyHint(text='暂无记录数据')
            self._content_area.add_widget(hint)
            return

        # 1. 数据概览
        overview = self._build_overview(records)
        self._content_area.add_widget(overview)

        # 2. 按机型统计
        machine_section = self._build_machine_stats(records)
        self._content_area.add_widget(machine_section)

        # 3. 按日期统计
        date_section = self._build_date_stats(records[:30])
        self._content_area.add_widget(date_section)

    def _build_overview(self, records):
        total_count = len(records)
        total_hours = sum(r.get('total_hours', 0) or 0 for r in records)
        total_amount = sum(r.get('total_amount', 0) or 0 for r in records)

        theme = get_theme()

        # 数据概览卡片
        card = Card()
        title = Label(text='📋 数据概览', font_size=dp(16), bold=True,
                      size_hint_y=None, height=dp(24), halign='left',
                      color=theme.TEXT)
        card.add_widget(title)

        # 三列布局
        grid = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(70), spacing=dp(8))

        def make_mini_card(label, value, accent_color):
            c = BoxLayout(orientation='vertical', size_hint_x=0.33, padding=dp(8), spacing=dp(2))
            draw_simple_card(c, theme.CARD_ALT, 8)
            c.add_widget(Label(text=label, font_size=dp(11), size_hint_y=None, height=dp(16),
                               halign='center', color=theme.TEXT_SEC))
            v = Label(text=value, font_size=dp(18), bold=True, size_hint_y=None, height=dp(26),
                      halign='center', color=accent_color)
            c.add_widget(v)
            return c

        grid.add_widget(make_mini_card('记录数', f'{total_count} 条', theme.ACCENT))
        grid.add_widget(make_mini_card('总时长', f'{total_hours:.1f}h', theme.GREEN))
        grid.add_widget(make_mini_card('总金额', f'¥{total_amount:.0f}', theme.GOLD))

        card.add_widget(grid)
        return card

    def _build_machine_stats(self, records):
        theme = get_theme()

        machine_groups = {}
        for r in records:
            mt = r.get('machine_type', '未指定')
            if mt not in machine_groups:
                machine_groups[mt] = {'count': 0, 'total_hours': 0.0, 'total_amount': 0.0}
            machine_groups[mt]['count'] += 1
            machine_groups[mt]['total_hours'] += r.get('total_hours', 0) or 0
            machine_groups[mt]['total_amount'] += r.get('total_amount', 0) or 0

        card = Card()
        title = Label(text='🤖 按机型统计', font_size=dp(16), bold=True,
                      size_hint_y=None, height=dp(24), halign='left',
                      color=theme.TEXT)
        card.add_widget(title)

        # 表头
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(24), spacing=dp(4))
        for txt, width in [('机型', 0.4), ('条数', 0.2), ('时长', 0.2), ('金额', 0.2)]:
            lbl = Label(text=txt, font_size=dp(12), bold=True, size_hint_x=width,
                        halign='center', color=theme.TEXT_SEC)
            header.add_widget(lbl)
        card.add_widget(header)
        card.add_widget(Divider())

        # 数据行
        for mt, stats in machine_groups.items():
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(26), spacing=dp(4))
            data = [
                (mt, 0.4, 'left', True, theme.TEXT),
                (str(stats['count']), 0.2, 'center', False, theme.TEXT_SEC),
                (f"{stats['total_hours']:.1f}", 0.2, 'center', False, theme.TEXT),
                (f"¥{stats['total_amount']:.0f}", 0.2, 'center', False, theme.GOLD),
            ]
            for txt, width, align, bold, color in data:
                lbl = Label(text=txt, font_size=dp(12), size_hint_x=width, halign=align, bold=bold,
                           color=color)
                row.add_widget(lbl)
            card.add_widget(row)

        # 合计
        card.add_widget(Divider())
        total_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(28), spacing=dp(4))
        total_count = sum(s['count'] for s in machine_groups.values())
        total_hours = sum(s['total_hours'] for s in machine_groups.values())
        total_amount = sum(s['total_amount'] for s in machine_groups.values())
        data = [
            ('合计', 0.4, 'left', True, theme.ACCENT),
            (str(total_count), 0.2, 'center', True, theme.ACCENT),
            (f"{total_hours:.1f}", 0.2, 'center', True, theme.ACCENT),
            (f"¥{total_amount:.0f}", 0.2, 'center', True, theme.GOLD),
        ]
        for txt, width, align, bold, color in data:
            lbl = Label(text=txt, font_size=dp(12), size_hint_x=width, halign=align, bold=bold,
                       color=color)
            total_row.add_widget(lbl)
        card.add_widget(total_row)

        return card

    def _build_date_stats(self, records):
        theme = get_theme()

        date_groups = {}
        for r in records:
            d = r.get('date', '未知日期')
            if d not in date_groups:
                date_groups[d] = {'count': 0, 'total_hours': 0.0, 'total_amount': 0.0}
            date_groups[d]['count'] += 1
            date_groups[d]['total_hours'] += r.get('total_hours', 0) or 0
            date_groups[d]['total_amount'] += r.get('total_amount', 0) or 0

        card = Card()
        title = Label(text='📅 按日期统计', font_size=dp(16), bold=True,
                      size_hint_y=None, height=dp(24), halign='left',
                      color=theme.TEXT)
        card.add_widget(title)

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(24), spacing=dp(4))
        for txt, width in [('日期', 0.4), ('条数', 0.2), ('时长', 0.2), ('金额', 0.2)]:
            lbl = Label(text=txt, font_size=dp(12), bold=True, size_hint_x=width,
                        halign='center', color=theme.TEXT_SEC)
            header.add_widget(lbl)
        card.add_widget(header)
        card.add_widget(Divider())

        sorted_dates = sorted(date_groups.keys(), reverse=True)
        for d in sorted_dates:
            stats = date_groups[d]
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(26), spacing=dp(4))
            data = [
                (d, 0.4, 'left', False, theme.TEXT),
                (str(stats['count']), 0.2, 'center', False, theme.TEXT_SEC),
                (f"{stats['total_hours']:.1f}", 0.2, 'center', False, theme.TEXT),
                (f"¥{stats['total_amount']:.0f}", 0.2, 'center', False, theme.GOLD),
            ]
            for txt, width, align, bold, color in data:
                lbl = Label(text=txt, font_size=dp(12), size_hint_x=width, halign=align, bold=bold,
                           color=color)
                row.add_widget(lbl)
            card.add_widget(row)

        return card
