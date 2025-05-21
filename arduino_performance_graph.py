from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle
from kivy.clock import Clock
from kivy.uix.label import Label
import math

class ArduinoGraph(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (300, 100)
        self.pos_hint = {'right': 0.99, 'y': 0.4}

        self.max_points = 300  # Number of points in the graph
        self.data_points = [0] * self.max_points

        # Motion label
        self.motion_label = Label(
            text="Motion: Low",
            size_hint=(None, None),
            size=(150, 30),
            pos=(10, self.height - 30),  # near top left
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        self.add_widget(self.motion_label)

        Clock.schedule_interval(self.update_graph, 0.01) # from 0.05

    def add_data_point(self, value):
        # Smoothing: weighted average with previous value
        if self.data_points:
            value = 0.6 * self.data_points[-1] + 0.4 * value

        self.data_points.pop(0)
        self.data_points.append(value)

    def update_graph(self, dt):
        # update the graph to return to 0 when not shaken!!!!!!!!!!!
        self.canvas.clear()

        magnitude = self.data_points[-1] * 16384.0  # restore original range to decide color

        with self.canvas:
            # Background
            Color(0.1, 0.1, 0.1, 1)
            Rectangle(pos=self.pos, size=self.size)

            # Dynamic color based on motion strength
            if magnitude < 2000:
                Color(0.3, 1, 0.3, 1)  # Green
            elif magnitude < 10000:
                Color(1, 1, 0.3, 1)  # Yellow
            else:
                Color(1, 0.4, 0.4, 1)  # Red

            # Smooth line using midpoint interpolation
            points = []
            prev_y = self.y + (self.data_points[0] * self.height / 4)
            for i in range(1, len(self.data_points)):
                x = self.x + i
                current_y = self.y + (self.data_points[i] * self.height / 4)
                mid_y = (prev_y + current_y) / 2
                points += [x, mid_y]
                prev_y = current_y

            if len(points) >= 4:
                Line(points=points, width=1.5)

        # Reposition label in case size or position changed
        self.motion_label.pos = (self.x + 10, self.y + self.height - 30)

    def feed_arduino(self, x, y, z):
        magnitude = math.sqrt(x**2 + y**2 + z**2)
        normalized = magnitude / 16384.0
        self.add_data_point(normalized)

        # Update label based on magnitude
        if magnitude < 2000:
            level = "Low"
        elif magnitude < 10000:
            level = "Medium"
        else:
            level = "Strong"
        self.motion_label.text = f"Motion: {level}"
