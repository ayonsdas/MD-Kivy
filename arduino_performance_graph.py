from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.properties import ListProperty
import math

class ArduinoGraph(Widget):
    background_color = ListProperty([0.1, 0.1, 0.1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Make it responsive
        self.size_hint = (0.6, 0.25)     # 90% width of container, 25% height
        self.pos_hint = {'right': 0.98}

        self.max_points = 300
        self.data_points = [0] * self.max_points

        # Add motion label
        self.motion_label = Label(
            text="Motion: Low",
            size_hint=(None, None),
            color=(1, 1, 1, 1),
            font_size='15sp'
        )
        self.add_widget(self.motion_label)

        self.bind(size=self.update_label_position, pos=self.update_label_position)
        Clock.schedule_interval(self.update_graph, 0.02)

    def update_label_position(self, *args):
        self.motion_label.pos = (self.x + 10, self.top - 30)

    def add_data_point(self, value):
        if self.data_points:
            value = 0.6 * self.data_points[-1] + 0.4 * value
        self.data_points.pop(0)
        self.data_points.append(value)

    def update_graph(self, dt):
        self.canvas.clear()

        magnitude = self.data_points[-1] * 16384.0
        height = self.height
        width = self.width

        with self.canvas:
            # Background
            Color(*self.background_color)
            Rectangle(pos=self.pos, size=self.size)

            # Motion color
            if magnitude < 2000:
                Color(0.3, 1, 0.3, 1)
            elif magnitude < 10000:
                Color(1, 1, 0.3, 1)
            else:
                Color(1, 0.4, 0.4, 1)

            # Scaled points
            points = []
            for i in range(1, len(self.data_points)):
                x = self.x + (i / self.max_points) * width
                y = self.y + self.data_points[i] * (height / 2)
                points.extend([x, y])

            if len(points) >= 4:
                Line(points=points, width=1.5)

        self.update_label_position()

    def feed_arduino(self, x, y, z):
        magnitude = math.sqrt(x**2 + y**2 + z**2)
        normalized = magnitude / 16384.0
        self.add_data_point(normalized)

        # Update label
        if magnitude < 2000:
            level = "Low"
        elif magnitude < 10000:
            level = "Medium"
        else:
            level = "Strong"
        self.motion_label.text = f"Motion: {level}"
