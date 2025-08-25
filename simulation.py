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
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle, Line
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

        # ------------------ RIGHT SIDE PANEL -------------------
        # Box that holds speedometer, CPU label, and Arduino graph
        self.right_panel = BoxLayout(
            orientation='vertical',
            size_hint=(0.25, 0.6),
            pos_hint={'right': 0.99, 'top': 0.94},
            spacing=8
        )

        # Speedometer at the top
        self.speedometer = Speedometer(performance_monitor=self.monitor)
        self.speedometer.size_hint = (0.57, 0.38)


        # CPU label below it
        self.cpu_usage_label = Label(
            text="[b]CPU % Usage[/b]",
            markup=True,
            font_size='14sp',
            color=(1, 1, 1, 1),
            size_hint=(1, 0.1),
            halign='center',
            valign='middle'
        )
        self.cpu_usage_label.bind(size=self.cpu_usage_label.setter('text_size'))

        # Arduino Graph + Label
        # self.arduino_graph = ArduinoGraph()
        # self.arduino_graph.size_hint = (1, 0.25)

        self.arduino_graph_label = Label(
            text="Arduino Energy Input",
            font_size='13sp',
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle',
            size_hint=(1, 0.1)
        )
        self.arduino_graph_label.bind(size=self.arduino_graph_label.setter('text_size'))

        # Add to right panel
        self.right_panel.add_widget(self.speedometer)
        self.right_panel.add_widget(self.cpu_usage_label)
        self.right_panel.add_widget(self.arduino_graph)
        self.right_panel.add_widget(self.arduino_graph_label)

        

        # Add right panel to root layout
        self.root.add_widget(self.right_panel)

#        label stays aligned under the graph even if it moves
        def update_arduino_label_pos(*args):
            self.arduino_graph_label.pos = (
            self.arduino_graph.x + 40,
            self.arduino_graph.y - 29
    )
        self.arduino_graph.bind(pos=update_arduino_label_pos)


        # Arduino label: get it from the same game_area
        self.arduino_label = self.game_area.arduino_data_label
        self.root.add_widget(self.arduino_label)  #  to root, not inside game_area



        #  the preset selector spinner in the control section
        self.add_preset_spinner(self.root)

        #  other UI elements (Sliders, buttons, etc.)
        self.add_ui_elements(self.root)

        # Graphs Container (Right Side, Slightly Smaller)
        graph_container = BoxLayout(
            orientation='vertical',
            size_hint=(0.2, 0.6),  # width & height
            pos_hint={'right': 0.96, 'top': 0.93}  # slightly further right
        )

        # # CPU & Memory Graphs (Smaller & Properly Positioned)
        # self.cpu_graph = CPUUsageGraph(monitor=self.monitor, size_hint=(1, 0.5))
        # self.memory_graph = MemoryUsageGraph(monitor=self.monitor, size_hint=(1, 0.5))


    

        # Graphs to the Root Layout (NOT Covered by Background)
        self.root.add_widget(graph_container)

        #  Add Everything to the Screen
        self.add_widget(self.root)


    def add_background(self, root):
        """Add a grey background and bind its size/position to root."""
        with root.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.ui_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_ui_background, size=self.update_ui_background)

    def update_ui_background(self, instance, *args):
        """Update background dynamically when the window size changes."""
        self.ui_rect.pos = instance.pos
        self.ui_rect.size = instance.size

    def add_preset_spinner(self, root):
        """Add the preset spinner to the bottom control section."""
        self.spinner_row = BoxLayout(orientation='horizontal', size_hint=(0.4, None), height=40, pos_hint={'center_x': 0.3, 'y': 0.085})

        # Label for the preset spinner
        # preset_label = Label(text="Presets:", size_hint=(0.4, 1, size_hint=(None, None)), font_size=14)
        self.preset_label = HoverItem(size_hint=(1, 1), 
                                      hoverSource="Graphics/Presets.png", 
                                      defaultSource="Graphics/Presets.png", 
                                      function=lambda x : None)
        
        self.spinner_row.add_widget(self.preset_label)

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
        ui_panel = self.create_sliders()
        bottom_row = self.create_bottom_controls()
        root.add_widget(ui_panel)
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


    def mPos(self, window, pos):
        self.cursOr.pos = (pos[0] - Window.width * 0.01, pos[1] - Window.height * 0.01)

    # Defines call Back Function HEre for Slider Box!!!!
    def create_sliders(self):
        """Create the slider UI for gravity, delta, sigma, epsilon, speed, and size."""
        ui_panel = GridLayout(cols=3,
                              rows=2,
                              size_hint=(0.8, 0.15),
                              pos_hint={'center_x': 0.5, 'center_y': 0.22},
                              spacing=(20, 20),  # Horizontal and vertical spacing (in pixels)
                              padding=[10, 10, 10, 10]  # Padding around the entire grid (left, top, right, bottom))
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


    def create_bottom_controls(self):
        """Create the bottom controls with switches and buttons."""
        bottom_row = BoxLayout(orientation='horizontal', size_hint=(0.9, None), height=50, pos_hint={'center_x': 0.5, 'center_y': 0.05})

        # forces_container, _ = self.create_forces_switch()
        # forces_visible_container, _ = self.create_forces_visible_switch()
        self.use_forces_button = self.create_hover_button("Forces-Off", self.toggle_intermolecular_forces)
        self.see_forces_button = self.create_hover_button("Hide-Forces", self.toggle_forces_visible)
        self.clear_button = self.create_hover_button("Clear", self.clear_game_area)
        self.start_stop_button = self.create_hover_button("Start", self.toggle_simulation)
        self.verlet_button = self.create_hover_button("Verlet-Off", self.toggle_verlet_mode)
        self.back_button = self.create_hover_button("Back", self.go_back)

        # bottom_row.add_widget(forces_container)
        # bottom_row.add_widget(forces_visible_container)
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
        """Helper to create buttons with hover effects."""
        return HoverItem(
            size_hint=(1, None),
            height=50,
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
        """Add labels to display simulation stats."""
        self.game_area.total_energy_label = Label(text="Total Energy: 0", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.18, 'center_y': 0.95})
        self.game_area.temperature_label = Label(text="Temperature: 0", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.51, 'center_y': 0.95})
        self.game_area.pressure_label = Label(text="Pressure: 0", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.84, 'center_y': 0.95})

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