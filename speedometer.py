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

        # current needle angle (starts at 135 deg)
        self.current_angle = 135

        # center label
        self.percent_label = Label(
            text="0%",
            font_size=30,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(100, 30),
        )
        self.add_widget(self.percent_label)

        Clock.schedule_interval(self.update_speedometer, 0.02)  # higher FPS = smoother

    def update_speedometer(self, dt):
        self.canvas.clear()
        cpu_percent = min(self.monitor.get_cpu_usage(), 100)

        # calculate target angle
        target_angle = 135 + (cpu_percent * 270 / 100)

        # smooth step (easing) very nice one
        self.current_angle += (target_angle - self.current_angle) * 0.1

        cx = self.x + self.width / 2
        cy = self.y + self.height / 2

        with self.canvas:
            # glowing thing
            Color(0.2, 0.6, 1.0, 0.15)
            Ellipse(pos=(self.x - 10, self.y - 10), size=(self.width + 20, self.height + 20))

            # outer dial
            Color(0.1, 0.3, 0.6, 1)
            Ellipse(pos=self.pos, size=self.size)

            # inner circle
            Color(0, 0, 0, 1)
            Ellipse(pos=(self.x + 10, self.y + 10), size=(self.width - 20, self.height - 20))

            # tick Marks and Labels
            for i in range(11):
                tick_angle = 135 + (i * 27)
                rad = math.radians(tick_angle)
                x1 = cx + 90 * math.cos(rad)
                y1 = cy + 90 * math.sin(rad)
                x2 = cx + 105 * math.cos(rad)
                y2 = cy + 105 * math.sin(rad)
                Color(1, 1, 1, 1)
                Line(points=[x1, y1, x2, y2], width=1.5)

                label = CoreLabel(text=str(i * 10), font_size=16)
                label.refresh()
                texture = label.texture
                lx = cx + 120 * math.cos(rad) - texture.size[0] / 2
                ly = cy + 120 * math.sin(rad) - texture.size[1] / 2
                Rectangle(texture=texture, pos=(lx, ly), size=texture.size)

            # needle params
            rad = math.radians(self.current_angle)
            nx = cx + 90 * math.cos(rad)
            ny = cy + 90 * math.sin(rad)

            Color(1, 0, 0, 0.15)
            Line(points=[cx, cy, nx, ny], width=10)

            Color(1, 0, 0, 1)
            Line(points=[cx, cy, nx, ny], width=3)

            Color(1, 0, 0, 1)
            Ellipse(pos=(cx - 6, cy - 6), size=(12, 12))

        # label update
        self.percent_label.text = f"{int(cpu_percent)}%"
        self.percent_label.pos = (cx - 25, cy - 15)
