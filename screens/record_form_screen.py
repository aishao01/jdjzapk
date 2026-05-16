"""
record_form_screen.py — 记录表单页面（v3.2 紧凑一页版）
标签放入输入框内，填写后自动隐藏，一页显示全
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.clock import Clock
from datetime import datetime
from config import get_theme, Size
from database import get_db
from widgets import TopBar, BtnPrimary, draw_bg


def _get_time_options():
    options = ['']
    h = 0
    while h < 24:
        for m in ('00', '30'):
            options.append(f'{h:02d}:{m}')
        h += 1
    return options


def _parse_time(t_str):
    if not t_str or not t_str.strip():
        return 0
    try:
        parts = t_str.strip().split(':')
        return int(parts[0]) * 60 + int(parts[1])
    except (ValueError, IndexError):
        return 0


class InlineField(BoxLayout):
    """紧凑输入框（无标签，hint_text 做标签，填写后自动消失）"""
    def __init__(self, hint='', value='', readonly=False, input_type='text', **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=dp(44), **kwargs)
        t = get_theme()
        self._input = TextInput(
            text=value,
            hint_text=hint,
            font_size=dp(15),
            size_hint_x=1,
            size_hint_y=None,
            height=dp(40),
            padding=(dp(12), dp(8)),
            readonly=readonly,
            multiline=False,
            input_type=input_type,
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


class InlineSpinner(BoxLayout):
    """紧凑下拉（无标签，hint 在值中体现）"""
    def __init__(self, values=None, text='', **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=dp(44), **kwargs)
        t = get_theme()
        self._spinner = Spinner(
            text=text or (values[0] if values else ''),
            values=values or (),
            font_size=dp(15),
            size_hint_x=1,
            size_hint_y=None,
            height=dp(40),
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


class RecordFormScreen(Screen):
    """记录表单页面（紧凑一页版，标签在框内）"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'record_form'
        self.app_ref = None
        self._customer_id = 0
        self._customer_name = ''
        self._editing_rid = None
        self._fields = {}
        self._date_range_box = None
        self._time_fields_box = None
        self._time_section = None
        self._custom_unit_box = None  # 自定义单位输入框
        self._custom_units = set()  # 已添加的自定义单位
        self._unit_values = ['小时', '台/班', '包月', '次', '天']  # 初始单位列表
        self._build_ui()

    def _build_ui(self):
        main = BoxLayout(orientation='vertical', spacing=0)
        self.add_widget(main)

        # 顶部导航（返回按钮红色）
        top = TopBar(title='记录表单', on_back=lambda w: self._go_back(), back_color=(0.92, 0.26, 0.21, 1))
        main.add_widget(top)

        # 表单主体（紧凑靠顶部，不用滚动）
        form = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(4),
            padding=(dp(10), dp(4), dp(10), dp(4)),
        )
        form.bind(minimum_height=form.setter('height'))
        main.add_widget(form)

        # ── 第1行：项目名称 ──
        f = InlineField(hint='项目名称')
        self._fields['project_name'] = f
        f._input.bind(focus=self._on_project_name_blur)
        form.add_widget(f)

        # ── 第2行：日期 + 单位 ──
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(44), spacing=dp(6))
        f = InlineField(hint='选择日期')
        f._input.bind(focus=self._on_date_focus)
        self._fields['date'] = f
        row.add_widget(f)
        f = InlineSpinner(values=self._unit_values + ['自定义'], text='小时')
        self._fields['unit'] = f
        f._spinner.bind(text=self._on_unit_changed)
        row.add_widget(f)
        form.add_widget(row)

        # ── 自定义单位输入行（选择自定义时显示）──
        custom_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(44), spacing=dp(6))
        self._custom_unit_box = custom_row
        custom_row.opacity = 0
        custom_row.disabled = True
        custom_input = InlineField(hint='输入自定义单位，按确定添加')
        self._fields['custom_unit'] = custom_input
        custom_input._input.bind(
            on_text_validate=lambda w: self._on_custom_unit_confirm(w))
        custom_row.add_widget(custom_input)
        form.add_widget(custom_row)

        # ── 第3行：机型 + 单价 ──
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(44), spacing=dp(6))
        f = InlineField(hint='机型/产品')
        self._fields['machine_type'] = f
        row.add_widget(f)
        f = InlineField(hint='单价(元)', input_type='number')
        self._fields['price'] = f
        row.add_widget(f)
        form.add_widget(row)

        # ── 日期范围（天单位时显示）──
        date_range_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(44), spacing=dp(6))
        self._date_range_box = date_range_box
        date_range_box.opacity = 0
        date_range_box.disabled = True
        f_start = InlineField(hint='开始日期')
        f_start._input.bind(focus=lambda w, v: self._on_date_range_focus(w, 'start'))
        self._fields['date_range_start'] = f_start
        f_end = InlineField(hint='结束日期')
        f_end._input.bind(focus=lambda w, v: self._on_date_range_focus(w, 'end'))
        self._fields['date_range_end'] = f_end
        date_range_box.add_widget(f_start)
        date_range_box.add_widget(f_end)
        form.add_widget(date_range_box)

        # ── 时间区域（小时/台班时显示）──
        time_section = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(4))
        self._time_section = time_section
        self._time_fields_box = time_section

        # 上午
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(6))
        lbl = Label(text='上午', font_size=dp(14), bold=True, size_hint_x=None, width=dp(44), halign='left')
        # Override color per theme
        Clock.schedule_once(lambda dt, l=lbl: setattr(l, 'color', get_theme().TEXT), 0)
        row.add_widget(lbl)
        f = InlineSpinner(values=_get_time_options(), text='07:00')
        self._fields['am_start'] = f
        f._spinner.bind(text=lambda w, v: self.calc_totals())
        row.add_widget(f)
        f = InlineSpinner(values=_get_time_options(), text='11:00')
        self._fields['am_end'] = f
        f._spinner.bind(text=lambda w, v: self.calc_totals())
        row.add_widget(f)
        time_section.add_widget(row)

        # 下午
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(6))
        lbl = Label(text='下午', font_size=dp(14), bold=True, size_hint_x=None, width=dp(44), halign='left')
        Clock.schedule_once(lambda dt, l=lbl: setattr(l, 'color', get_theme().TEXT), 0)
        row.add_widget(lbl)
        f = InlineSpinner(values=_get_time_options(), text='13:00')
        self._fields['pm_start'] = f
        f._spinner.bind(text=lambda w, v: self.calc_totals())
        row.add_widget(f)
        f = InlineSpinner(values=_get_time_options(), text='17:00')
        self._fields['pm_end'] = f
        f._spinner.bind(text=lambda w, v: self.calc_totals())
        row.add_widget(f)
        time_section.add_widget(row)

        # 加班
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(6))
        lbl = Label(text='加班', font_size=dp(14), bold=True, size_hint_x=None, width=dp(44), halign='left')
        Clock.schedule_once(lambda dt, l=lbl: setattr(l, 'color', get_theme().TEXT), 0)
        row.add_widget(lbl)
        f = InlineSpinner(values=_get_time_options(), text='')
        self._fields['ot_start'] = f
        f._spinner.bind(text=lambda w, v: self.calc_totals())
        row.add_widget(f)
        f = InlineSpinner(values=_get_time_options(), text='')
        self._fields['ot_end'] = f
        f._spinner.bind(text=lambda w, v: self.calc_totals())
        row.add_widget(f)
        time_section.add_widget(row)

        form.add_widget(time_section)

        # ── 合计行 ──
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(44), spacing=dp(6))
        f = InlineField(hint='合计时间(h)', readonly=True)
        self._fields['total_hours'] = f
        row.add_widget(f)
        f = InlineField(hint='合计金额(元)', readonly=True)
        self._fields['total_amount'] = f
        row.add_widget(f)
        form.add_widget(row)

        # ── 施工单位 ──
        f = InlineField(hint='施工单位')
        self._fields['construction_unit'] = f
        form.add_widget(f)

        # ── 备注 ──
        f = InlineField(hint='备注')
        self._fields['remarks'] = f
        form.add_widget(f)

        # ── 开票人 ──
        f = InlineField(hint='开票人')
        self._fields['issuer'] = f
        form.add_widget(f)

        # 底部保存按钮（固定在底部）
        main.add_widget(BoxLayout(size_hint_y=1))  # 弹性空间撑到底部

        # 底部固定保存按钮
        bottom = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(52),
            padding=(dp(10), dp(4)),
        )
        save_btn = BtnPrimary('💾 保存记录', color_name='GREEN', size_hint_x=1)
        save_btn.bind(on_release=lambda w: self.save_record())
        bottom.add_widget(save_btn)
        main.add_widget(bottom)

        # 默认单位联动
        Clock.schedule_once(lambda dt: self._on_unit_changed(None, '小时'), 0)

    def _go_back(self):
        if self.manager and self.manager.has_screen('record_list'):
            self.manager.current = 'record_list'

    def _on_unit_changed(self, spinner, text):
        unit = text

        # 自定义单位处理
        if unit == '自定义':
            if self._custom_unit_box:
                self._custom_unit_box.opacity = 1
                self._custom_unit_box.disabled = False
                Clock.schedule_once(lambda dt: self._fields['custom_unit']._input.focus
                                    if self._fields.get('custom_unit') else None, 0.1)
            time_visible = False
            show_range = False
            amount_editable = True  # 自定义单位时手动填写数量
        else:
            if self._custom_unit_box:
                self._custom_unit_box.opacity = 0
                self._custom_unit_box.disabled = True
            time_visible = unit in ('小时', '台/班')
            show_range = (unit == '天')
            amount_editable = unit in ('包月', '次', '天')

        if self._time_section:
            self._time_section.opacity = 1 if time_visible else 0
            self._time_section.disabled = not time_visible

        if self._date_range_box:
            self._date_range_box.opacity = 1 if show_range else 0
            self._date_range_box.disabled = not show_range

        if 'total_amount' in self._fields:
            self._fields['total_amount']._input.readonly = not amount_editable
            self._fields['total_amount']._input.hint_text = '输入数量' if amount_editable else '自动计算(元)'
            if not amount_editable:
                self._fields['total_amount'].text = ''

        if 'price' in self._fields:
            try:
                self._fields['price']._input.unbind(on_text=self.calc_totals)
            except:
                pass
            self._fields['price']._input.bind(text=self.calc_totals)

        if amount_editable:
            try:
                self._fields['total_amount']._input.unbind(on_text=self.calc_totals)
            except:
                pass
            self._fields['total_amount']._input.bind(text=self.calc_totals)
        else:
            self.calc_totals()

    def _on_custom_unit_confirm(self, text_input):
        """用户输入自定义单位后确认"""
        unit = text_input.text.strip()
        if not unit:
            return
        if unit == '自定义':
            text_input.text = ''
            return
        # 添加到已保存的自定义单位列表
        if unit not in self._custom_units:
            self._custom_units.add(unit)
            # 更新 Spinner 的 values（在 '自定义' 前插入）
            values = self._unit_values + list(self._custom_units) + ['自定义']
            self._fields['unit']._spinner.values = values
        # 选中输入的单位
        self._fields['unit']._spinner.text = unit
        text_input.text = ''
        # 隐藏自定义输入框
        if self._custom_unit_box:
            self._custom_unit_box.opacity = 0
            self._custom_unit_box.disabled = True

    def calc_totals(self, *args):
        try:
            am_s = _parse_time(self._fields.get('am_start', {}).text or '00:00')
            am_e = _parse_time(self._fields.get('am_end', {}).text or '00:00')
            pm_s = _parse_time(self._fields.get('pm_start', {}).text or '00:00')
            pm_e = _parse_time(self._fields.get('pm_end', {}).text or '00:00')
            ot_s = _parse_time(self._fields.get('ot_start', {}).text or '00:00')
            ot_e = _parse_time(self._fields.get('ot_end', {}).text or '00:00')

            total_min = max(0, am_e - am_s) + max(0, pm_e - pm_s) + max(0, ot_e - ot_s)
            total_hours = total_min / 60.0

            self._fields['total_hours'].text = f'{total_hours:.1f}'

            unit = self._fields['unit'].text
            amount_editable = unit in ('包月', '次', '天')

            if amount_editable and not self._fields['total_amount']._input.readonly:
                return

            try:
                price = float(self._fields['price'].text or 0)
            except:
                price = 0

            if unit in ('小时', 'h'):
                amount = total_hours * price
            elif unit == '台/班':
                amount = (total_hours / 8.0) * price if total_hours else 0
            elif unit == '包月':
                try:
                    count = float(self._fields['total_amount'].text or 0)
                    amount = count * price
                except:
                    amount = 0
            elif unit == '次':
                try:
                    count = float(self._fields['total_amount'].text or 0)
                    amount = count * price
                except:
                    amount = 0
            elif unit == '天':
                if self._fields.get('date_range_start') and self._fields.get('date_range_end'):
                    try:
                        d1 = datetime.strptime(self._fields['date_range_start'].text[:10], '%Y-%m-%d')
                        d2 = datetime.strptime(self._fields['date_range_end'].text[:10], '%Y-%m-%d')
                        days = max(1, (d2 - d1).days + 1)
                    except:
                        days = 1
                    amount = days * price
                else:
                    amount = price
            else:
                amount = total_hours * price

            self._fields['total_amount'].text = f'{amount:.2f}'
        except Exception as e:
            print(f'计算错误：{e}')

    def _on_project_name_blur(self, instance, focus):
        if not focus and instance.text:
            self._cache_project_name(instance.text)

    def _cache_project_name(self, name):
        try:
            with get_db() as db:
                db.execute(
                    'INSERT OR IGNORE INTO project_cache (name) VALUES (?)',
                    (name,)
                )
        except:
            pass

    def _on_date_focus(self, instance, focus):
        if focus:
            self._show_date_picker(self._fields['date'])

    def _on_date_range_focus(self, instance, field):
        if field == 'start':
            self._show_date_picker(self._fields['date_range_start'])
        else:
            self._show_date_picker(self._fields['date_range_end'])

    def _show_date_picker(self, field):
        from kivy.uix.popup import Popup
        from kivy.uix.button import Button
        from kivy.uix.spinner import Spinner as Sp
        from widgets import BtnPrimary
        theme = get_theme()
        now = datetime.now()

        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        content.size_hint = (None, None)
        content.size = (dp(280), dp(200))

        spinner_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            spacing=dp(8),
        )
        years = [str(y) for y in range(now.year - 10, now.year + 11)]
        year_sp = Sp(text=str(now.year), values=years, font_size=dp(15), size_hint_x=0.35,
                     background_color=theme.INPUT_BG)
        months = [f'{m:02d}' for m in range(1, 13)]
        month_sp = Sp(text=f'{now.month:02d}', values=months, font_size=dp(15), size_hint_x=0.3,
                      background_color=theme.INPUT_BG)
        days = [f'{d:02d}' for d in range(1, 32)]
        day_sp = Sp(text=f'{now.day:02d}', values=days, font_size=dp(15), size_hint_x=0.3,
                    background_color=theme.INPUT_BG)
        spinner_row.add_widget(year_sp)
        spinner_row.add_widget(month_sp)
        spinner_row.add_widget(day_sp)
        content.add_widget(spinner_row)

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        cancel_btn = Button(text='取消', font_size=dp(15), background_color=theme.CARD_ALT,
                            background_normal='', color=theme.TEXT_SEC)
        ok_btn = BtnPrimary('确定')
        ok_btn.size_hint_y = None
        ok_btn.height = dp(44)

        def do_select(*a):
            field.text = f'{year_sp.text}-{month_sp.text}-{day_sp.text}'
            popup.dismiss()

        cancel_btn.bind(on_release=lambda w: popup.dismiss())
        ok_btn.bind(on_release=do_select)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(ok_btn)
        content.add_widget(btn_row)

        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(dp(300), dp(260)),
            background='',
            background_color=(0, 0, 0, 0),
            separator_color=(0, 0, 0, 0),
        )
        Clock.schedule_once(lambda dt: draw_bg(popup, theme.POPUP_BG, 14), 0)
        popup.open()

    def load_form(self, record_id=None, customer_id=0, customer_name=''):
        self._editing_rid = record_id
        if record_id:
            with get_db() as db:
                row = db.execute(
                    'SELECT * FROM records WHERE id = ?', (record_id,)
                ).fetchone()
                if row:
                    self._customer_id = row['customer_id']
                    for key in self._fields:
                        self._fields[key].text = str(row.get(key, '') or '')
                    self._on_unit_changed(None, self._fields['unit'].text)
        else:
            self._customer_id = customer_id
            self._customer_name = customer_name
            for key in self._fields:
                self._fields[key].text = ''
            self._fields['unit'].text = '小时'
            self._fields['am_start'].text = '07:00'
            self._fields['am_end'].text = '11:00'
            self._fields['pm_start'].text = '13:00'
            self._fields['pm_end'].text = '17:00'
            self._on_unit_changed(None, '小时')

    def save_record(self, *args):
        try:
            data = {}
            for key in self._fields:
                if key == 'custom_unit':
                    continue  # 跳过自定义单位输入字段
                if key in ('total_hours', 'total_amount', 'price'):
                    try:
                        data[key] = float(self._fields[key].text or 0)
                    except:
                        data[key] = 0.0
                else:
                    data[key] = self._fields[key].text

            data['customer_id'] = self._customer_id

            if self._editing_rid:
                with get_db() as db:
                    db.execute('''
                        UPDATE records SET
                            project_name=?, date=?, machine_type=?, price=?, unit=?,
                            am_start=?, am_end=?, pm_start=?, pm_end=?,
                            ot_start=?, ot_end=?, total_hours=?, total_amount=?,
                            date_range_start=?, date_range_end=?,
                            construction_unit=?, remarks=?, issuer=?
                        WHERE id=?
                    ''', (
                        data['project_name'], data['date'], data['machine_type'],
                        data['price'], data['unit'],
                        data['am_start'], data['am_end'],
                        data['pm_start'], data['pm_end'],
                        data['ot_start'], data['ot_end'],
                        data['total_hours'], data['total_amount'],
                        data['date_range_start'], data['date_range_end'],
                        data['construction_unit'], data['remarks'], data['issuer'],
                        self._editing_rid,
                    ))
            else:
                with get_db() as db:
                    db.execute('''
                        INSERT INTO records (
                            customer_id, project_name, date, machine_type,
                            price, unit, am_start, am_end,
                            pm_start, pm_end, ot_start, ot_end,
                            total_hours, total_amount,
                            date_range_start, date_range_end,
                            construction_unit, remarks, issuer
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        data['customer_id'], data['project_name'], data['date'],
                        data['machine_type'], data['price'], data['unit'],
                        data['am_start'], data['am_end'],
                        data['pm_start'], data['pm_end'],
                        data['ot_start'], data['ot_end'],
                        data['total_hours'], data['total_amount'],
                        data['date_range_start'], data['date_range_end'],
                        data['construction_unit'], data['remarks'], data['issuer'],
                    ))

            self._go_back()
        except Exception as e:
            print(f'保存失败：{e}')
