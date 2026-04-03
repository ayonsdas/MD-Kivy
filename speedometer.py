from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
from kivy.uix.label import Label
from kivy.core.window import Window
import math
import time

class Speedometer(Widget):
    def __init__(self, performance_monitor, **kwargs):
        super().__init__(**kwargs)
        self.monitor = performance_monitor
        # Allow parent layouts to size this widget via size_hint.
        # We'll render a circular dial inside the allocated rect without forcing self.size.
        self.size_hint = self.size_hint or (None, None)
        if self.size_hint == (None, None):
            # default standalone size when not managed by a layout
            self.size = (200, 200)
        self.pos_hint = getattr(self, 'pos_hint', {'right': 0.99, 'top': 0.94})
        self.current_angle = 135

        self.percent_label = Label(
            text="0%",
            font_size=Window.height * 0.025,  # 2.5% of screen height
            color=(1, 1, 1, 1),
            bold=True,
            size_hint=(None, None),
            size=(100, 30)
        )
        self.add_widget(self.percent_label)

        Clock.schedule_interval(self.update_speedometer, 0.02)

    # Do not mutate self.size when managed by a layout; instead draw within a square
    # that fits inside the current bounding box in update_speedometer.

    def get_dynamic_color(self, percent):
        """Green → Yellow → Red based on percent."""
        if percent < 50:
            r = percent / 50
            g = 1
        else:
            r = 1
            g = 1 - ((percent - 50) / 50)
        return r, g, 0

    def update_speedometer(self, dt):
        self.canvas.clear()
        # Use target usage (simulation metrics) instead of actual CPU
        # This reflects Arduino shake intensity + molecule activity
        cpu_percent = min(self.monitor._target_usage, 100)
        target_angle = 135 + (cpu_percent * 270 / 100)
        self.current_angle += (target_angle - self.current_angle) * 0.1

        # Draw in a centered square within the current widget rect
        side = min(self.width, self.height)
        radius = side / 2.0
        cx = self.x + self.width / 2.0
        cy = self.y + self.height / 2.0
        square_x = cx - radius
        square_y = cy - radius
        r, g, b = self.get_dynamic_color(cpu_percent)

        tick_outer = radius * 0.9
        tick_inner = radius * 0.75
        label_radius = radius * 0.65
        needle_length = radius * 0.8

        with self.canvas:
            # Multi-layer glowing ring — all offsets proportional to radius so they
            # scale correctly on small (800 p) and large (4K) screens alike.
            pulse = 0.5 + 0.5 * math.sin(time.time() * 2)
            base_alpha = 0.18 + (cpu_percent / 100) * 0.45 * pulse

            g1 = int(radius * 0.55)   # outermost glow margin
            g2 = int(radius * 0.41)
            g3 = int(radius * 0.27)
            g4 = int(radius * 0.18)
            g5 = int(radius * 0.09)   # innermost glow margin

            Color(r, g, b, base_alpha * 0.35)
            Ellipse(pos=(square_x - g1, square_y - g1), size=(side + g1 * 2, side + g1 * 2))
            Color(r, g, b, base_alpha * 0.50)
            Ellipse(pos=(square_x - g2, square_y - g2), size=(side + g2 * 2, side + g2 * 2))
            Color(r, g, b, base_alpha * 0.65)
            Ellipse(pos=(square_x - g3, square_y - g3), size=(side + g3 * 2, side + g3 * 2))
            Color(r, g, b, base_alpha * 0.80)
            Ellipse(pos=(square_x - g4, square_y - g4), size=(side + g4 * 2, side + g4 * 2))
            Color(r, g, b, base_alpha * 0.95)
            Ellipse(pos=(square_x - g5, square_y - g5), size=(side + g5 * 2, side + g5 * 2))

            # Outer dial
            Color(0.1, 0.3, 0.6, 1)
            Ellipse(pos=(square_x, square_y), size=(side, side))

            # Inner black circle — border also proportional
            border = int(radius * 0.09)
            Color(0, 0, 0, 1)
            Ellipse(pos=(square_x + border, square_y + border),
                    size=(side - border * 2, side - border * 2))

            # Ticks and labels
            for i in range(11):
                angle = 135 + (i * 27)
                rad = math.radians(angle)
                x1 = cx + tick_inner * math.cos(rad)
                y1 = cy + tick_inner * math.sin(rad)
                x2 = cx + tick_outer * math.cos(rad)
                y2 = cy + tick_outer * math.sin(rad)
                Color(1, 1, 1, 1)
                Line(points=[x1, y1, x2, y2], width=1.5)

                # Scale font size proportionally to speedometer size (bold)
                font_size = int(side * 0.055)  # 5.5% of speedometer diameter
                label = CoreLabel(text=str(i * 10), font_size=font_size, bold=True)
                label.refresh()
                texture = label.texture
                lx = cx + label_radius * math.cos(rad) - texture.size[0] / 2
                ly = cy + label_radius * math.sin(rad) - texture.size[1] / 2
                Rectangle(texture=texture, pos=(lx, ly), size=texture.size)

            # Needle
            rad = math.radians(self.current_angle)
            nx = cx + needle_length * math.cos(rad)
            ny = cy + needle_length * math.sin(rad)
            Color(r, g, 0, base_alpha)
            Line(points=[cx, cy, nx, ny], width=10)

            Color(r, g, 0, 1)
            Line(points=[cx, cy, nx, ny], width=3)

            # Center dot — proportional to dial size
            dot_r = int(radius * 0.055)
            Color(r, g, 0, 1)
            Ellipse(pos=(cx - dot_r, cy - dot_r), size=(dot_r * 2, dot_r * 2))

        # Percent label: center it on the dial using its own size
        self.percent_label.text = f"{int(cpu_percent)}%"
        self.percent_label.font_size = int(side * 0.12)
        self.percent_label.bold = True
        lw = self.percent_label.texture_size[0] if self.percent_label.texture else side * 0.12
        lh = self.percent_label.texture_size[1] if self.percent_label.texture else side * 0.12
        self.percent_label.pos = (cx - lw / 2, cy - lh / 2 - int(radius * 0.18))





