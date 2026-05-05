from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle, Line, RoundedRectangle, PushMatrix, PopMatrix, Translate
from game_layout import GameLayout
from HoverItem import HoverItem
from TextBlurb import TextBlurb
from CustomSlider import CustomSlider
from SliderBox import SliderBox
from SpinnerBox import SpinnerBox
from usage_graph import CPUUsageGraph
from performance_monitor import PerformanceMonitor
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from usage_graph import CPUUsageGraph  # Import Graph
from performance_monitor import PerformanceMonitor  # Import CPU Monitor
from memory_usage import MemoryUsageGraph  # 
from speedometer import Speedometer  # Import Speedometer
from game_layout import GameLayout
from performance_monitor import PerformanceMonitor
from arduino_performance_graph import ArduinoGraph
from kivy.clock import Clock
from kivy.metrics import mm
from makey_makey import MakeyMakeyMonitor, KEY_LEGEND
from energy_bar import EnergyBar
from energy_input import EnergyInputWidget

Clock.max_iteration = 1000


class WindowManager(ScreenManager):
    pass



# 
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "GameScreen"

        # make performance monitor
        self.monitor = PerformanceMonitor()

#        layout for the entire screen
        self.root = FloatLayout(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})

#        background
        self.add_background(self.root)

#        Arduino graph first
        self.arduino_graph = ArduinoGraph()

#        GameLayout with both monitor and arduino graph <== make it glow like speedometer
        self.game_area = GameLayout(
            performance_monitor=self.monitor,
            arduino_graph=self.arduino_graph,
            size_hint=(0.7, 0.6),
            pos_hint={'x': 0.12, 'center_y': 0.6}
        )

