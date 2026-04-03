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

Clock.max_iteration = 1000


class WindowManager(ScreenManager):
    pass



# 
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "GameScreen"

        # Create Performance Monitor
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

        # ------------------ RIGHT SIDE PANEL (RESPONSIVE) -------------------
        # Use FloatLayout with pos_hint for screen-size independent positioning
        
        # Speedometer (top right) - larger size, keep circular
        self.speedometer = Speedometer(performance_monitor=self.monitor)
        # Using same proportion for width and height to maintain circular shape
        self.speedometer.size_hint = (0.25, 0.25)  # Bigger and circular (increased from 0.20)
        self.speedometer.pos_hint = {'right': 1.035, 'top': 0.95}  # Moved more right to perfectly center with label
        self.root.add_widget(self.speedometer)

        # CPU Usage Label (below speedometer, centered)
        self.cpu_usage_label = Label(
            text="[b]CPU % Usage[/b]",
            markup=True,
            font_size=Window.height * 0.032,  # 3.2% of screen height (much larger)
            color=(1, 1, 1, 1),
            size_hint=(0.15, 0.05),
            pos_hint={'right': 0.99, 'top': 0.68},
            halign='center',
            valign='middle'
        )
        self.cpu_usage_label.bind(size=self.cpu_usage_label.setter('text_size'))
        self.root.add_widget(self.cpu_usage_label)

        # Arduino Graph (below CPU label)
        self.arduino_graph.size_hint = (0.15, 0.2)
        self.arduino_graph.pos_hint = {'right': 0.99, 'top': 0.62}
        self.root.add_widget(self.arduino_graph)

        # Arduino Graph Label (below graph, centered)
        self.arduino_graph_label = Label(
            text="[b]Arduino Energy Input[/b]",
            markup=True,
            font_size=Window.height * 0.030,  # 3.0% of screen height (much larger)
            color=(1, 1, 1, 1),
            size_hint=(0.15, 0.05),
            pos_hint={'right': 0.99, 'top': 0.41},
            halign='center',
            valign='middle'
        )
        self.arduino_graph_label.bind(size=self.arduino_graph_label.setter('text_size'))
        self.root.add_widget(self.arduino_graph_label)

        # Arduino label: get it from the same game_area
        self.arduino_label = self.game_area.arduino_data_label
        self.root.add_widget(self.arduino_label)  # to root, not inside game_area

        # the preset selector spinner in the control section
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

        # Add Everything to the Screen
        self.add_widget(self.root)

        # Initial status reflects current connection
        self._update_arduino_status_label()
        Clock.schedule_interval(lambda dt: self._update_arduino_status_label(), 2)

        # Makey Makey - checks in the background every 2 seconds if one is plugged in
        # shows a status dot at the bottom left and a key legend when connected
        self.makey = MakeyMakeyMonitor()
        self._build_makey_status(self.root)
        Clock.schedule_interval(lambda dt: self._refresh_makey_ui(), 2)


    def _build_makey_status(self, root):
        # Status row (dot + text) stays at the bottom-left, above the Arduino status
        container = FloatLayout(
            size_hint=(0.22, 0.035),
            pos_hint={'x': 0.005, 'y': 0.042}
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
        # Sits in the right-side gap: below the Arduino graph label (y≈0.36)
        # and above the bottom button row (y≈0.09).  Nothing else lives there.
        self.makey_legend_container = FloatLayout(
            size_hint=(0.155, 0.245),
            pos_hint={'right': 0.99, 'y': 0.105},
            opacity=0       # hidden until Makey Makey connects
        )

        # Dark rounded background + glowing border
        with self.makey_legend_container.canvas.before:
            Color(0.03, 0.07, 0.15, 0.92)
            self._legend_bg = RoundedRectangle(
                pos=self.makey_legend_container.pos,
                size=self.makey_legend_container.size,
                radius=[(8, 8), (8, 8), (8, 8), (8, 8)]
            )
            Color(0.2, 0.6, 1.0, 0.6)
            self._legend_border = Line(
                rounded_rectangle=[
                    self.makey_legend_container.x,
                    self.makey_legend_container.y,
                    self.makey_legend_container.width,
                    self.makey_legend_container.height, 8
                ],
                width=1.2
            )
        self.makey_legend_container.bind(
            pos=self._update_legend_bg, size=self._update_legend_bg
        )

        # Inner label — positioned with a small inset so text doesn't touch border
        self.makey_legend_label = Label(
            text='', markup=True,
            size_hint=(0.88, 0.90),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            font_size='9.5sp',
            halign='left', valign='top'
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

            # Build styled legend:  [cyan key]  [dim arrow]  [warm action]
            rows = ['[b][color=40d4ff]  Makey Makey Controls[/color][/b]', '']
            for key, action in KEY_LEGEND:
                rows.append(
                    f'  [color=7ec8e8]{key}[/color]'
                    f'  [color=556677]→[/color]'
                    f'  [color=ffd580]{action}[/color]'
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
        """Add the preset spinner to the bottom control section."""
        spinner_h = max(28, int(Window.height * 0.04))
        self.spinner_row = BoxLayout(orientation='horizontal', size_hint=(0.4, None), height=spinner_h, pos_hint={'center_x': 0.3, 'y': 0.085})

        # Label for the preset spinner - REMOVED (redundant with new Presets button)
        # preset_label = Label(text="Presets:", size_hint=(0.4, 1, size_hint=(None, None)), font_size=14)
        # self.preset_label = HoverItem(size_hint=(1, 1), 
        #                               hoverSource="Graphics/Presets.png", 
        #                               defaultSource="Graphics/Presets.png", 
        #                               function=lambda x : None)
        # self.spinner_row.add_widget(self.preset_label)

        # Spinner for presets
        # preset_spinner = Spinner(
        #     text="Solid",
        #     values=("Solid", "Liquid", "Gas"),
        #     size_hint=(0.6, 1),
        #     font_size=14
        # )
        # preset_spinner.bind(text=self.on_preset_selected)
        
        self.preset_spinner = SpinnerBox(0, ["Solid", "Liquid", "Gas"], size_hint=(1, 1))
        self.spinner_row.add_widget(self.preset_spinner)
        
        self.preset_activate = HoverItem(size_hint=(1, 1), 
                                         hoverSource="Graphics/Create_Highlighted.png", 
                                         defaultSource="Graphics/Create.png", 
                                         function=lambda x : 
                                             self.generated_selected_preset(self.preset_spinner.possibleValues[self.preset_spinner.value]))
        self.spinner_row.add_widget(self.preset_activate)

        # Add the spinner row to the root layout
        root.add_widget(self.spinner_row)

    def generated_selected_preset(self, preset):
        """Handle preset selection and update the GameLayout."""
        if preset == "Solid":
            self.game_area.generate_solid()
        elif preset == "Liquid":
            self.game_area.generate_liquid()
        elif preset == "Gas":
            self.game_area.generate_gas()

    def add_ui_elements(self, root):
        """Add sliders, switches, and other UI elements."""
        self.ui_panel = self.create_sliders()
        self.ui_panel.opacity = 0  # Hidden by default
        self.ui_panel_visible = False  # Track visibility state
        bottom_row = self.create_bottom_controls()
        root.add_widget(self.ui_panel)
        root.add_widget(bottom_row)
        self.add_stat_labels(root)
        
        self.lennard_jones_text = TextBlurb(text="Lennard-Jones potential: a simple mathematical model that describes the attractive and repulsive forces between atoms or molecules, like how they pull towards each other at a moderate distance but push away when very close.",
                                            parent_size_prop=(0.15, 0.07),
                                            parent_pos_prop=(0.9, 0.38))
        self.query_lennard_jones = HoverItem(size_hint=(0.05, 0.05), pos_hint={"center_x":0.93, "center_y":0.3}, height=50, hoverSource="Graphics/Query_Highlighted.png", defaultSource="Graphics/Query.png", function=lambda x: self.toggle_info(self.query_lennard_jones, self.lennard_jones_text))
        
        self.verlet_text = TextBlurb(text="Verlet algorithm: a method used to calculate the movement of these particles in a simulation, allowing us to track how they interact based on the Lennard-Jones potential over time.",
                                            parent_size_prop=(0.15, 0.07),
                                            parent_pos_prop=(0.87, 0.11))
        self.query_verlet = HoverItem(size_hint=(0.05, 0.05), pos_hint={"center_x":0.77, "center_y":0.11}, height=50, hoverSource="Graphics/Query_Highlighted.png", defaultSource="Graphics/Query.png", function=lambda x: self.toggle_info(self.query_verlet, self.verlet_text))
        
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
        sp_x = max(8,  int(Window.width  * 0.010))   # ~1 % of screen width
        sp_y = max(6,  int(Window.height * 0.009))   # ~0.9 % of screen height
        pad  = max(5,  int(Window.height * 0.007))
        ui_panel = GridLayout(cols=3,
                              rows=2,
                              size_hint=(0.8, 0.15),
                              pos_hint={'center_x': 0.5, 'center_y': 0.22},
                              spacing=(sp_x, sp_y),
                              padding=[pad, pad, pad, pad]
        )

        gravity_box = SliderBox(
            "Gravity (W increase, S decrease)",
            0, 10, 0, 0.01, self.game_area.set_gravity, size_hint = (1, 1)
        )
        epsilon_box = SliderBox(
            "Epsilon (Potential Depth used for Lennard-Jones force between Molecules) (E increase, D decrease)",
            0, 10, 1, 0.1, self.game_area.set_epsilon
        )
        sigma_box = SliderBox(
            "Sigma (Potential Distance used for Lennard-Jones force between Molecules) (R increase, F decrease)",
            0.1, 3, 1, 0.01, self.game_area.set_sigma
        )
        delta_box = SliderBox(
            "Delta (Timestep update for Verlet's Algorithm) (T increase, G decrease)",
            0, 1, 1 / 60.0, 1 / 60.0, self.game_area.set_delta
        )
        speed_box = SliderBox(
            "Speed of Simulation (Y increase, H decrease)",
            0.1, 1, 1, 0.1, self.game_area.set_speed
        )
        size_box = SliderBox(
            "Size of Molecules (U increase, J decrease)",
            0.2, 1, 0.6, 0.05, self.game_area.set_size
        )
        
        # Add sliders to the grid layout in a 3x2 formation
        ui_panel.add_widget(gravity_box)
        ui_panel.add_widget(epsilon_box)
        ui_panel.add_widget(sigma_box)
        ui_panel.add_widget(delta_box)
        ui_panel.add_widget(speed_box)
        ui_panel.add_widget(size_box)
        
        self.game_area.gravity_slider = gravity_box.slider
        self.game_area.epsilon_slider = epsilon_box.slider
        self.game_area.sigma_slider = sigma_box.slider
        self.game_area.delta_slider = delta_box.slider
        self.game_area.speed_slider = speed_box.slider
        self.game_area.size_slider = size_box.slider


        return ui_panel
    
    def toggle_info(self, button, text):
        if button.hoverSource == 'Graphics/Query_Highlighted.png':
            button.hoverSource = 'Graphics/Query_On_Highlighted.png'
            button.defaultSource = 'Graphics/Query_On.png'
        else:
            button.hoverSource = 'Graphics/Query_Highlighted.png'
            button.defaultSource = 'Graphics/Query.png'
        button.source = button.hoverSource if button.use else button.defaultSource
        text.toggle_visibility()

    def toggle_sliders(self):
        """Toggle visibility of the slider panel."""
        if self.ui_panel_visible:
            self.ui_panel.opacity = 0  # Hide
            self.ui_panel_visible = False
            self.remove_glow_effect()
            # Keep hover disabled (no white square)
            self.presets_button.hoverSource = "Graphics/Presets.png"
        else:
            self.ui_panel.opacity = 1  # Show
            self.ui_panel_visible = True
            self.add_glow_effect()
            # Keep hover disabled to show glow properly
            self.presets_button.hoverSource = "Graphics/Presets.png"
            # Force button to show default image
            self.presets_button.source = self.presets_button.defaultSource
    
    def add_glow_effect(self):
        """Add a glowing blue-purple gradient effect to the presets button."""
        from kivy.graphics import Color, Ellipse, PushMatrix, PopMatrix, Rotate
        from kivy.animation import Animation
        
        # Store glow elements for updating
        self.glow_elements = []
        
        # Create glowing gradient layers around the button using ellipses for softer edges
        with self.presets_button.canvas.before:
            # Multiple layers of ellipses to create a gradient glow effect
            
            # Outer glow - deep purple (largest, most transparent)
            Color(0.6, 0.0, 1.0, 0.15)  # Purple
            glow1 = Ellipse(
                pos=(self.presets_button.x - 15, self.presets_button.y - 15),
                size=(self.presets_button.width + 30, self.presets_button.height + 30)
            )
            self.glow_elements.append(('ellipse', glow1, 15))
            
            # Second layer - purple
            Color(0.5, 0.2, 0.9, 0.2)
            glow2 = Ellipse(
                pos=(self.presets_button.x - 12, self.presets_button.y - 12),
                size=(self.presets_button.width + 24, self.presets_button.height + 24)
            )
            self.glow_elements.append(('ellipse', glow2, 12))
            
            # Third layer - blue-purple
            Color(0.3, 0.3, 1.0, 0.25)
            glow3 = Ellipse(
                pos=(self.presets_button.x - 9, self.presets_button.y - 9),
                size=(self.presets_button.width + 18, self.presets_button.height + 18)
            )
            self.glow_elements.append(('ellipse', glow3, 9))
            
            # Fourth layer - blue
            Color(0.2, 0.5, 1.0, 0.3)
            glow4 = Ellipse(
                pos=(self.presets_button.x - 6, self.presets_button.y - 6),
                size=(self.presets_button.width + 12, self.presets_button.height + 12)
            )
            self.glow_elements.append(('ellipse', glow4, 6))
            
            # Fifth layer - light blue
            Color(0.4, 0.7, 1.0, 0.35)
            glow5 = Ellipse(
                pos=(self.presets_button.x - 3, self.presets_button.y - 3),
                size=(self.presets_button.width + 6, self.presets_button.height + 6)
            )
            self.glow_elements.append(('ellipse', glow5, 3))
            
            # Innermost layer - bright cyan
            Color(0.5, 0.8, 1.0, 0.4)
            glow6 = Ellipse(
                pos=(self.presets_button.x - 1, self.presets_button.y - 1),
                size=(self.presets_button.width + 2, self.presets_button.height + 2)
            )
            self.glow_elements.append(('ellipse', glow6, 1))
        
        # Bind position updates
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
        """Create the bottom controls with switches and buttons (responsive sizing)."""
        # Make button row height scale with screen - 8% of screen height
        button_height = Window.height * 0.08
        bottom_row = BoxLayout(
            orientation='horizontal',
            size_hint=(0.9, None),
            height=button_height,
            pos_hint={'center_x': 0.5, 'center_y': 0.05}
        )

        # forces_container, _ = self.create_forces_switch()
        # forces_visible_container, _ = self.create_forces_visible_switch()
        self.presets_button = self.create_hover_button("Presets", self.toggle_sliders)
        # Disable hover effect initially - keep it same as default to show glow properly
        self.presets_button.hoverSource = "Graphics/Presets.png"
        self.use_forces_button = self.create_hover_button("Forces-Off", self.toggle_intermolecular_forces)
        self.see_forces_button = self.create_hover_button("Hide-Forces", self.toggle_forces_visible)
        self.clear_button = self.create_hover_button("Clear", self.clear_game_area)
        self.start_stop_button = self.create_hover_button("Start", self.toggle_simulation)
        self.verlet_button = self.create_hover_button("Verlet-Off", self.toggle_verlet_mode)
        self.back_button = self.create_hover_button("Back", self.go_back)

        # bottom_row.add_widget(forces_container)
        # bottom_row.add_widget(forces_visible_container)
        bottom_row.add_widget(self.presets_button)
        bottom_row.add_widget(self.use_forces_button)
        bottom_row.add_widget(self.see_forces_button)
        bottom_row.add_widget(self.start_stop_button)
        bottom_row.add_widget(self.clear_button)
        bottom_row.add_widget(self.verlet_button)
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
        # Buttons fill their container proportionally
        return HoverItem(
            size_hint=(1, 1),
            hoverSource=f"Graphics/{label}_Highlighted.png",
            defaultSource=f"Graphics/{label}.png",
            function=lambda x: callback()
        )
        
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
        """Toggle the simulation state."""
        if self.game_area.simulation_running:
            self.start_stop_button.hoverSource="Graphics/Start_Highlighted.png"
            self.start_stop_button.defaultSource="Graphics/Start.png"
            self.start_stop_button.source = self.start_stop_button.hoverSource if self.start_stop_button.use else self.start_stop_button.defaultSource
            self.game_area.stop_simulation()
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
        self.game_area.clear_widgets()
        self.game_area.molecules.clear()
        self.game_area.clear_bonds()

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