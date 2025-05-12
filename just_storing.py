  
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
from kivy.clock import Clock   # adde dnew import
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle, Line
import psutil
from game_layout import GameLayout
from HoverItem import HoverItem
from TextBlurb import TextBlurb
from CustomSlider import CustomSlider
from SliderBox import SliderBox
from SpinnerBox import SpinnerBox




class GameScreen(Screen):
    
    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        
        self.name = "GameScreen"
        
        # Root layout for the entire screen
        self.root = FloatLayout()

        Clock.schedule_interval(self.monitor_performance, 1)

######################################################################
        # performance labels
        self.cpu_label = Label(text="CPU Usage: 0%", size_hint=(0.2, 0.05), pos_hint={'x': 0.82, 'y': 0.7})
        self.memory_label = Label(text="Memory Usage: 0 MB", size_hint=(0.2, 0.05), pos_hint={'x': 0.82, 'y': 0.65})
        self.gpu_label = Label(text="GPU Usage: 0%", size_hint=(0.2, 0.05), pos_hint={'x': 0.82, 'y': 0.6})

        # labels to the sidebar UI
        self.root.add_widget(self.cpu_label)
        self.root.add_widget(self.memory_label)
        self.root.add_widget(self.gpu_label)

        # schedule performance monitoring to update every second
        # (removed duplicate scheduling)



def monitor_performance(self, dt):
        """Update CPU, Memory, and GPU stats in real-time."""
        import psutil
        import subprocess

        psutil.cpu_percent(interval=None)
        cpu_usage = psutil.cpu_percent(interval=1.0, percpu=False)  # Instant CPU usage
        memory_usage = psutil.virtual_memory().used / (1024 * 1024)  # Convert bytes to MB

        # GPU Usage (for NVIDIA)
        try:
            gpu_result = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
                capture_output=True, text=True
            )
            gpu_usage = float(gpu_result.stdout.strip()) if gpu_result.stdout.strip().isdigit() else 0
        except Exception:
            gpu_usage = 0  # Skip if no GPU detected

        # Ensure UI labels exist before updating them
        if hasattr(self, "cpu_label"):
            self.cpu_label.text = f"CPU Usage: {cpu_usage:.2f}%"
        if hasattr(self, "memory_label"):
            self.memory_label.text = f"Memory Usage: {memory_usage:.2f} MB"
        if hasattr(self, "gpu_label"):
            self.gpu_label.text = f"GPU Usage: {gpu_usage:.2f}%"

        # Log data when atoms change
        current_atoms = len(self.game_area.molecules)  # Count atoms
        self.log_performance(current_atoms, cpu_usage, memory_usage, gpu_usage)


    def log_performance(self, atoms, cpu, memory, gpu):
        
        """Logs system performance when atom count changes."""
        with open("performance_log.txt", "a") as log:
            log.write(f"Atoms: {atoms}, CPU: {cpu:.2f}%, Memory: {memory:.2f} MB, GPU: {gpu:.2f}%\n")

        print(f" Logged: Atoms: {atoms}, CPU: {cpu:.2f}%, Memory: {memory:.2f} MB, GPU: {gpu:.2f}%")







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
from kivy.clock import Clock
from kivy_garden.graph import Graph, MeshLinePlot
from game_layout import GameLayout
from HoverItem import HoverItem
from TextBlurb import TextBlurb
from CustomSlider import CustomSlider
from SliderBox import SliderBox
from SpinnerBox import SpinnerBox
from simulation import GameScreen
from start_screen import StartScreen
from performance_monitor import PerformanceMonitor

