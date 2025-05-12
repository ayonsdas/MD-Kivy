from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from CustomSlider import CustomSlider
from kivy.graphics import Color, Rectangle
import os
from performance_monitor import get_global_monitor  # <-- global access point

class SliderBox(BoxLayout):
    """A widget that encapsulates a slider with a label, a background, and a border."""

    def __init__(self, label_text, min_value, max_value, default_value, step, callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.font_path = os.path.join(os.path.dirname(__file__), "Fonts/Impact.ttf")

        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_graphics, size=self.update_graphics)
        self.bind(size=self._update_label_text_size)

        # Add label
        self.label = Label(
            text=label_text,
            size_hint=(1, 0.2),
            font_name=self.font_path,
            font_size=12,
            pos_hint={"center_x": 0.5, "center_y": 0.8}
        )
        self.add_widget(self.label)

        # Create and add slider
        self.slider = CustomSlider(
            min=min_value,
            max=max_value,
            value=default_value,
            step=step,
            track_image="Graphics/SliderTrack.png",
            thumb_image="Graphics/SliderThumb.png",
            size_hint=(0.7, None),
            pos_hint={"center_x": 0.5, "center_y": 0.3},
            height=10
        )
        self.slider.bind(value=self.on_slider_change)
        self.add_widget(self.slider)

        self.external_callback = callback

    def on_slider_change(self, instance, value):
        if self.external_callback:
            self.external_callback(value)

        try:
            monitor = get_global_monitor()
            if monitor:
                monitor.trigger_boost(40.0)  # Simulate activity
        except Exception as e:
            print("[Slider boost error]", e)

    def update_graphics(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _update_label_text_size(self, *args):
        self.label.height = self.height * 0.3
        self.label.font_size = self.height * 0.2
