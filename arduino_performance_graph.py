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

        # make it fit nicely
        self.size_hint = (0.6, 0.25)     # 60% width, 25% height
        self.pos_hint = {'right': 0.98}

        self.max_points = 300
        self.data_points = [0] * self.max_points

        # label - font gets updated in update_label_position
        self.motion_label = Label(
            text="Motion: Low",
            size_hint=(None, None),
            color=(1, 1, 1, 1),
            font_size='12sp'
        )
        self.add_widget(self.motion_label)

        self.bind(size=self.update_label_position, pos=self.update_label_position)
        Clock.schedule_interval(self.update_graph, 0.02)

    def update_label_position(self, *args):
        # label gets moved and scaled so it never overflows
        x_pad  = max(6, int(self.width  * 0.04))
        y_pad  = max(14, int(self.height * 0.12))
        self.motion_label.font_size = max(10, int(self.height * 0.14))
        self.motion_label.texture_update()
        self.motion_label.pos = (self.x + x_pad, self.top - y_pad)

    def add_data_point(self, value):
        # Smooth transitions for professional appearance
        if self.data_points:
            value = 0.3 * self.data_points[-1] + 0.7 * value  # Balanced smoothing
        self.data_points.pop(0)
        self.data_points.append(value)

    def update_graph(self, dt):
        self.canvas.clear()

        height = self.height
        width = self.width
        
        # Current intensity (0.0 = rest, 1.0 = strong shake)
        intensity = self.data_points[-1]

        with self.canvas:
            # Background
            Color(*self.background_color)
            Rectangle(pos=self.pos, size=self.size)

            # Dynamic color gradient based on shake intensity
            if intensity < 0.05:  # Very low activity (at rest)
                Color(0.3, 1, 0.3, 1)  # Green
            elif intensity < 0.15:  # Light movement
                Color(0.6, 1, 0.3, 1)  # Light green
            elif intensity < 0.35:  # Moderate shake
                Color(1, 1, 0.3, 1)  # Yellow
            elif intensity < 0.60:  # Strong shake
                Color(1, 0.5, 0.2, 1)  # Orange
            else:  # Very strong shake (60%+)
                Color(1, 0.2, 0.2, 1)  # Red

            # graph line - height shows how much shaking
            points = []
            for i in range(1, len(self.data_points)):
                x = self.x + (i / self.max_points) * width
                # Full height utilization: 0.0 = bottom, 1.0 = top
                y = self.y + self.data_points[i] * height
                points.extend([x, y])

            if len(points) >= 4:
                Line(points=points, width=2.0)  # Slightly thicker for visibility

        self.update_label_position()

    def feed_arduino(self, x, y, z, shake_intensity=0):
        """
        Feed Arduino data and shake intensity.
        shake_intensity: 0-100 value representing shake strength (calculated from delta)
        """
        # use the shake intensity result from game_layout
        # Normalize to 0.0-1.0 range for graph height
        normalized = min(shake_intensity / 100.0, 1.0)
        
        self.add_data_point(normalized)

        # change label based on shake intensity (adjusted thresholds)
        if shake_intensity < 10:  # Very minimal movement
            level = "Low"
        elif shake_intensity < 30:  # Moderate shaking
            level = "Medium"
        else:  # Strong shaking
            level = "Strong"
        self.motion_label.text = f"Shake: {level} ({shake_intensity:.0f}%)"