#        GameLayout to root
        self.root.add_widget(self.game_area)

        # ── Energy thermometer bar — foldable, right of game_area ────────────
        self._energy_bar_visible = False
        self.energy_bar = EnergyBar(game_area_ref=self.game_area)
        self.energy_bar.size_hint = (0.025, 0)    # collapsed by default
        self.energy_bar.opacity   = 0
        self.energy_bar.pos_hint  = {'x': 0.822, 'y': 0.26}
        self.root.add_widget(self.energy_bar)
        self.game_area.energy_bar = self.energy_bar

        # small toggle button just above where the bar lives
        self.energy_bar_btn = Button(
            text='+',
            size_hint=(0.025, 0.032),
            pos_hint={'x': 0.822, 'y': 0.83},
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(0.3, 0.9, 1.0, 1),
            font_size='14sp',
            bold=True,
        )
        with self.energy_bar_btn.canvas.before:
            Color(0.04, 0.12, 0.20, 0.92)
            self._ebar_btn_bg = RoundedRectangle(
                pos=self.energy_bar_btn.pos,
                size=self.energy_bar_btn.size,
                radius=[(6, 6)] * 4,
            )
        self.energy_bar_btn.bind(
            pos=lambda *a: setattr(self._ebar_btn_bg, 'pos', self.energy_bar_btn.pos),
            size=lambda *a: setattr(self._ebar_btn_bg, 'size', self.energy_bar_btn.size),
        )
        self.energy_bar_btn.bind(on_press=lambda x: self._toggle_energy_bar())
        self.root.add_widget(self.energy_bar_btn)

        # ── Energy input (foldable, right panel) ─────────────────────────────
        self.energy_input = EnergyInputWidget(game_area_ref=self.game_area)
        self.energy_input.size_hint = (0.14, 0)
        self.energy_input.opacity   = 0
        self.energy_input.pos_hint  = {'right': 0.99, 'top': 0.70}
        self.root.add_widget(self.energy_input)

        self.energy_input_label = Label(
            text='[b]Energy Input[/b]',
            markup=True,
            font_size=Window.height * 0.028,
            color=(1.0, 0.6, 0.2, 1),
            size_hint=(0.14, 0.04),
            pos_hint={'right': 0.99, 'top': 0.51},
            halign='center', valign='middle',
            opacity=0,
        )
        self.energy_input_label.bind(size=self.energy_input_label.setter('text_size'))
        self.root.add_widget(self.energy_input_label)

        self._energy_input_visible = False
        self.energy_input_btn = Button(
            text='+',
            size_hint=(0.04, 0.032),
            pos_hint={'right': 0.99, 'y': 0.48},
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1.0, 0.65, 0.2, 1),
            font_size='15sp',
            bold=True,
        )
        with self.energy_input_btn.canvas.before:
            Color(0.20, 0.14, 0.06, 0.90)
            self._einput_btn_bg = RoundedRectangle(
                pos=self.energy_input_btn.pos,
                size=self.energy_input_btn.size,
                radius=[(10, 10)] * 4,
            )
        self.energy_input_btn.bind(
            pos=lambda *a: setattr(self._einput_btn_bg, 'pos', self.energy_input_btn.pos),
            size=lambda *a: setattr(self._einput_btn_bg, 'size', self.energy_input_btn.size),
        )
        self.energy_input_btn.bind(on_press=lambda x: self._toggle_energy_input())
        self.root.add_widget(self.energy_input_btn)

        # RIGHT SIDE PANEL with stuff
        # Using FloatLayout for screen-size independent positioning
        
        # Speedometer (top right) — small by default, tap to expand
        self.speedometer = Speedometer(performance_monitor=self.monitor)
        self.speedometer.size_hint = (0.10, 0.10)
        self.speedometer.pos_hint = {'right': 1.015, 'top': 0.95}
        self.root.add_widget(self.speedometer)

        # CPU Usage Label (under speedometer) — hidden until expanded
        self.cpu_usage_label = Label(
            text="[b]CPU % Usage[/b]",
            markup=True,
            font_size=Window.height * 0.032,
            color=(1, 1, 1, 1),
            size_hint=(0.15, 0.05),
            pos_hint={'right': 0.99, 'top': 0.68},
            halign='center',
            valign='middle',
            opacity=0
        )
        self.cpu_usage_label.bind(size=self.cpu_usage_label.setter('text_size'))
        self.root.add_widget(self.cpu_usage_label)

        self._cpu_expanded = False
        self.speedometer.bind(on_touch_down=self._on_cpu_touch)

        # Arduino Graph (under CPU label) — starts collapsed
        self.arduino_graph.size_hint = (0.15, 0)
        self.arduino_graph.opacity = 0
        self.arduino_graph.pos_hint = {'right': 0.99, 'top': 0.62}
        self.root.add_widget(self.arduino_graph)

        # Arduino Graph Label (under graph) — hidden until graph is expanded
        self.arduino_graph_label = Label(
            text="[b]Arduino Energy Input[/b]",
            markup=True,
            font_size=Window.height * 0.030,
            color=(1, 1, 1, 1),
            size_hint=(0.15, 0.05),
            pos_hint={'right': 0.99, 'top': 0.41},
            halign='center',
            valign='middle',
            opacity=0
        )
        self.arduino_graph_label.bind(size=self.arduino_graph_label.setter('text_size'))
        self.root.add_widget(self.arduino_graph_label)

        # small toggle button at bottom-right — collapses/restores the arduino graph
        self._arduino_graph_visible = False
        self.arduino_toggle_btn = Button(
            text='+',
            size_hint=(0.04, 0.032),
            pos_hint={'right': 0.99, 'y': 0.115},
            background_normal='',
            background_color=(0, 0, 0, 0),   # fully transparent — we draw our own bg
            color=(0.78, 0.82, 0.95, 1),
            font_size='15sp',
            bold=True,
        )
        with self.arduino_toggle_btn.canvas.before:
            Color(0.16, 0.18, 0.26, 0.90)
            self._ard_btn_bg = RoundedRectangle(
                pos=self.arduino_toggle_btn.pos,
                size=self.arduino_toggle_btn.size,
                radius=[(10, 10), (10, 10), (10, 10), (10, 10)]
            )
        self.arduino_toggle_btn.bind(
            pos=lambda *a: setattr(self._ard_btn_bg, 'pos', self.arduino_toggle_btn.pos),
            size=lambda *a: setattr(self._ard_btn_bg, 'size', self.arduino_toggle_btn.size),
        )
        self.arduino_toggle_btn.bind(on_press=lambda x: self._toggle_arduino_graph())
        self.root.add_widget(self.arduino_toggle_btn)


        # the spinner thingy in the controls
        self.add_preset_spinner(self.root)

        # other UI elements (Sliders, buttons, etc.)
        self.add_ui_elements(self.root)

        # Arduino connection status UI (bottom-left)
        # Arduino status with glowing text (no background box)
        self.arduino_status_container = FloatLayout(
            size_hint=(0.15, 0.035),
            pos_hint={'x': 0.005, 'y': 0.005}
        )
        
        # Status indicator dot with outline for glow effect
        self.arduino_indicator = Label(
            text="●",
            size_hint=(0.1, 1),
            pos_hint={'x': 0, 'center_y': 0.5},
            color=(1, 0.3, 0.3, 1),  # Red for disconnected
            font_size='16sp',
            halign='center',
            valign='middle',
            outline_width=2,
            outline_color=(1, 0.3, 0.3, 0.5)  # Glow effect
        )
        self.arduino_status_container.add_widget(self.arduino_indicator)
        
        # Status text with outline for glow effect
        self.arduino_status_label = Label(
            text="Arduino: connecting…",
            size_hint=(0.9, 1),
            pos_hint={'x': 0.1, 'center_y': 0.5},
            color=(0.9, 0.9, 0.9, 1),
            font_size='11sp',
            halign='left',
            valign='middle',
            bold=True,
            outline_width=1,
            outline_color=(0.5, 0.5, 0.5, 0.3)  # Subtle glow
        )
        self.arduino_status_label.bind(size=self.arduino_status_label.setter('text_size'))
        self.arduino_status_container.add_widget(self.arduino_status_label)
        
        self.root.add_widget(self.arduino_status_container)

        # ── Energy injection slider (foldable, bottom-left, for when Arduino off) ─

        # Add Everything to the Screen
        self.add_widget(self.root)

        # Initial status reflects current connection
        self._update_arduino_status_label()
        Clock.schedule_interval(lambda dt: self._update_arduino_status_label(), 2)

        # checks in the background for makey makey (every 2 seconds)
        # shows a status dot at the bottom left and a key legend when connected
        self.makey = MakeyMakeyMonitor()
        self._build_makey_status(self.root)
        Clock.schedule_interval(lambda dt: self._refresh_makey_ui(), 2)


    def _build_makey_status(self, root):
        # Status row sits below the BACK button (bottom-right)
        container = FloatLayout(
            size_hint=(0.22, 0.035),
            pos_hint={'right': 1.06, 'y': 0.005}
        )

        self.makey_dot = Label(
            text='●', size_hint=(0.08, 1), pos_hint={'x': 0, 'center_y': 0.5},
            color=(0.45, 0.45, 0.45, 1), font_size='16sp',
            halign='center', valign='middle',
            outline_width=2, outline_color=(0.3, 0.3, 0.3, 0.4)
        )
        self.makey_label = Label(
            text='Makey Makey: scanning…',
            size_hint=(0.92, 1), pos_hint={'x': 0.08, 'center_y': 0.5},
            color=(0.6, 0.6, 0.6, 1), font_size='11sp',
            halign='left', valign='middle', bold=True,
            outline_width=1, outline_color=(0.3, 0.3, 0.3, 0.2)
        )
        self.makey_label.bind(size=self.makey_label.setter('text_size'))
        container.add_widget(self.makey_dot)
        container.add_widget(self.makey_label)
        root.add_widget(container)

        # ── Key legend panel ──────────────────────────────────────────────────
        # right-side gap: under the arduino graph (y~0.36)
        # and over the button row (y~0.09). nothing else goes there.
        self.makey_legend_container = FloatLayout(
            size_hint=(0.113, 0.33),
            pos_hint={'x': 0.005, 'y': 0.13},
            opacity=0
        )

        with self.makey_legend_container.canvas.before:
            Color(0.02, 0.06, 0.14, 0.97)
            self._legend_bg = RoundedRectangle(
                pos=self.makey_legend_container.pos,
                size=self.makey_legend_container.size,
                radius=[(10, 10), (10, 10), (10, 10), (10, 10)]
            )
            Color(0.0, 0.75, 1.0, 0.85)
            self._legend_border = Line(
                rounded_rectangle=[
                    self.makey_legend_container.x,
                    self.makey_legend_container.y,
                    self.makey_legend_container.width,
                    self.makey_legend_container.height, 10
                ],
                width=1.8
            )
        self.makey_legend_container.bind(
            pos=self._update_legend_bg, size=self._update_legend_bg
        )

        legend_font = max(12, int(Window.height * 0.020))
        self.makey_legend_label = Label(
            text='', markup=True,
            size_hint=(0.88, 0.92),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            font_size=f'{legend_font}sp',
            halign='left', valign='top',
            line_height=1.35,
        )
        self.makey_legend_label.bind(size=self.makey_legend_label.setter('text_size'))
        self.makey_legend_container.add_widget(self.makey_legend_label)
        root.add_widget(self.makey_legend_container)

    def _update_legend_bg(self, *args):
        """Keep the rounded background and border in sync with the container."""
        c = self.makey_legend_container
        self._legend_bg.pos  = c.pos
        self._legend_bg.size = c.size
        self._legend_border.rounded_rectangle = [c.x, c.y, c.width, c.height, 8]

    def _refresh_makey_ui(self):
        if self.makey.connected:
            self.makey_dot.color         = (0.3, 0.85, 1, 1)
            self.makey_dot.outline_color = (0.1, 0.6, 0.9, 0.7)
            device = self.makey.device_info or 'Connected'
            self.makey_label.text        = f'Makey Makey: {device}'
            self.makey_label.color       = (0.4, 0.9, 1, 1)

            title_font = max(14, int(Window.height * 0.024))
            rows = [
                f'[b][size={title_font}][color=00cfff]KEY BINDINGS[/color][/size][/b]',
                '[color=1a5f7a]──────────────[/color]',
            ]
            for key, action in KEY_LEGEND:
                rows.append(
                    f'  [b][color=ffffff]{key}[/color][/b]'
                    f'  [color=4499bb]->[/color]'
                    f'  [color=ffa940]{action}[/color]'
                )
            self.makey_legend_label.text = '\n'.join(rows)
            self.makey_legend_container.opacity = 1

        else:
            self.makey_dot.color         = (0.45, 0.45, 0.45, 1)
            self.makey_dot.outline_color = (0.3, 0.3, 0.3, 0.3)
            self.makey_label.text        = 'Makey Makey: Not Connected'
            self.makey_label.color       = (0.55, 0.55, 0.55, 1)
            self.makey_legend_container.opacity = 0
            self.makey_legend_label.text = ''

    def _on_cpu_touch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self._toggle_cpu_panel()
            return True

    def _toggle_cpu_panel(self):
        from kivy.animation import Animation
        if self._cpu_expanded:
            Animation(size_hint_x=0.10, size_hint_y=0.10, duration=0.25).start(self.speedometer)
            self.cpu_usage_label.opacity = 0
            self._cpu_expanded = False
        else:
            Animation(size_hint_x=0.25, size_hint_y=0.25, duration=0.25).start(self.speedometer)
            self.cpu_usage_label.opacity = 1
            self._cpu_expanded = True

    def _toggle_energy_bar(self):
        from kivy.animation import Animation
        if self._energy_bar_visible:
            anim = Animation(opacity=0, duration=0.15) + Animation(size_hint_y=0, duration=0.15)
            anim.start(self.energy_bar)
            self.energy_bar_btn.text = '+'
            self._energy_bar_visible = False
        else:
            anim = Animation(size_hint_y=0.55, duration=0.20) + Animation(opacity=1, duration=0.15)
            anim.start(self.energy_bar)
            self.energy_bar_btn.text = '−'
            self._energy_bar_visible = True

    def _toggle_energy_input(self):
        from kivy.animation import Animation
        if self._energy_input_visible:
            anim = Animation(opacity=0, duration=0.15) + Animation(size_hint_y=0, duration=0.15)
            anim.start(self.energy_input)
            self.energy_input_label.opacity = 0
            self.energy_input_btn.text = '+'
            self._energy_input_visible = False
        else:
            anim = Animation(size_hint_y=0.18, duration=0.15) + Animation(opacity=1, duration=0.15)
            anim.start(self.energy_input)
            self.energy_input_label.opacity = 1
            self.energy_input_btn.text = '−'
            self._energy_input_visible = True

    def _toggle_arduino_graph(self):
        from kivy.animation import Animation
        if self._arduino_graph_visible:
            # fade out first, then collapse height to zero
            anim = Animation(opacity=0, duration=0.15) + Animation(size_hint_y=0, duration=0.15)
            anim.start(self.arduino_graph)
            self.arduino_graph_label.opacity = 0
            self.arduino_toggle_btn.text = '+'
            self._arduino_graph_visible = False
        else:
            # expand height back to original, then fade in
            anim = Animation(size_hint_y=0.2, duration=0.15) + Animation(opacity=1, duration=0.15)
            anim.start(self.arduino_graph)
            self.arduino_graph_label.opacity = 1
            self.arduino_toggle_btn.text = '−'
            self._arduino_graph_visible = True

    def add_background(self, root):
        """Add a grey background and bind its size/position to root."""
        with root.canvas.before:
            Color(0.04, 0.04, 0.07, 1)  # Dark navy — pairs with sphere glow colours
            self.ui_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_ui_background, size=self.update_ui_background)

    def update_ui_background(self, instance, *args):
        """Update background dynamically when the window size changes."""
        self.ui_rect.pos = instance.pos
        self.ui_rect.size = instance.size

    def add_preset_spinner(self, root):
        # spinner is now part of the main bottom row — nothing to do here
        pass

    def generated_selected_preset(self, preset):
        """when user selects a preset, generate that type of molecule config"""
        if preset == "Solid":
            self.game_area.generate_solid()
        elif preset == "Liquid":
            self.game_area.generate_liquid()
        elif preset == "Gas":
            self.game_area.generate_gas()

    def _make_query_btn(self, pos_hint, callback):
        """Small styled circle '?' button — replaces HoverItem image buttons."""
        import os as _os
        from kivy.graphics import Color, Ellipse, Line as GLine
        _font = _os.path.join(_os.path.dirname(__file__), "Fonts/Impact.ttf")
        btn = Button(
            text='?',
            size_hint=(0.030, 0.030),
            pos_hint=pos_hint,
            background_normal='', background_color=(0, 0, 0, 0),
            color=(0.0, 0.85, 1.0, 1),
            font_name=_font,
        )
        with btn.canvas.before:
            Color(0.04, 0.10, 0.28, 0.95)
            _bg = Ellipse(pos=btn.pos, size=btn.size)
            Color(0.15, 0.65, 1.0, 0.85)
            _brd = GLine(ellipse=(btn.x, btn.y, btn.width, btn.height), width=1.5)
        def _sync(*a):
            _bg.pos = btn.pos
            _bg.size = btn.size
            _brd.ellipse = (btn.x, btn.y, btn.width, btn.height)
            btn.font_size = f'{max(9, int(btn.height * 0.52))}sp'
        btn.bind(pos=_sync, size=_sync)
        btn.bind(on_press=lambda *a: callback())
        return btn

    def add_ui_elements(self, root):
        """add all the sliders and buttons and stuff"""
        # shared description label — shown when any slider '?' is tapped
        import os as _os
        _font = _os.path.join(_os.path.dirname(__file__), "Fonts/Impact.ttf")
        self._slider_info_label = Label(
            text='',
            font_name=_font,
            font_size='13sp',
            color=(0.78, 0.90, 1.0, 1),
            halign='left', valign='middle',
            size_hint=(0.75, None),
            height=0, opacity=0,
            pos_hint={'center_x': 0.48, 'y': 0.10},
        )
        with self._slider_info_label.canvas.before:
            Color(0.04, 0.07, 0.15, 0.96)
            self._sil_bg = Rectangle(
                pos=self._slider_info_label.pos,
                size=self._slider_info_label.size,
            )
            Color(0.0, 0.55, 0.9, 0.75)
            self._sil_border = Line(
                rectangle=(
                    self._slider_info_label.x, self._slider_info_label.y,
                    self._slider_info_label.width, self._slider_info_label.height,
                ),
                width=1.4,
            )
        def _sync_sil(*a):
            lbl = self._slider_info_label
            self._sil_bg.pos  = lbl.pos
            self._sil_bg.size = lbl.size
            self._sil_border.rectangle = (lbl.x, lbl.y, lbl.width, lbl.height)
            lbl.text_size = (lbl.width - 14, None)
        self._slider_info_label.bind(pos=_sync_sil, size=_sync_sil)
        root.add_widget(self._slider_info_label)

        self.ui_panel = self.create_sliders()
        self.ui_panel.opacity = 0  # Hidden by default
        self.ui_panel_visible = False  # Track visibility state
        bottom_row = self.create_bottom_controls()
        root.add_widget(self.ui_panel)
        root.add_widget(bottom_row)
        self.add_stat_labels(root)
        
        self.lennard_jones_text = TextBlurb(
            text="Lennard-Jones potential: a simple mathematical model that describes the attractive and repulsive forces between atoms or molecules, like how they pull towards each other at a moderate distance but push away when very close.",
            parent_size_prop=(0.15, 0.07),
            parent_pos_prop=(0.9, 0.38))
        self.query_lennard_jones = self._make_query_btn(
            {"center_x": 0.93, "center_y": 0.3},
            lambda: self.toggle_info(self.lennard_jones_text))

        self.verlet_text = TextBlurb(
            text="Verlet algorithm: a method used to calculate the movement of these particles in a simulation, allowing us to track how they interact based on the Lennard-Jones potential over time.",
            parent_size_prop=(0.15, 0.07),
            parent_pos_prop=(0.87, 0.11))
        self.query_verlet = self._make_query_btn(
            {"center_x": 0.77, "center_y": 0.11},
            lambda: self.toggle_info(self.verlet_text))

        self.cursOr = Image()
        self.cursOr.source = "Graphics/Cursor.png"
        self.cursOr.size_hint = (0.02, 0.02)
        self.cursOr.allow_stretch = True

        root.add_widget(self.query_lennard_jones)
        root.add_widget(self.lennard_jones_text)

        root.add_widget(self.query_verlet)
        root.add_widget(self.verlet_text)
        
        Window.bind(mouse_pos=self.mPos)
        root.add_widget(self.cursOr)

    def _update_arduino_status_label(self):
        try:
            ard = self.game_area.arduino
            if ard and ((getattr(ard, 'serial_connection', None) and ard.serial_connection.is_open) or getattr(ard, 'sock', None)):
                info = getattr(ard, 'connection_info', None)
                mode = 'Wi‑Fi' if getattr(ard, 'sock', None) else 'Serial'
                if not info:
                    info = getattr(ard, 'port', 'unknown')
                self.arduino_status_label.text = f"Arduino: Connected ({mode})"
                # Green glowing text
                self.arduino_status_label.color = (0.4, 1, 0.4, 1)
                self.arduino_status_label.outline_color = (0.2, 0.8, 0.2, 0.6)
                # Green glowing dot
                self.arduino_indicator.color = (0.4, 1, 0.4, 1)
                self.arduino_indicator.outline_color = (0.2, 0.8, 0.2, 0.7)
            else:
                self.arduino_status_label.text = "Arduino: Not Connected"
                # Red glowing text
                self.arduino_status_label.color = (1, 0.5, 0.5, 1)
                self.arduino_status_label.outline_color = (0.8, 0.2, 0.2, 0.5)
                # Red glowing dot
                self.arduino_indicator.color = (1, 0.3, 0.3, 1)
                self.arduino_indicator.outline_color = (0.8, 0.2, 0.2, 0.6)
        except Exception:
            self.arduino_status_label.text = "Arduino: Not Connected"
            # Red glowing text
            self.arduino_status_label.color = (1, 0.5, 0.5, 1)
            self.arduino_status_label.outline_color = (0.8, 0.2, 0.2, 0.5)
            # Red glowing dot
            self.arduino_indicator.color = (1, 0.3, 0.3, 1)
            self.arduino_indicator.outline_color = (0.8, 0.2, 0.2, 0.6)

    def retry_arduino_connect(self):
        # Close existing, attempt to re-open without blocking UI
        # IT"S FIXED OOOOOOOOOO
        try:
            if self.game_area.arduino:
                self.game_area.arduino.close()
        except Exception:
            pass

        from arduino_reading import ArduinoReading
        try:
            self.game_area.arduino = ArduinoReading()
            print(f"[INFO] Arduino reconnected on {self.game_area.arduino.port}")
        except Exception as e:
            print(f"[WARNING] Arduino reconnect failed: {e}")
            self.game_area.arduino = None
        self._update_arduino_status_label()


    def mPos(self, window, pos):
        self.cursOr.pos = (pos[0] - Window.width * 0.01, pos[1] - Window.height * 0.01)

    # Defines call Back Function HEre for Slider Box!!!!
    def create_sliders(self):
        """Create the slider UI for gravity, delta, sigma, epsilon, speed, and size."""
        sp_x = max(8,  int(Window.width  * 0.010))
        sp_y = max(6,  int(Window.height * 0.009))
        pad  = max(5,  int(Window.height * 0.007))

        ui_panel = BoxLayout(
            orientation='vertical',
            size_hint=(0.8, 0.18),
            pos_hint={'center_x': 0.5, 'center_y': 0.23},
        )

        slider_grid = GridLayout(
            cols=3, rows=2,
            size_hint=(1, 0.84),
            spacing=(sp_x, sp_y),
            padding=[pad, pad, pad, pad]
        )

        # shared info popup — shows description for whichever slider '?' was tapped
        _active = [None]
        def _show_slider_info(text):
            from kivy.animation import Animation
            lbl = self._slider_info_label
            if lbl.text == text and lbl.height > 0:
                Animation(height=0, opacity=0, duration=0.12).start(lbl)
                lbl.text = ''
                _active[0] = None
            else:
                lbl.text = text
                _active[0] = text
                Animation(height=45, opacity=1, duration=0.12).start(lbl)

        gravity_box = SliderBox(
            "Gravity (W increase, S decrease)",
            0, 10, 0, 0.01, self.game_area.set_gravity,
            info_text="Pulls all molecules downward, just like real gravity. Set to 0 for a weightless space environment!",
            info_callback=_show_slider_info,
            size_hint=(1, 1)
        )
        epsilon_box = SliderBox(
            "Epsilon (Potential Depth used for Lennard-Jones force between Molecules) (E increase, D decrease)",
            0, 10, 1, 0.1, self.game_area.set_epsilon,
            info_text="How strongly molecules attract each other. High ε = sticky molecules that clump together. Low ε = they barely feel each other.",
            info_callback=_show_slider_info,
        )
        sigma_box = SliderBox(
            "Sigma (Potential Distance used for Lennard-Jones force between Molecules) (R increase, F decrease)",
            0.1, 3, 1, 0.01, self.game_area.set_sigma,
            info_text="Natural spacing between molecules — like the size of the atom. High σ = molecules settle farther apart from each other.",
            info_callback=_show_slider_info,
        )
        delta_box = SliderBox(
            "Delta (Timestep update for Verlet's Algorithm) (T increase, G decrease)",
            1 / 60.0, 1, 1 / 60.0, 1 / 60.0, self.game_area.set_delta,
            info_text="Simulation timestep size. Larger Δt = faster but less accurate. Too large causes molecules to fly apart — try it!",
            info_callback=_show_slider_info,
        )
        speed_box = SliderBox(
            "Speed of Simulation (Y increase, H decrease)",
            0.1, 1, 1, 0.1, self.game_area.set_speed,
            info_text="How fast the simulation clock runs. Does not change the physics, just how quickly you watch it play out.",
            info_callback=_show_slider_info,
        )
        size_box = SliderBox(
            "Size of Molecules (U increase, J decrease)",
            0.2, 1, 0.6, 0.05, self.game_area.set_size,
            info_text="Physical radius of each molecule. Larger molecules collide sooner and are easier to see on screen.",
            info_callback=_show_slider_info,
        )

        slider_grid.add_widget(gravity_box)
        slider_grid.add_widget(epsilon_box)
        slider_grid.add_widget(sigma_box)
        slider_grid.add_widget(delta_box)
        slider_grid.add_widget(speed_box)
        slider_grid.add_widget(size_box)

        self.game_area.gravity_slider = gravity_box.slider
        self.game_area.epsilon_slider = epsilon_box.slider
        self.game_area.sigma_slider = sigma_box.slider
        self.game_area.delta_slider = delta_box.slider
        self.game_area.speed_slider = speed_box.slider
        self.game_area.size_slider = size_box.slider

        # Verlet/Euler + Vectors toggle row — centred below the sliders
        verlet_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.22))
        self.verlet_button = self.create_hover_button("Verlet-Off", self.toggle_verlet_mode)
        self.verlet_button.size_hint = (0.25, 1)

        self.bonds_button = HoverItem(
            size_hint=(0.25, 1),
            hoverSource="Graphics/Vectors_Highlighted.png",
            defaultSource="Graphics/Vectors.png",
            function=lambda x: self.toggle_force_arrows()
        )
        with self.bonds_button.canvas.after:
            Color(0.45, 0.48, 0.56, 0.85)
            _bonds_border = Line(rectangle=(self.bonds_button.x, self.bonds_button.y,
                                            self.bonds_button.width, self.bonds_button.height), width=1.5)
        self.bonds_button.bind(
            pos=lambda *a: setattr(_bonds_border, 'rectangle',
                (self.bonds_button.x, self.bonds_button.y,
                 self.bonds_button.width, self.bonds_button.height)),
            size=lambda *a: setattr(_bonds_border, 'rectangle',
                (self.bonds_button.x, self.bonds_button.y,
                 self.bonds_button.width, self.bonds_button.height)),
        )

        verlet_row.add_widget(Widget(size_hint=(0.125, 1)))
        verlet_row.add_widget(self.verlet_button)
        verlet_row.add_widget(Widget(size_hint=(0.25, 1)))
        verlet_row.add_widget(self.bonds_button)
        verlet_row.add_widget(Widget(size_hint=(0.125, 1)))

        ui_panel.add_widget(slider_grid)
        ui_panel.add_widget(verlet_row)

        return ui_panel
    
    def toggle_info(self, text):
        text.toggle_visibility()

    def toggle_sliders(self):
        """Toggle visibility of the slider panel."""
        if self.ui_panel_visible:
            self.ui_panel.opacity = 0  # Hide
            self.ui_panel_visible = False
            self.remove_glow_effect()
            # dont hover (no white square)
            self.presets_button.hoverSource = "Graphics/Why.png"
        else:
            self.ui_panel.opacity = 1  # Show
            self.ui_panel_visible = True
            self.add_glow_effect()
            # no hover so glow shows right
            self.presets_button.hoverSource = "Graphics/Why.png"
            # Force button to show default image
            self.presets_button.source = self.presets_button.defaultSource
    
    def add_glow_effect(self):
        """Add a glowing blue-purple gradient effect to the presets button."""
        from kivy.graphics import Color, Ellipse, PushMatrix, PopMatrix, Rotate
        from kivy.animation import Animation
        
        # keep glow things so we can update em
        self.glow_elements = []
        
        # make glowing glow layers around the button using ellipses for soft edges
        with self.presets_button.canvas.before:
            # many layers of ellipses = gradient glow effect
            
            # Outer glow - deep purple (largest, most transparent)
            Color(0.6, 0.0, 1.0, 0.15)  # Purple
            glow1 = Ellipse(
                pos=(self.presets_button.x - 15, self.presets_button.y - 15),
                size=(self.presets_button.width + 30, self.presets_button.height + 30)
            )
            self.glow_elements.append(('ellipse', glow1, 15))
            
            # layer 2 - purple
            Color(0.5, 0.2, 0.9, 0.2)
            glow2 = Ellipse(
                pos=(self.presets_button.x - 12, self.presets_button.y - 12),
                size=(self.presets_button.width + 24, self.presets_button.height + 24)
            )
            self.glow_elements.append(('ellipse', glow2, 12))
            
            # layer 3 - blue-purple
            Color(0.3, 0.3, 1.0, 0.25)
            glow3 = Ellipse(
                pos=(self.presets_button.x - 9, self.presets_button.y - 9),
                size=(self.presets_button.width + 18, self.presets_button.height + 18)
            )
            self.glow_elements.append(('ellipse', glow3, 9))
            
            # layer 4 - blue
            Color(0.2, 0.5, 1.0, 0.3)
            glow4 = Ellipse(
                pos=(self.presets_button.x - 6, self.presets_button.y - 6),
                size=(self.presets_button.width + 12, self.presets_button.height + 12)
            )
            self.glow_elements.append(('ellipse', glow4, 6))
            
            # layer 5 - light blue
            Color(0.4, 0.7, 1.0, 0.35)
            glow5 = Ellipse(
                pos=(self.presets_button.x - 3, self.presets_button.y - 3),
                size=(self.presets_button.width + 6, self.presets_button.height + 6)
            )
            self.glow_elements.append(('ellipse', glow5, 3))
            
            # innermost - bright cyan
            Color(0.5, 0.8, 1.0, 0.4)
            glow6 = Ellipse(
                pos=(self.presets_button.x - 1, self.presets_button.y - 1),
                size=(self.presets_button.width + 2, self.presets_button.height + 2)
            )
            self.glow_elements.append(('ellipse', glow6, 1))
        
        # hook up position changes
        self.presets_button.bind(pos=self.update_glow_position, size=self.update_glow_position)
    
    def update_glow_position(self, *args):
        """Update glow position when button moves."""
        if hasattr(self, 'glow_elements'):
            for glow_type, glow_shape, offset in self.glow_elements:
                glow_shape.pos = (self.presets_button.x - offset, self.presets_button.y - offset)
                glow_shape.size = (self.presets_button.width + offset * 2, self.presets_button.height + offset * 2)
    
    def remove_glow_effect(self):
        """Remove the glowing effect from the presets button."""
        if hasattr(self, 'glow_elements'):
            self.presets_button.canvas.before.clear()
            self.glow_elements = []
            self.presets_button.unbind(pos=self.update_glow_position, size=self.update_glow_position)

    def create_bottom_controls(self):
        """One single row at the bottom: preset picker + all control buttons."""
        button_height = Window.height * 0.08
        bottom_row = BoxLayout(
            orientation='horizontal',
            size_hint=(1.0, None),
            height=button_height,
            pos_hint={'center_x': 0.5, 'center_y': 0.05}
        )

        # preset picker (◄ SOLID ►) + create button — live here now
        self.preset_spinner = SpinnerBox(0, ["Solid", "Liquid", "Gas"], size_hint=(1.4, 1))
        self.preset_activate = HoverItem(
            size_hint=(1, 1),
            hoverSource="Graphics/Create_Highlighted.png",
            defaultSource="Graphics/Create.png",
            function=lambda x: self.generated_selected_preset(
                self.preset_spinner.possibleValues[self.preset_spinner.value])
        )
        with self.preset_activate.canvas.after:
            Color(0.45, 0.48, 0.56, 0.85)
            _create_border = Line(rectangle=(self.preset_activate.x, self.preset_activate.y,
                                             self.preset_activate.width, self.preset_activate.height), width=1.5)
        self.preset_activate.bind(
            pos=lambda *a: setattr(_create_border, 'rectangle',
                (self.preset_activate.x, self.preset_activate.y,
                 self.preset_activate.width, self.preset_activate.height)),
            size=lambda *a: setattr(_create_border, 'rectangle',
                (self.preset_activate.x, self.preset_activate.y,
                 self.preset_activate.width, self.preset_activate.height)),
        )

        self.presets_button = self.create_hover_button("Why", self.toggle_sliders)
        self.presets_button.hoverSource = "Graphics/Why_Highlighted.png"
        self.use_forces_button = self.create_hover_button("Forces-Off", self.toggle_intermolecular_forces)
        self.clear_button = self.create_hover_button("Clear", self.clear_game_area)
        self.start_stop_button = self.create_hover_button("Start", self.toggle_simulation)
        self.back_button = self.create_hover_button("Back", self.go_back)

        bottom_row.add_widget(self.preset_spinner)
        bottom_row.add_widget(self.preset_activate)
        bottom_row.add_widget(self.presets_button)
        bottom_row.add_widget(self.use_forces_button)
        bottom_row.add_widget(self.start_stop_button)
        bottom_row.add_widget(self.clear_button)
        bottom_row.add_widget(self.back_button)
        return bottom_row
    
    def go_back(self):
        self.parent.go_back(self.name)

    def create_slider(self, label_text, min_value, max_value, default_value, step_value, callback):
        """Helper to create labeled sliders."""
        box = BoxLayout(orientation='horizontal')
        label = Label(text=label_text, size_hint=(0.3, None), height=10)
        if False:
            slider = Slider(min=min_value, max=max_value, value=default_value, step=step_value, size_hint=(0.7, None), height=10)
        else:
            slider = CustomSlider(
                min=min_value,
                max=max_value,
                value=default_value,
                step=step_value,
                track_image="Graphics/SliderTrack.png",
                thumb_image="Graphics/SliderThumb.png",
                slider_length=200,
                size_hint=(0.7,None),
                height=10
            )
        slider.bind(value=lambda instance, value: callback(value))
        box.add_widget(label)
        box.add_widget(slider)
        return box, slider

    def create_hover_button(self, label, callback):
        """Helper to create buttons with hover effects (responsive sizing)."""
        btn = HoverItem(
            size_hint=(1, 1),
            hoverSource=f"Graphics/{label}_Highlighted.png",
            defaultSource=f"Graphics/{label}.png",
            function=lambda x: callback()
        )
        with btn.canvas.after:
            Color(0.45, 0.48, 0.56, 0.85)
            border_rect = Line(rectangle=(btn.x, btn.y, btn.width, btn.height), width=1.5)
        def _update_border(*args):
            border_rect.rectangle = (btn.x, btn.y, btn.width, btn.height)
        btn.bind(pos=_update_border, size=_update_border)
        return btn
        
    def toggle_intermolecular_forces(self):
        """Toggle the usage of intermolecular forces."""
        if self.game_area.intermolecular_forces:
            self.use_forces_button.hoverSource="Graphics/Forces-On_Highlighted.png"
            self.use_forces_button.defaultSource="Graphics/Forces-On.png"
            self.use_forces_button.source = self.use_forces_button.hoverSource if self.use_forces_button.use else self.use_forces_button.defaultSource
        else:
            self.use_forces_button.hoverSource="Graphics/Forces-Off_Highlighted.png"
            self.use_forces_button.defaultSource="Graphics/Forces-Off.png"
            self.use_forces_button.source = self.use_forces_button.hoverSource if self.use_forces_button.use else self.use_forces_button.defaultSource
        self.game_area.toggle_intermolecular_forces()
        
    def toggle_force_arrows(self):
        """Toggle directional force arrows on molecules."""
        if self.game_area.forces_visible:
            self.bonds_button.hoverSource = "Graphics/Vectors_Highlighted.png"
            self.bonds_button.defaultSource = "Graphics/Vectors.png"
        else:
            self.bonds_button.hoverSource = "Graphics/Hide-Vecs_Highlighted.png"
            self.bonds_button.defaultSource = "Graphics/Hide-Vecs.png"
        self.bonds_button.source = self.bonds_button.hoverSource if self.bonds_button.use else self.bonds_button.defaultSource
        self.game_area.toggle_force_arrows()

    def toggle_forces_visible(self):
        """Toggle the visibility of forces."""
        if self.game_area.forces_visible:
            self.see_forces_button.hoverSource="Graphics/Show-Forces_Highlighted.png"
            self.see_forces_button.defaultSource="Graphics/Show-Forces.png"
            self.see_forces_button.source = self.see_forces_button.hoverSource if self.see_forces_button.use else self.see_forces_button.defaultSource
        else:
            self.see_forces_button.hoverSource="Graphics/Hide-Forces_Highlighted.png"
            self.see_forces_button.defaultSource="Graphics/Hide-Forces.png"
            self.see_forces_button.source = self.see_forces_button.hoverSource if self.see_forces_button.use else self.see_forces_button.defaultSource
        self.game_area.toggle_forces_visible()

    # toggle_combine was removed (dead code with broken return statement)

    def toggle_simulation(self):
        """Toggle the simulation state. STOP resets fully; START begins fresh."""
        if self.game_area.simulation_running:
            self.start_stop_button.hoverSource="Graphics/Start_Highlighted.png"
            self.start_stop_button.defaultSource="Graphics/Start.png"
            self.start_stop_button.source = self.start_stop_button.hoverSource if self.start_stop_button.use else self.start_stop_button.defaultSource
            self.game_area.reset_simulation()
            # sync UI buttons to match reset state
            self.use_forces_button.hoverSource = "Graphics/Forces-Off_Highlighted.png"
            self.use_forces_button.defaultSource = "Graphics/Forces-Off.png"
            self.use_forces_button.source = self.use_forces_button.hoverSource if self.use_forces_button.use else self.use_forces_button.defaultSource
            self.bonds_button.hoverSource = "Graphics/Vectors_Highlighted.png"
            self.bonds_button.defaultSource = "Graphics/Vectors.png"
            self.bonds_button.source = self.bonds_button.hoverSource if self.bonds_button.use else self.bonds_button.defaultSource
        else:
            self.start_stop_button.hoverSource="Graphics/Stop_Highlighted.png"
            self.start_stop_button.defaultSource="Graphics/Stop.png"
            self.start_stop_button.source = self.start_stop_button.hoverSource if self.start_stop_button.use else self.start_stop_button.defaultSource
            self.game_area.start_simulation()
            
    def toggle_verlet_mode(self):
        """Toggle between Verlet and non-Verlet updates."""
        if self.game_area.use_verlet:
            self.verlet_button.hoverSource="Graphics/Verlet-On_Highlighted.png"
            self.verlet_button.defaultSource="Graphics/Verlet-On.png"
        else:
            self.verlet_button.hoverSource="Graphics/Verlet-Off_Highlighted.png"
            self.verlet_button.defaultSource="Graphics/Verlet-Off.png"
        self.verlet_button.source = self.verlet_button.hoverSource if self.verlet_button.use else self.verlet_button.defaultSource
        self.game_area.toggle_update_mode()

    def clear_game_area(self):
        """Clear the game area of all molecules and bonds."""
        self.game_area.clear_molecules()

    # def create_forces_switch(self):
    #     """Create a switch for intermolecular forces."""
    #     return self.create_switch("Forces", self.game_area.toggle_intermolecular_forces)

    # def create_forces_visible_switch(self):
    #     """Create a switch to toggle visibility of forces."""
    #     return self.create_switch("Show Forces", self.game_area.toggle_forces_visible)

    # def create_switch(self, label_text, callback):
    #     """Helper to create labeled switches."""
    #     container = BoxLayout(orientation='horizontal', size_hint=(0.6, None), height=50)
    #     label = Label(text=label_text, size_hint=(0.6, 1, size_hint=(None, None)))
    #     switch = Switch(active=True, size_hint=(0.4, 1))
    #     switch.bind(active=callback)
    #     container.add_widget(label)
    #     container.add_widget(switch)
    #     return container, switch

    def add_stat_labels(self, root):
        """Add labels to display simulation stats with responsive font sizes."""
        self.game_area.total_energy_label = Label(
            text="Total Energy: 0",
            size_hint=(0.2, 0.1),
            pos_hint={'center_x': 0.18, 'center_y': 0.95},
            font_size=Window.height * 0.035,
            bold=True,
            color=(1.0, 0.6, 0.2, 1),   # warm orange
        )
        self.game_area.temperature_label = Label(
            text="Temperature: 0",
            size_hint=(0.2, 0.1),
            pos_hint={'center_x': 0.51, 'center_y': 0.95},
            font_size=Window.height * 0.035,
            bold=True,
            color=(1.0, 0.32, 0.55, 1), # hot pink — matches molecule fast-colour
        )
        self.game_area.pressure_label = Label(
            text="Pressure: 0",
            size_hint=(0.2, 0.1),
            pos_hint={'center_x': 0.84, 'center_y': 0.95},
            font_size=Window.height * 0.035,
            bold=True,
            color=(0.35, 0.85, 1.0, 1), # cyan — matches bond / arrow colour
        )

        root.add_widget(self.game_area.total_energy_label)
        root.add_widget(self.game_area.temperature_label)
        root.add_widget(self.game_area.pressure_label)


class MyApp(App):
    
    def build(self):
        self.window_manager = WindowManager()
        self.game_screen = GameScreen()
        self.window_manager.add_widget(self.game_screen)
        return self.window_manager

if __name__ == "__main__":
    MyApp().run()