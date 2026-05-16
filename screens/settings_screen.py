"""
settings_screen.py — 设置页面（v3.0 移动端风格）
卡片式分组设置项，主题切换/密码/数据管理
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.app import App
from datetime import datetime
import os
import json
import shutil

from config import get_theme, set_theme, Size, AppInfo, Database
from config import _get_password, _set_password, _get_password_path
from database import get_db
from widgets import Card, TopBar, BtnPrimary, BtnDanger, draw_bg


class SettingsScreen(Screen):
    """设置页面"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'
        self._build_ui()

    def _build_ui(self):
        theme = get_theme()
        draw_bg(self, theme.BG)

        root = BoxLayout(orientation='vertical', spacing=0)

        topbar = TopBar(
            title='⚙ 设置',
            on_back=lambda w: setattr(self.manager, 'current', 'customer_list'),
        )
        root.add_widget(topbar)

        scroll = ScrollView()
        content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(Size.SPACING_M),
            padding=(dp(Size.PAGE_PAD), dp(Size.SPACING_M),
                     dp(Size.PAGE_PAD), dp(Size.SPACING_XL)),
        )
        content.bind(minimum_height=content.setter('height'))
        scroll.add_widget(content)
        root.add_widget(scroll)

        # ══════════════════════════════════════
        # 1. 显示主题
        # ══════════════════════════════════════
        theme_card = Card()
        theme_card.add_widget(Label(
            text='🎨 显示主题',
            font_size=dp(Size.HEADING),
            bold=True,
            size_hint_y=None,
            height=dp(26),
            halign='left',
            color=theme.TEXT,
        ))

        # 自动跟随
        auto_btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(Size.BTN_H), spacing=dp(Size.SPACING_M))
        self._auto_btn = BtnPrimary(text='🔄 自动跟随系统', color_name='ACCENT')
        self._auto_btn.bind(on_release=lambda w: self.switch_theme('auto'))
        auto_btn_row.add_widget(self._auto_btn)
        theme_card.add_widget(auto_btn_row)

        # 深色/浅色
        btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(Size.BTN_H), spacing=dp(Size.SPACING_M))
        self._dark_btn = BtnPrimary(text='🌙 深色模式')
        self._dark_btn.bind(on_release=lambda w: self.switch_theme('dark'))
        btn_row.add_widget(self._dark_btn)
        self._light_btn = BtnPrimary(text='☀️ 浅色模式')
        self._light_btn.bind(on_release=lambda w: self.switch_theme('light'))
        btn_row.add_widget(self._light_btn)
        theme_card.add_widget(btn_row)
        content.add_widget(theme_card)

        # ══════════════════════════════════════
        # 2. 登录密码
        # ══════════════════════════════════════
        pw_card = Card()
        pw_card.add_widget(Label(
            text='🔑 登录密码',
            font_size=dp(Size.HEADING),
            bold=True,
            size_hint_y=None,
            height=dp(26),
            halign='left',
            color=theme.TEXT,
        ))
        pw_btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(Size.BTN_H), spacing=dp(Size.SPACING_M))

        set_pw_btn = BtnPrimary(text='🔑 修改密码')
        set_pw_btn.bind(on_release=self.show_set_password)
        pw_btn_row.add_widget(set_pw_btn)

        clear_pw_btn = BtnDanger(text='🔓 清除密码')
        clear_pw_btn.bind(on_release=self.show_clear_password)
        pw_btn_row.add_widget(clear_pw_btn)

        pw_card.add_widget(pw_btn_row)
        content.add_widget(pw_card)

        # ══════════════════════════════════════
        # 3. 数据管理
        # ══════════════════════════════════════
        data_card = Card()
        data_card.add_widget(Label(
            text='💾 数据管理',
            font_size=dp(Size.HEADING),
            bold=True,
            size_hint_y=None,
            height=dp(26),
            halign='left',
            color=theme.TEXT,
        ))
        data_btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(Size.BTN_H), spacing=dp(Size.SPACING_M))

        backup_btn = BtnPrimary(text='💾 备份数据', color_name='GREEN')
        backup_btn.bind(on_release=self.show_backup)
        data_btn_row.add_widget(backup_btn)

        restore_btn = BtnPrimary(text='📂 恢复数据', color_name='ACCENT')
        restore_btn.bind(on_release=self.show_restore)
        data_btn_row.add_widget(restore_btn)

        data_card.add_widget(data_btn_row)
        content.add_widget(data_card)

        # ══════════════════════════════════════
        # 4. 关于
        # ══════════════════════════════════════
        about_card = Card()
        about_card.add_widget(Label(
            text=f'{AppInfo.NAME} v{AppInfo.VERSION}',
            font_size=dp(Size.BODY),
            bold=True,
            size_hint_y=None,
            height=dp(24),
            halign='left',
            color=theme.TEXT,
        ))
        about_card.add_widget(Label(
            text='技术支持：请联系开发者',
            font_size=dp(Size.SMALL),
            size_hint_y=None,
            height=dp(20),
            halign='left',
            color=theme.TEXT_SEC,
        ))
        content.add_widget(about_card)

        content.add_widget(Widget(size_hint_y=None, height=dp(20)))

        self.add_widget(root)

    def _show_msg(self, msg):
        theme = get_theme()
        popup = Popup(
            title='提示',
            size_hint=(0.7, 0.2),
            background='',
            background_color=(0, 0, 0, 0),
            separator_color=(0, 0, 0, 0),
        )
        Clock.schedule_once(lambda dt: draw_bg(popup, theme.POPUP_BG, 12), 0)
        lbl = Label(
            text=msg,
            font_size=dp(Size.BODY),
            color=theme.TEXT,
            halign='center',
        )
        popup.add_widget(lbl)
        popup.open()

    def _rebuild_app(self):
        app = App.get_running_app()
        if not app or not hasattr(app, 'root'):
            return
        old_sm = app.root
        old_current = old_sm.current
        from kivy.uix.screenmanager import ScreenManager, SlideTransition
        sm = ScreenManager(transition=SlideTransition())
        from screens.customer_screen import CustomerListScreen
        from screens.record_list_screen import RecordListScreen
        from screens.record_form_screen import RecordFormScreen
        from screens.statistics_screen import StatisticsScreen
        from screens.print_preview_screen import PrintPreviewScreen
        from screens.login_screen import LoginScreen
        from screens.settings_screen import SettingsScreen

        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(CustomerListScreen(name='customer_list'))
        sm.add_widget(RecordListScreen(name='record_list'))
        sm.add_widget(RecordFormScreen(name='record_form'))
        sm.add_widget(StatisticsScreen(name='statistics'))
        sm.add_widget(PrintPreviewScreen(name='print_preview'))
        sm.add_widget(SettingsScreen(name='settings'))
        for s in sm.screens:
            s.app_ref = app
        from kivy.core.window import Window
        Window.bind(on_keyboard=app._on_keyboard)
        target = old_current if old_current != 'settings' else 'customer_list'
        if sm.has_screen(target):
            sm.current = target
        app.root = sm

    def switch_theme(self, mode):
        from config import _current_theme, set_auto_theme, is_auto_theme

        if mode == 'auto':
            set_auto_theme(True)
            try:
                app = App.get_running_app()
                if hasattr(app, '_detect_system_theme'):
                    system_theme = app._detect_system_theme()
                    mode = system_theme
            except Exception as e:
                print(f"自动主题检测失败：{e}")
        else:
            set_auto_theme(False)

        from config_theme import set_theme as ct_set_theme, get_theme as ct_get_theme
        ct_set_theme(mode)
        import config
        config._current_theme = mode

        try:
            pref_path = os.path.join(Database.STORAGE_ROOT, '.theme_pref.json')
            os.makedirs(os.path.dirname(pref_path), exist_ok=True)
            with open(pref_path, 'w', encoding='utf-8') as f:
                json.dump({'theme': mode, 'auto': is_auto_theme()}, f)
        except Exception:
            pass

        from kivy.core.window import Window
        theme = ct_get_theme()
        Window.clearcolor = theme.BG

        try:
            app = App.get_running_app()
            if app and app.root:
                self._refresh_widget_colors(app.root)
        except Exception as e:
            print(f"刷新颜色失败：{e}")

    def _refresh_widget_colors(self, widget):
        from config_theme import get_theme
        theme = get_theme()
        cls_name = type(widget).__name__

        if cls_name == 'TopBar':
            from kivy.graphics import Color, Rectangle
            widget.canvas.before.clear()
            bg_col = Color(*theme.HEADER_BG)
            widget.canvas.before.add(bg_col)
            bg_rect = Rectangle(size=widget.size, pos=widget.pos)
            widget.canvas.before.add(bg_rect)
            widget._bg_rect = bg_rect
            widget.bind(size=lambda w, *a: setattr(w._bg_rect, 'size', w.size),
                        pos=lambda w, *a: setattr(w._bg_rect, 'pos', w.pos))
            for child in widget.children:
                if hasattr(child, 'color'):
                    child.color = (1, 1, 1, 1)
                if hasattr(child, 'background_color'):
                    child.background_color = theme.HEADER_BG
                    child.background_normal = ''
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: (
                setattr(widget._bg_rect, 'size', widget.size),
                setattr(widget._bg_rect, 'pos', widget.pos)
            ) if hasattr(widget, '_bg_rect') else None, 0)
            return

        if cls_name == 'BottomToolbar':
            from kivy.graphics import Color, Rectangle
            widget.canvas.before.clear()
            col = Color(*theme.TOOLBAR_BG)
            widget.canvas.before.add(col)
            rect = Rectangle(size=widget.size, pos=widget.pos)
            widget.canvas.before.add(rect)
            widget._bg_rect = rect
            widget.bind(size=lambda w, *a: setattr(w._bg_rect, 'size', w.size),
                        pos=lambda w, *a: setattr(w._bg_rect, 'pos', w.pos))

        if hasattr(widget, 'color') and hasattr(widget, 'text'):
            if cls_name not in ('TopBar',):
                widget.color = theme.TEXT
        if hasattr(widget, 'foreground_color'):
            widget.foreground_color = theme.TEXT
        if hasattr(widget, 'hint_text_color'):
            widget.hint_text_color = theme.TEXT_DIM

        if cls_name in ('BtnPrimary', 'BtnDanger'):
            if cls_name == 'BtnPrimary':
                cname = getattr(widget, '_color_name', 'ACCENT')
                widget.background_color = getattr(theme, cname, theme.ACCENT)
            else:
                widget.background_color = theme.RED
            widget.color = (1, 1, 1, 1)

        if hasattr(widget, 'children'):
            for child in widget.children[:]:
                self._refresh_widget_colors(child)

    def show_set_password(self, *args):
        theme = get_theme()
        content = BoxLayout(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(10),
        )

        t = get_theme()
        old_input = TextInput(
            password=True,
            hint_text='当前密码',
            multiline=False,
            font_size=dp(Size.SMALL),
            size_hint_y=None,
            height=dp(Size.INPUT_H),
            padding=(dp(12), dp(10)),
            background_color=t.INPUT_BG,
            foreground_color=t.TEXT,
            hint_text_color=t.TEXT_SEC,
        )
        content.add_widget(old_input)

        new_input = TextInput(
            password=True,
            hint_text='新密码',
            multiline=False,
            font_size=dp(Size.SMALL),
            size_hint_y=None,
            height=dp(Size.INPUT_H),
            padding=(dp(12), dp(10)),
            background_color=t.INPUT_BG,
            foreground_color=t.TEXT,
            hint_text_color=t.TEXT_SEC,
        )
        content.add_widget(new_input)

        confirm_input = TextInput(
            password=True,
            hint_text='确认新密码',
            multiline=False,
            font_size=dp(Size.SMALL),
            size_hint_y=None,
            height=dp(Size.INPUT_H),
            padding=(dp(12), dp(10)),
            background_color=t.INPUT_BG,
            foreground_color=t.TEXT,
            hint_text_color=t.TEXT_SEC,
        )
        content.add_widget(confirm_input)

        btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(Size.BTN_H), spacing=dp(10))

        cancel_btn = Button(text='取消', font_size=dp(Size.SMALL), background_color=theme.CARD_ALT,
                           background_normal='', color=theme.TEXT_SEC)
        ok_btn = BtnPrimary(text='确认修改', color_name='GREEN')

        def do_change(*args):
            old_pw = old_input.text.strip()
            new_pw = new_input.text.strip()
            confirm_pw = confirm_input.text.strip()

            try:
                if _get_password() != old_pw:
                    self._show_msg('当前密码错误')
                    return
            except NameError:
                self._show_msg('无法读取密码，请重启应用')
                return

            if len(new_pw) < 4:
                self._show_msg('新密码至少 4 位')
                return
            if new_pw != confirm_pw:
                self._show_msg('两次输入的密码不一致')
                return

            try:
                _set_password(new_pw)
            except NameError:
                self._show_msg('密码修改失败')
                return

            popup.dismiss()
            success_popup = Popup(
                title='成功',
                size_hint=(0.7, 0.2),
                background='',
                background_color=(0, 0, 0, 0),
                separator_color=(0, 0, 0, 0),
            )
            Clock.schedule_once(lambda dt: draw_bg(success_popup, theme.POPUP_BG, 12), 0)
            success_popup.add_widget(Label(
                text='密码已修改',
                font_size=dp(Size.BODY),
                color=theme.GREEN,
                halign='center',
            ))
            success_popup.open()

        cancel_btn.bind(on_release=lambda w: popup.dismiss())
        ok_btn.bind(on_release=do_change)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(ok_btn)
        content.add_widget(btn_row)

        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(dp(300), dp(300)),
            background='',
            background_color=(0, 0, 0, 0),
            separator_color=(0, 0, 0, 0),
        )
        Clock.schedule_once(lambda dt: draw_bg(popup, theme.POPUP_BG, 12), 0)
        popup.open()

    def show_clear_password(self, *args):
        theme = get_theme()
        content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        msg = Label(
            text='确定要清除密码吗？\n清除后下次启动无需密码。',
            font_size=dp(Size.SMALL),
            halign='center',
            size_hint_y=None,
            height=dp(50),
        )
        msg.bind(size=lambda w, *a: setattr(w, 'text_size', (w.width - 20, None)))
        content.add_widget(msg)

        btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(Size.BTN_H), spacing=dp(10))
        cancel_btn = Button(text='取消', font_size=dp(Size.SMALL), background_color=theme.CARD_ALT,
                           background_normal='', color=theme.TEXT_SEC)
        ok_btn = BtnDanger(text='清除密码')

        def do_clear(*args):
            try:
                pw_path = _get_password_path()
                if os.path.exists(pw_path):
                    os.remove(pw_path)
                popup.dismiss()
                self._show_msg('密码已清除')
            except Exception as e:
                popup.dismiss()
                self._show_msg(f'清除失败: {str(e)}')

        cancel_btn.bind(on_release=lambda w: popup.dismiss())
        ok_btn.bind(on_release=do_clear)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(ok_btn)
        content.add_widget(btn_row)

        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(dp(280), dp(200)),
            background='',
            background_color=(0, 0, 0, 0),
            separator_color=(0, 0, 0, 0),
        )
        Clock.schedule_once(lambda dt: draw_bg(popup, theme.POPUP_BG, 12), 0)
        popup.open()

    def show_backup(self, *args):
        try:
            backup_dir = AppInfo.get_backup_dir()
            os.makedirs(backup_dir, exist_ok=True)
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f'机械施工记账_备份_{ts}.db'
            dest = os.path.join(backup_dir, backup_name)
            shutil.copy2(Database.DB_PATH, dest)
            self._show_msg(f'✅ 备份成功！\n{backup_name}')
        except Exception as e:
            self._show_msg(f'❌ 备份失败: {str(e)}')

    def show_restore(self, *args):
        """显示恢复数据选择弹窗"""
        try:
            backup_dir = AppInfo.get_backup_dir()
            if not os.path.exists(backup_dir):
                self._show_msg('没有找到备份文件')
                return
            backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.db')], reverse=True)
            if not backups:
                self._show_msg('没有找到备份文件')
                return

            theme = get_theme()
            content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
            title = Label(text='选择要恢复的备份', font_size=dp(Size.HEADING), bold=True,
                         size_hint_y=None, height=dp(30), halign='center', color=theme.TEXT)
            content.add_widget(title)

            backup_sp = Spinner(
                text=backups[0],
                values=backups,
                font_size=dp(Size.SMALL),
                size_hint_y=None,
                height=dp(40),
                background_color=theme.INPUT_BG,
            )
            content.add_widget(backup_sp)

            btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(Size.BTN_H), spacing=dp(10))
            cancel_btn = Button(text='取消', font_size=dp(Size.SMALL), background_color=theme.CARD_ALT,
                               background_normal='', color=theme.TEXT_SEC)
            ok_btn = BtnPrimary(text='恢复数据', color_name='GREEN')

            def do_restore(*args):
                selected = backup_sp.text
                src = os.path.join(backup_dir, selected)
                try:
                    shutil.copy2(src, Database.DB_PATH)
                    popup.dismiss()
                    self._show_msg('✅ 数据已恢复！请重启应用。')
                except Exception as e:
                    popup.dismiss()
                    self._show_msg(f'❌ 恢复失败: {str(e)}')

            cancel_btn.bind(on_release=lambda w: popup.dismiss())
            ok_btn.bind(on_release=do_restore)
            btn_row.add_widget(cancel_btn)
            btn_row.add_widget(ok_btn)
            content.add_widget(btn_row)

            popup = Popup(
                title='',
                content=content,
                size_hint=(None, None),
                size=(dp(320), dp(240)),
                background='',
                background_color=(0, 0, 0, 0),
                separator_color=(0, 0, 0, 0),
            )
            Clock.schedule_once(lambda dt: draw_bg(popup, theme.POPUP_BG, 12), 0)
            popup.open()

        except Exception as e:
            self._show_msg(f'❌ 读取备份失败: {str(e)}')