class GraphWidget(BoxLayout):
    def __init__(self, monitor, **kwargs):
        super().__init__(**kwargs)
        self.monitor = monitor  # Performance monitor instance

        #reate the Graph Widget
        self.graph = Graph(
            xlabel='Time', ylabel='CPU Usage (%)', x_ticks_minor=5, x_ticks_major=10,
            y_ticks_major=10, y_grid_label=True, x_grid_label=True, 
            xmin=0, xmax=60, ymin=0, ymax=100,  # Set limits
            border_color=[1, 1, 1, 1]
        )

        # reate the CPU usage line plot
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])  # Red Line
        self.graph.add_plot(self.plot)

        # Add the Graph to Layout
        self.add_widget(Label(text="CPU Usage", size_hint=(0.2, 1)))
        self.add_widget(self.graph)

        # Schedule updates every second
        Clock.schedule_interval(self.update_graph, 1)

        # Store CPU values for plotting
        self.cpu_values = []

    def update_graph(self, dt):
        """Update the CPU graph every second."""
        cpu_usage = self.monitor.get_cpu_usage()  # Fetch latest CPU usage
        self.cpu_values.append(cpu_usage)

        # Keep only last 60 values (1 min)
        if len(self.cpu_values) > 60:
            self.cpu_values.pop(0)

        # Update Plot Data
        self.plot.points = [(i, val) for i, val in enumerate(self.cpu_values)]

class WindowManager(ScreenManager):
    
    def __init__(self, **kwargs):
        """Set up WindowManager"""
        
        self.start_screen = kwargs.pop("start_screen")
        self.game_screen = kwargs.pop("game_screen")
        super().__init__(**kwargs)
        
        self.add_widget(self.start_screen)
        self.add_widget(self.game_screen)
        
        # self.current = self.start_screen.name
    
    def start_game(self, name):
        if name == self.start_screen.name:
            # self.game_screen.reset()
            self.current = self.game_screen.name
            
    def go_back(self, name):
        if name == self.game_screen.name:
            self.current = self.start_screen.name

class GameApp(App):

    def build(self):
        
        self.start_screen = StartScreen()
        self.game_screen = GameScreen()
        self.window_manager = WindowManager(start_screen=self.start_screen, game_screen=self.game_screen)
        return self.window_manager


if __name__ == "__main__":
    GameApp().run()





Very useful   WE NEED THIS
    class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create Performance Monitor
        self.monitor = PerformanceMonitor()

        # Use FloatLayout to position elements freely
        self.layout = FloatLayout()

        # 🎮 Full-Screen Game Area
        self.game_area = GameLayout(size_hint=(1, 1))  # FULL SCREEN
        self.layout.add_widget(self.game_area)

        # CPU Graph (Smaller, in Top-Right Corner)
        self.cpu_graph = CPUUsageGraph(monitor=self.monitor, size_hint=(0.3, 0.3))  # 30% Width, 30% Height
        self.graph_container = AnchorLayout(anchor_x='right', anchor_y='top')
        self.graph_container.add_widget(self.cpu_graph)

        # Add graph container to main layout
        self.layout.add_widget(self.graph_container)

        self.add_widget(self.layout)












sliders \



from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        
        self.monitor = PerformanceMonitor()

    
        self.layout = BoxLayout(orientation='horizontal')  # Side-by-side game + graph

        
        self.game_area = GameLayout(size_hint=(0.7, 1))  # Takes 70% of the width
        self.layout.add_widget(self.game_area)

        
        self.right_panel = BoxLayout(orientation='vertical', size_hint=(0.3, 1))  # 30% width for graph/sliders

        
        self.cpu_graph = CPUUsageGraph(monitor=self.monitor, size_hint=(1, 0.7))  # 70% height
        self.right_panel.add_widget(self.cpu_graph)

        
        self.slider_container = BoxLayout(orientation='vertical', size_hint=(1, 0.3))  # 30% height
        self.slider1 = CustomSlider(min=0, max=100, value=50, size_hint=(1, 0.5))
        self.slider2 = CustomSlider(min=0, max=200, value=100, size_hint=(1, 0.5))
        self.slider_container.add_widget(self.slider1)
        self.slider_container.add_widget(self.slider2)

        
        self.right_panel.add_widget(self.slider_container)

        
        self.layout.add_widget(self.right_panel)

        self.add_widget(self.layout)