# good looking but no diff color glow

# from kivy.uix.widget import Widget
# from kivy.graphics import Color, Ellipse, Line, Rectangle
# from kivy.clock import Clock
# from kivy.core.text import Label as CoreLabel
# from kivy.uix.label import Label
# import math
# import time  # needed for pulsing effect

# class Speedometer(Widget):
#     def __init__(self, performance_monitor, **kwargs):
#         super().__init__(**kwargs)
#         self.monitor = performance_monitor
#         self.size_hint = (None, None)
#         self.size = (300, 300)
#         self.pos_hint = {'right': 0.99, 'top': 0.92}

#         self.current_angle = 135  # start angle for needle

#         self.percent_label = Label(
#             text="0%",
#             font_size=30,
#             color=(1, 1, 1, 1),
#             size_hint=(None, None),
#             size=(100, 30),
#         )
#         self.add_widget(self.percent_label)

#         Clock.schedule_interval(self.update_speedometer, 0.02)  # smooth update

#     def update_speedometer(self, dt):
#         self.canvas.clear()
#         cpu_percent = min(self.monitor.get_cpu_usage(), 100)
#         target_angle = 135 + (cpu_percent * 270 / 100)
#         self.current_angle += (target_angle - self.current_angle) * 0.1

#         cx = self.x + self.width / 2
#         cy = self.y + self.height / 2

#         with self.canvas:
#             # Outer blue glow
#             Color(0.2, 0.6, 1.0, 0.15)
#             Ellipse(pos=(self.x - 10, self.y - 10), size=(self.width + 20, self.height + 20))

#             # Outer dial
#             Color(0.1, 0.3, 0.6, 1)
#             Ellipse(pos=self.pos, size=self.size)

#             # Inner black circle
#             Color(0, 0, 0, 1)
#             Ellipse(pos=(self.x + 10, self.y + 10), size=(self.width - 20, self.height - 20))

#             # Tick marks + numbers
#             for i in range(11):
#                 tick_angle = 135 + (i * 27)
#                 rad = math.radians(tick_angle)
#                 x1 = cx + 90 * math.cos(rad)
#                 y1 = cy + 90 * math.sin(rad)
#                 x2 = cx + 105 * math.cos(rad)
#                 y2 = cy + 105 * math.sin(rad)
#                 Color(1, 1, 1, 1)
#                 Line(points=[x1, y1, x2, y2], width=1.5)

#                 label = CoreLabel(text=str(i * 10), font_size=16)
#                 label.refresh()
#                 texture = label.texture
#                 lx = cx + 120 * math.cos(rad) - texture.size[0] / 2
#                 ly = cy + 120 * math.sin(rad) - texture.size[1] / 2
#                 Rectangle(texture=texture, pos=(lx, ly), size=texture.size)

#             # Needle position
#             rad = math.radians(self.current_angle)
#             nx = cx + 90 * math.cos(rad)
#             ny = cy + 90 * math.sin(rad)

#             # Glowing pulse behind needle
#             pulse = 0.5 + 0.5 * math.sin(time.time() * 2)  # pulse from 0 to 1
#             glow_alpha = 0.2 + (cpu_percent / 100) * 0.5 * pulse  # max 0.7
#             Color(1, 0, 0, glow_alpha)
#             Line(points=[cx, cy, nx, ny], width=10)

#             # Main red needle
#             Color(1, 0, 0, 1)
#             Line(points=[cx, cy, nx, ny], width=3)

#             # Needle center dot
#             Color(1, 0, 0, 1)
#             Ellipse(pos=(cx - 6, cy - 6), size=(12, 12))

#         self.percent_label.text = f"{int(cpu_percent)}%"
#         self.percent_label.pos = (cx - 25, cy - 15)
