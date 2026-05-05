import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from CustomSlider import CustomSlider
from kivy.graphics import Color, RoundedRectangle, Line
from performance_monitor import get_global_monitor

_IMPACT = os.path.join(os.path.dirname(__file__), "Fonts/Impact.ttf")


class SliderBox(BoxLayout):
    """Styled slider card: dark background, cyan border, short name + live value."""

    def __init__(self, label_text, min_value, max_value, default_value, step, callback,
                 info_text='', info_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding   = [8, 3, 8, 3]
        self.spacing   = 2

        # background + border
        with self.canvas.before:
            Color(0.04, 0.07, 0.15, 1.0)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[(8, 8)] * 4)
            Color(0.0, 0.55, 0.9, 0.75)
            self.border = Line(
                rounded_rectangle=[self.x, self.y, self.width, self.height, 8],
                width=1.4
            )
        self.bind(pos=self._sync_bg, size=self._sync_bg)

        # first word only as short name — keeps labels tight
        short_name = label_text.split('(')[0].strip().split()[0].upper()

        # header row: name left, live value right
        header = BoxLayout(orientation='horizontal', size_hint=(1, None), height=24)

        self.name_label = Label(
            text=short_name,
            font_size='15sp',
            bold=True,
            color=(0.78, 0.88, 1.0, 1),
            halign='left',
            valign='middle',
        )
        self.name_label.bind(size=self.name_label.setter('text_size'))

        self.value_label = Label(
            text=f'{default_value:.2f}',
            font_size='15sp',
            bold=True,
            color=(0.0, 0.85, 1.0, 1),
            halign='right',
            valign='middle',
        )
        self.value_label.bind(size=self.value_label.setter('text_size'))

        header.add_widget(self.name_label)
        header.add_widget(self.value_label)

        if info_text and info_callback:
            info_btn = Button(
                text='?',
                size_hint=(None, 1), width=22,
                background_normal='', background_color=(0.04, 0.10, 0.28, 0.95),
                color=(0.0, 0.85, 1.0, 1),
                font_name=_IMPACT,
                font_size='14sp',
            )
            info_btn.bind(on_press=lambda *a: info_callback(info_text))
            header.add_widget(info_btn)

        self.add_widget(header)

        # slider
        self.slider = CustomSlider(
            min=min_value,
            max=max_value,
            value=default_value,
            step=step,
            track_image="Graphics/SliderTrack.png",
            thumb_image="Graphics/SliderThumb.png",
            size_hint=(1, None),
            height=30,
        )
        self.slider.bind(value=self._on_value)
        self.add_widget(self.slider)

        self.external_callback = callback

    def _on_value(self, instance, value):
        self.value_label.text = f'{value:.2f}'
        if self.external_callback:
            self.external_callback(value)

    def _sync_bg(self, *args):
        self.bg.pos  = self.pos
        self.bg.size = self.size
        self.border.rounded_rectangle = [self.x, self.y, self.width, self.height, 8]
