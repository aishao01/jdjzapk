"""
record_list_screen.py — 记录列表页面（v3.0）
现代卡片列表，筛选栏+底部工具栏，导出直接跳转
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.clock import Clock
from datetime import datetime
from config import get_theme, Size
from database import get_db
from widgets import (
    Card, TopBar, BtnPrimary, BtnOutline,
    ScrollList, EmptyHint, ConfirmPopup,
    draw_bg, BottomToolbar
)


class RecordListScreen(Screen):
    """记录列表页面"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'record_list'
        self.customer_id = None
        self.customer_name = ''
        self.selected_ids = set()

        # 筛选状态
        self.filter_year = '全部'
        self.filter_month = '全部'
        self.filter_start = ''
        self.filter_end = ''

        # 缓存数据
        self._records = []

        self._build_ui()

    # ──────────────────────────────────────────
    # UI 构建
    # ──────────────────────────────────────────

    def _build_ui(self):
        self._theme = get_theme()
        main = BoxLayout(orientation='vertical', spacing=0)
        self.add_widget(main)

        # 顶部导航
        top = TopBar(
            title='记录列表',
            on_back=lambda w: self._go_back()
        )
        main.add_widget(top)

        # 信息栏 — 客户名
        self._info_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            padding=(dp(Size.PAGE_PAD), dp(4), dp(Size.PAGE_PAD), dp(4)),
            spacing=dp(Size.SPACING_M),
        )
        Clock.schedule_once(self._update_info_bar_bg, 0)
        self._customer_label = Label(
            text='',
            font_size=dp(Size.BODY),
            bold=True,
            halign='left',
            size_hint_x=1,
        )
        Clock.schedule_once(lambda dt: setattr(
            self._customer_label, 'color', get_theme().TEXT), 0)
        self._info_bar.add_widget(self._customer_label)
        main.add_widget(self._info_bar)

        # 筛选栏
        filter_bar = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            padding=(dp(Size.PAGE_PAD), dp(4), dp(Size.PAGE_PAD), dp(4)),
            spacing=dp(4),
        )
        Clock.schedule_once(lambda dt: draw_bg(
            filter_bar, get_theme().CARD_ALT), 0)

        # 第一行：年份 + 月份 + 全部按钮
        spinner_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(34),
            spacing=dp(6),
        )

        now = datetime.now()
        years = [str(y) for y in range(now.year - 10, now.year + 11)]
        t = get_theme()
        self._year_spinner = Spinner(
            text=str(now.year),
            values=years,
            font_size=dp(Size.SMALL),
            size_hint=(0.3, 1),
            background_color=t.INPUT_BG,
            color=t.TEXT,
        )
        self._year_spinner.bind(text=lambda w, v: self._on_year_spinner(v))

        months = [f'{m:02d}' for m in range(1, 13)]
        self._month_spinner = Spinner(
            text=f'{now.month:02d}',
            values=months,
            font_size=dp(Size.SMALL),
            size_hint=(0.3, 1),
            background_color=t.INPUT_BG,
            color=t.TEXT,
        )
        self._month_spinner.bind(text=lambda w, v: self._on_month_spinner(v))

        reset_btn = Button(
            text='全部',
            font_size=dp(Size.SMALL),
            size_hint=(0.15, 1),
            background_color=(0.20, 0.66, 0.33, 1),
            background_normal='',
            color=(1, 1, 1, 1),
        )
        reset_btn.bind(on_release=lambda w: self._reset_filters())

        spinner_row.add_widget(self._year_spinner)
        spinner_row.add_widget(self._month_spinner)
        spinner_row.add_widget(reset_btn)
        filter_bar.add_widget(spinner_row)

        # 第二行：起止日期
        date_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(34),
            spacing=dp(4),
        )

        t_filter = get_theme()
        self._filter_start_input = TextInput(
            hint_text='开始日期',
            font_size=dp(10),
            size_hint=(0.3, 1),
            padding=(dp(4), dp(2)),
            readonly=True,
            background_color=t_filter.INPUT_BG,
            foreground_color=t_filter.TEXT,
            hint_text_color=t_filter.TEXT_SEC,
        )
        self._filter_start_input.bind(focus=lambda w, v: self._on_date_focus(w, v, 'start'))

        self._filter_end_input = TextInput(
            hint_text='结束日期',
            font_size=dp(10),
            size_hint=(0.3, 1),
            padding=(dp(4), dp(2)),
            readonly=True,
            background_color=t_filter.INPUT_BG,
            foreground_color=t_filter.TEXT,
            hint_text_color=t_filter.TEXT_SEC,
        )
        self._filter_end_input.bind(focus=lambda w, v: self._on_date_focus(w, v, 'end'))

        apply_btn = Button(
            text='筛选',
            font_size=dp(10),
            size_hint=(0.15, 1),
            background_color=(0.92, 0.26, 0.21, 1),
            background_normal='',
            color=(1, 1, 1, 1),
        )
        apply_btn.bind(on_release=lambda w: self._apply_custom_date())

        clear_btn = Button(
            text='清除',
            font_size=dp(10),
            size_hint=(0.15, 1),
            background_color=(0, 0, 0, 0),
            background_normal='',
            color=(0.10, 0.45, 0.91, 1),
        )
        clear_btn.bind(on_release=lambda w: self._clear_custom_date())

        date_row.add_widget(self._filter_start_input)
        date_row.add_widget(self._filter_end_input)
        date_row.add_widget(apply_btn)
        date_row.add_widget(clear_btn)
        filter_bar.add_widget(date_row)
        main.add_widget(filter_bar)

        # 主体列表
        self._scroll_list = ScrollList()
        main.add_widget(self._scroll_list)

        # 底部工具栏
        toolbar = BottomToolbar()
        self._build_toolbar(toolbar)
        main.add_widget(toolbar)

    def _build_toolbar(self, toolbar):
        toolbar.orientation = 'vertical'
        toolbar.height = dp(Size.TOOLBAR_H + 30)

        # 第一行：合计
        self._summary_label = Label(
            text='共 0 条 | 合计 ¥0.00',
            font_size=dp(Size.SMALL),
            size_hint_y=None,
            height=dp(24),
            halign='left',
            valign='middle',
        )
        Clock.schedule_once(
            lambda dt: setattr(self._summary_label, 'color', get_theme().GOLD), 0)
        toolbar.add_widget(self._summary_label)

        # 第二行：操作按钮
        btn_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(Size.BTN_H),
            spacing=dp(Size.SPACING_M),
        )

        add_btn = BtnPrimary(text='+ 新增', color_name='GREEN')
        add_btn.size_hint_x = 0.25
        add_btn.bind(on_release=lambda w: self.show_add_record())
        btn_row.add_widget(add_btn)

        stats_btn = BtnPrimary(text='📊 统计')
        stats_btn.size_hint_x = 0.25
        stats_btn.bind(on_release=lambda w: self.show_stats())
        btn_row.add_widget(stats_btn)

        export_btn = BtnPrimary(text='📄 导出')
        export_btn.size_hint_x = 0.25
        export_btn.bind(on_release=lambda w: self._export_all())
        btn_row.add_widget(export_btn)

        toolbar.add_widget(btn_row)

    def _update_info_bar_bg(self, *a):
        theme = get_theme()
        draw_bg(self._info_bar, theme.CARD)

    # ──────────────────────────────────────────
    # 筛选回调
    # ──────────────────────────────────────────

    def _on_year_spinner(self, val):
        self.filter_year = val
        self.filter_start = ''
        self.filter_end = ''
        self.refresh_list()

    def _on_month_spinner(self, val):
        self.filter_month = val
        self.filter_start = ''
        self.filter_end = ''
        self.refresh_list()

    def _reset_filters(self, *args):
        self.filter_year = '全部'
        self.filter_month = '全部'
        self.filter_start = ''
        self.filter_end = ''
        now = datetime.now()
        self._year_spinner.text = str(now.year)
        self._month_spinner.text = f'{now.month:02d}'
        self.refresh_list()

    def _apply_custom_date(self):
        start = self._filter_start_input.text.strip()
        end = self._filter_end_input.text.strip()
        if not start and not end:
            return
        self.filter_start = start
        self.filter_end = end
        self.filter_year = '全部'
        self.filter_month = '全部'
        self.refresh_list()

    def _clear_custom_date(self):
        self._filter_start_input.text = ''
        self._filter_end_input.text = ''
        self.filter_start = ''
        self.filter_end = ''
        self.refresh_list()

    # ──────────────────────────────────────────
    # 日期选择器
    # ──────────────────────────────────────────

    def _on_date_focus(self, widget, focused, which):
        if focused:
            self._show_date_picker(widget, which)

    def _show_date_picker(self, text_input, which):
        from kivy.uix.spinner import Spinner as Sp
        from kivy.uix.popup import Popup
        from widgets import BtnPrimary, draw_bg
        theme = get_theme()
        now = datetime.now()
        content = BoxLayout(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(12),
            size_hint=(None, None),
            size=(dp(260), dp(200)),
        )
        title_lbl = Label(
            text='选择日期',
            font_size=dp(Size.HEADING),
            bold=True,
            size_hint_y=None,
            height=dp(30),
            halign='center',
            color=theme.TEXT,
        )
        content.add_widget(title_lbl)
        spinner_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(8),
        )
        years = [str(y) for y in range(now.year - 10, now.year + 11)]
        year_sp = Sp(
            text=str(now.year),
            values=years,
            font_size=dp(Size.SMALL),
            size_hint_x=0.35,
            background_color=theme.INPUT_BG,
        )
        spinner_row.add_widget(year_sp)
        months = [f'{m:02d}' for m in range(1, 13)]
        month_sp = Sp(
            text=f'{now.month:02d}',
            values=months,
            font_size=dp(Size.SMALL),
            size_hint_x=0.3,
            background_color=theme.INPUT_BG,
        )
        spinner_row.add_widget(month_sp)
        days = [f'{d:02d}' for d in range(1, 32)]
        day_sp = Sp(
            text=f'{now.day:02d}',
            values=days,
            font_size=dp(Size.SMALL),
            size_hint_x=0.3,
            background_color=theme.INPUT_BG,
        )
        spinner_row.add_widget(day_sp)
        content.add_widget(spinner_row)
        ok_btn = BtnPrimary('确定')
        ok_btn.size_hint_y = None
        ok_btn.height = dp(40)
        content.add_widget(ok_btn)
        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(dp(280), dp(260)),
            background='',
            background_color=(0, 0, 0, 0),
            separator_color=(0, 0, 0, 0),
        )
        Clock.schedule_once(lambda dt: draw_bg(popup, theme.POPUP_BG, 12), 0)
        def on_confirm(w):
            selected = f'{year_sp.text}-{month_sp.text}-{day_sp.text}'
            text_input.text = selected
            popup.dismiss()
        ok_btn.bind(on_release=on_confirm)
        popup.open()

    # ──────────────────────────────────────────
    # 生命周期
    # ──────────────────────────────────────────

    def on_enter(self, *args):
        super().on_enter(*args)
        Clock.schedule_once(lambda dt: self.refresh_list(), 0)

    def load_customer(self, cid, name):
        self.customer_id = cid
        self.customer_name = name
        self.selected_ids.clear()
        self._customer_label.text = f'客户: {name}'

    def _go_back(self):
        self.manager.current = 'customer_list'

    # ──────────────────────────────────────────
    # 刷新列表
    # ──────────────────────────────────────────

    def refresh_list(self):
        self._scroll_list.clear()
        self.selected_ids.clear()

        if not self.customer_id:
            self._scroll_list.add_item(EmptyHint(text='请先选择客户'))
            self._update_summary(0, 0.0)
            return

        records = self._fetch_records()
        self._records = records

        if not records:
            self._scroll_list.add_item(EmptyHint(text='暂无记录'))
            self._update_summary(0, 0.0)
            return

        total_amount = sum(r['total_amount'] for r in records)

        # 表头行
        theme = get_theme()
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(30),
            spacing=dp(2),
            padding=(dp(34), dp(2), dp(4), dp(2)),
        )
        draw_bg(header, theme.CARD_ALT)
        for txt, width in [('序号', 0.1), ('日期', 0.25), ('机型', 0.25), ('数量', 0.15), ('金额', 0.2)]:
            header.add_widget(Label(
                text=txt, font_size=dp(Size.TINY), bold=True,
                size_hint_x=width, halign='center', color=theme.TEXT_SEC))
        self._scroll_list.add_item(header)

        for r in records:
            card = self._build_record_card(r)
            self._scroll_list.add_item(card)

        self._update_summary(len(records), total_amount)

    def _fetch_records(self):
        with get_db() as db:
            where_clauses = ['customer_id = ?']
            params = [self.customer_id]

            if self.filter_year and self.filter_year != '全部':
                where_clauses.append("strftime('%Y', date) = ?")
                params.append(self.filter_year)

            if self.filter_month and self.filter_month != '全部':
                where_clauses.append("strftime('%m', date) = ?")
                params.append(self.filter_month.zfill(2))

            if self.filter_start:
                where_clauses.append('date >= ?')
                params.append(self.filter_start)
            if self.filter_end:
                where_clauses.append('date <= ?')
                params.append(self.filter_end)

            sql = 'SELECT * FROM records WHERE ' + \
                ' AND '.join(where_clauses) + ' ORDER BY date DESC'
            rows = db.execute(sql, params).fetchall()
            return [dict(r) for r in rows]

    # ──────────────────────────────────────────
    # 构建记录行（表格式五列）
    # ──────────────────────────────────────────

    def _build_record_card(self, record):
        rid = record['id']
        theme = get_theme()
        idx = self._records.index(record) + 1

        # 卡片容器（可见背景）
        card = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(48),
            spacing=dp(2),
            padding=(dp(6), dp(2), dp(4), dp(2)),
        )
        draw_bg(card, theme.CARD, Size.CARD_RADIUS)

        # 左侧 CheckBox
        cb = CheckBox(size_hint_x=None, width=dp(32), size_hint_y=None, height=dp(40))
        cb.active = rid in self.selected_ids
        cb.bind(active=lambda w, val: self.toggle_select(rid, val))
        Clock.schedule_once(lambda dt: setattr(cb, 'color', theme.ACCENT), 0)
        card.add_widget(cb)

        # 五列表格（序号 日期 机型 数量 金额）
        cols_data = [
            (str(idx), 0.12, theme.TEXT_SEC),
            (record.get('date', ''), 0.25, theme.TEXT),
            (record.get('machine_type', ''), 0.28, theme.TEXT_SEC),
            (f"{record.get('total_hours', 0):.1f}h", 0.15, theme.ACCENT),
            (f"¥{record.get('total_amount', 0):.0f}", 0.2, theme.GOLD),
        ]

        for txt, width, color in cols_data:
            lbl = Label(
                text=txt,
                font_size=dp(Size.TINY),
                bold=True,
                size_hint_x=width,
                halign='center',
                valign='middle',
                color=color,
                shorten=True,
            )
            card.add_widget(lbl)

        # 点击行弹出详情（避开 CheckBox）
        card.bind(on_touch_down=lambda inst, touch: (
            self._show_record_detail(record)
            if inst.collide_point(*touch.pos) and not cb.collide_point(*touch.pos)
            else None
        ))

        return card

    def _show_record_detail(self, record):
        """弹出记录详情弹窗"""
        theme = get_theme()
        from kivy.uix.popup import Popup
        from kivy.uix.button import Button
        from kivy.uix.scrollview import ScrollView
        from widgets import draw_bg

        content = BoxLayout(orientation='vertical', spacing=dp(8), size_hint=(None, None))
        content.size = (dp(320), dp(420))

        # 标题
        title_lbl = Label(
            text='📋 记录详情',
            font_size=dp(Size.HEADING),
            bold=True,
            size_hint_y=None,
            height=dp(30),
            halign='center',
            color=theme.TEXT,
        )
        content.add_widget(title_lbl)

        # 详情字段
        fields = [
            ('项目名称', record.get('project_name', '')),
            ('日期', record.get('date', '')),
            ('机型', record.get('machine_type', '')),
            ('单价', f"¥{record.get('price', 0):.2f}/{record.get('unit', '')}"),
            ('上午', f"{record.get('am_start', '')} - {record.get('am_end', '')}"),
            ('下午', f"{record.get('pm_start', '')} - {record.get('pm_end', '')}"),
            ('加班', f"{record.get('ot_start', '')} - {record.get('ot_end', '')}"),
            ('合计时间', f"{record.get('total_hours', 0):.1f} h"),
            ('合计金额', f"¥{record.get('total_amount', 0):.2f}"),
            ('施工单位', record.get('construction_unit', '')),
            ('备注', record.get('remarks', '')),
            ('开票人', record.get('issuer', '')),
        ]

        scroll = ScrollView(size_hint=(1, 1))
        field_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(4),
            padding=(dp(8), 0),
        )
        field_container.bind(minimum_height=field_container.setter('height'))

        for label, val in fields:
            if not val:
                continue
            row_f = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(26), spacing=dp(8))
            lbl = Label(text=label, font_size=dp(Size.SMALL), bold=True,
                       size_hint_x=0.3, halign='right', color=theme.TEXT_SEC)
            val_lbl = Label(text=str(val), font_size=dp(Size.SMALL),
                          size_hint_x=0.7, halign='left', color=theme.TEXT)
            row_f.add_widget(lbl)
            row_f.add_widget(val_lbl)
            field_container.add_widget(row_f)

        scroll.add_widget(field_container)
        content.add_widget(scroll)

        # 底部按钮行
        rid = record['id']
        btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(10),
                           padding=(dp(8), dp(4)))

        edit_btn = Button(
            text='✏ 编辑',
            font_size=dp(Size.SMALL),
            bold=True,
            background_color=theme.ACCENT,
            background_normal='',
            color=(1, 1, 1, 1),
        )
        edit_btn.bind(on_release=lambda w: (popup.dismiss(), self.edit_record(rid)))

        del_btn = Button(
            text='🗑 删除',
            font_size=dp(Size.SMALL),
            bold=True,
            background_color=theme.RED,
            background_normal='',
            color=(1, 1, 1, 1),
        )
        del_btn.bind(on_release=lambda w: (popup.dismiss(), self.delete_record(rid)))

        cancel_btn = Button(
            text='关闭',
            font_size=dp(Size.SMALL),
            background_color=theme.CARD_ALT,
            background_normal='',
            color=theme.TEXT_SEC,
        )
        cancel_btn.bind(on_release=lambda w: popup.dismiss())

        btn_row.add_widget(edit_btn)
        btn_row.add_widget(del_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(dp(340), dp(460)),
            background='',
            background_color=(0, 0, 0, 0),
            separator_color=(0, 0, 0, 0),
        )
        from kivy.clock import Clock as _Clk
        _Clk.schedule_once(lambda dt: draw_bg(popup, theme.POPUP_BG, 14), 0)
        popup.open()

    # ──────────────────────────────────────────
    # 选中管理
    # ──────────────────────────────────────────

    def toggle_select(self, rid, val):
        if val:
            self.selected_ids.add(rid)
        else:
            self.selected_ids.discard(rid)

    def _update_summary(self, count, total_amount):
        self._summary_label.text = f'共 {count} 条 | 合计 ¥{total_amount:.2f}'

    # ──────────────────────────────────────────
    # 动作
    # ──────────────────────────────────────────

    def show_add_record(self):
        screen = self.manager.get_screen('record_form')
        screen.load_form(customer_id=self.customer_id,
                         customer_name=self.customer_name)
        self.manager.current = 'record_form'

    def show_stats(self):
        if self.manager.has_screen('statistics'):
            stats_screen = self.manager.get_screen('statistics')
            if hasattr(stats_screen, 'load_customer'):
                stats_screen.load_customer(
                    self.customer_id, self.customer_name)
            self.manager.current = 'statistics'
        else:
            self._show_toast('统计页面未实现')

    def edit_record(self, rid):
        screen = self.manager.get_screen('record_form')
        screen.load_form(rid)
        self.manager.current = 'record_form'

    def delete_record(self, rid):
        def do_delete():
            with get_db() as db:
                db.execute('DELETE FROM records WHERE id = ?', (rid,))
            self.selected_ids.discard(rid)
            self.refresh_list()

        ConfirmPopup.show(
            title='确认删除',
            message='确定要删除这条记录吗？此操作不可撤销。',
            confirm_text='删除',
            confirm_color='RED',
            on_confirm=do_delete,
        )

    def _export_all(self):
        """直接导出全部记录到打印预览页面"""
        if not self._records:
            self._show_toast('没有可导出的记录')
            return

        if self.manager.has_screen('print_preview'):
            pp = self.manager.get_screen('print_preview')
            if hasattr(pp, 'load_records'):
                pp.load_records(
                    self._records,
                    customer_name=self.customer_name,
                )
            self.manager.current = 'print_preview'
        else:
            self._show_toast('打印预览页面未实现')

    def _show_toast(self, msg):
        theme = get_theme()
        content = BoxLayout(padding=dp(20))
        lbl = Label(text=msg, font_size=dp(Size.SMALL),
                    halign='center')
        Clock.schedule_once(lambda dt: setattr(lbl, 'color', theme.TEXT), 0)
        content.add_widget(lbl)

        popup = Popup(
            title='',
            content=content,
            size_hint=(0.5, 0.2),
            background='',
            background_color=(0, 0, 0, 0),
            separator_color=(0, 0, 0, 0),
        )
        Clock.schedule_once(lambda dt: draw_bg(popup, theme.POPUP_BG, 8), 0)
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)
