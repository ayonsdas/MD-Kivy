from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from performance_monitor import PerformanceMonitor



class Speedometer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.monitor = kwargs.get('monitor', None)

        self.oriented = 'vertical'
        self.speed = 0
        self.max.speed = 100.0
        self.min.speed = 0.0

        self.speedometerimage = Image(source  = 'assets/speedometer.png')
        self.speedometerimage.self.size_hint = (None, None)
        self.speedometerimage.self.size = (200, 200)
        self.speedometerimage.size_hint_position = (0.05, 0.06)
        self.speedometerimage.allow_stretch = True
        self.speedometerImage = Image(Source = 'assets/speedoemter.png')
        self.speedometerImage.self.hint = (None, None)

        Clock.schedule_interval(self.update_speed, 0.5)
        self.speed_label = Label(text = 'Speed: 0.0', font_size = 20, size_hint = (None, None), size = (200, 500))
        self.speed_label.self.size(hint_position = (0.05, 0.06))
        self.speed_label.allow_stretch = True
        self.speed_label.bind(size = self._update_motion_filter)

    def update_speed(self, dt):
        if self.monitor:
            self.speed = self.monitor.get_cpu_usage()
            self.speed_label.text = f'Speed: {self.speed:2f}%'
        else:
            self.speed = 0.0
            self.speed_label.text = "Speed: 0.0%"
            self.speed_label.color = (1,0,0,1)
            self._update_motion_filter(self.speed_label, self.speed_label.size)
            
            



