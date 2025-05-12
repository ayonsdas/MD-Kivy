<<<<<<< HEAD
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
from kivy.uix.label import Label
import math

class Speedometer(Widget):
    def __init__(self, performance_monitor, **kwargs):
        super().__init__(**kwargs)
        self.monitor = performance_monitor
        self.size_hint = (None, None)
        self.size = (300, 300)
        self.pos_hint = {'right': 0.99, 'top': 0.92}

        # Center label
        self.percent_label = Label(
            text="0%",
            font_size=30,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(100, 30),
        )
        self.add_widget(self.percent_label)

        Clock.schedule_interval(self.update_speedometer, 0.1)

    def update_speedometer(self, dt):
        self.canvas.clear()
        cpu_percent = min(self.monitor.get_cpu_usage(), 100)
        angle = 135 + (cpu_percent * 270 / 100)  # 135 to 405 degrees

        with self.canvas:
            # Outer frame
            Color(0.1, 0.3, 0.6, 1)
            Ellipse(pos=self.pos, size=self.size)

            # Inner circle
            Color(0, 0, 0, 1)
            Ellipse(pos=(self.x + 10, self.y + 10), size=(self.width - 20, self.height - 20))

            # Tick marks
            for i in range(11):
                tick_angle = 135 + (i * 27)
                rad = math.radians(tick_angle)
                x1 = self.center_x + 90 * math.cos(rad)
                y1 = self.center_y + 90 * math.sin(rad)
                x2 = self.center_x + 105 * math.cos(rad)
                y2 = self.center_y + 105 * math.sin(rad)
                Color(1, 1, 1, 1)
                Line(points=[x1, y1, x2, y2], width=1.5)

                # Labels
                label = CoreLabel(text=str(i * 10), font_size=16)
                label.refresh()
                texture = label.texture
                lx = self.center_x + 120 * math.cos(rad) - texture.size[0] / 2
                ly = self.center_y + 120 * math.sin(rad) - texture.size[1] / 2
                Rectangle(texture=texture, pos=(lx, ly), size=texture.size)

            # Needle
            needle_rad = math.radians(angle)
            nx = self.center_x + 90 * math.cos(needle_rad)
            ny = self.center_y + 90 * math.sin(needle_rad)

            # Needle glow
            Color(1, 0, 0, 0.3)
            Line(points=[self.center_x, self.center_y, nx, ny], width=6)

            # Needle main
            Color(1, 0, 0, 1)
            Line(points=[self.center_x, self.center_y, nx, ny], width=3)

            # Center dot
            Color(1, 0, 0, 1)
            Ellipse(pos=(self.center_x - 6, self.center_y - 6), size=(12, 12))

        # Label update
        self.percent_label.text = f"{int(cpu_percent)}%"
        self.percent_label.pos = (self.center_x - 25, self.center_y - 15)
=======
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
from kivy.uix.label import Label
import math

class Speedometer(Widget):
    def __init__(self, performance_monitor, **kwargs):
        super().__init__(**kwargs)
        self.monitor = performance_monitor
        self.size_hint = (None, None)
        self.size = (300, 300)  # Bigger dial
        self.pos_hint = {'right': 0.99, 'top': 0.92}  # Top-right

        self.percent_label = Label(
            text="CPU: 0%",
            font_size=30,
            color=(1, 0, 0, 1),
            size_hint=(None, None),
            size=(100, 30),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.add_widget(self.percent_label)
        Clock.schedule_interval(self.update_speedometer, 0.1)

    def update_speedometer(self, dt):
        self.canvas.clear()
        with self.canvas:
            # Outer glow
            Color(0.2, 0.5, 1, 0.2)
            Ellipse(pos=(self.x - 15, self.y - 15), size=(self.width + 30, self.height + 30))

            # Outer blue frame
            Color(0.1, 0.3, 0.6, 1)
            Ellipse(pos=self.pos, size=self.size)

            # Inner black circle
            Color(0, 0, 0, 1)
            Ellipse(pos=(self.x + 10, self.y + 10), size=(self.width - 20, self.height - 20))

            # Tick marks and number labels
            steps = 10
            for i in range(steps + 1):
                value = i * 10
                angle = 135 - i * (270 / steps)
                rad = math.radians(angle)

                # Ticks
                x1 = self.center_x + 75 * math.cos(rad)
                y1 = self.center_y + 75 * math.sin(rad)
                x2 = self.center_x + 85 * math.cos(rad)
                y2 = self.center_y + 85 * math.sin(rad)
                Color(1, 1, 1, 1)
                Line(points=[x1, y1, x2, y2], width=1.5)

                # Labels
                label = CoreLabel(text=str(value), font_size=18)
                label.refresh()
                texture = label.texture
                radius = self.width / 2 - 20  # Pull labels closer to edge
                lx = self.center_x + radius * math.cos(rad) - texture.size[0] / 2
                ly = self.center_y + radius * math.sin(rad) - texture.size[1] / 2
                Rectangle(texture=texture, pos=(lx, ly), size=texture.size)

            # CPU percentage
            cpu_percent = self.monitor.get_cpu_usage()
            self.percent_label.text = f"{int(cpu_percent)}%"
            self.percent_label.pos = (self.center_x - 35, self.center_y - 20)

            # Needle (glow + sharp red)
            angle = 135 - (cpu_percent * 270 / 100)
            rad = math.radians(angle)
            x_end = self.center_x + 90 * math.cos(rad)  # longer needle
            y_end = self.center_y + 90 * math.sin(rad)

            # Glow behind needle
            Color(1, 0, 0, 0.3)
            Line(points=[self.center_x, self.center_y, x_end, y_end], width=6)

            # Main needle
            Color(1, 0, 0, 1)
            Line(points=[self.center_x, self.center_y, x_end, y_end], width=3)

            # Center glowing dot
            Color(1, 0, 0, 1)
            Ellipse(pos=(self.center_x - 6, self.center_y - 6), size=(12, 12))
>>>>>>> 66de32636f7bcaf91b565dd16c2168a2759d80cb
