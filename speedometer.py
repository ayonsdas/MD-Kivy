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
