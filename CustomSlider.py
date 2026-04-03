from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.graphics import Rectangle


class CustomSlider(Widget):
    value = NumericProperty(0)  # Slider value (0 to 1)
    min = NumericProperty(0)   # Minimum slider value
    max = NumericProperty(100)  # Maximum slider value
    step = NumericProperty(1)   # Step value for the slider
    
    slider_length = NumericProperty(200)  # Length of the slider track
    is_active = BooleanProperty(False)    # Tracks if the slider is actively being adjusted

    track_image = StringProperty("")  # Path to track image
    thumb_image = StringProperty("")  # Path to thumb image

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, None)  # Set size_hint for dynamic width resizing

        self.track = Image(
            source=self.track_image,
            size_hint=(None, None),
            allow_stretch=True,
            keep_ratio=False,
        )
        self.thumb = Image(
            source=self.thumb_image,
            size_hint=(None, None),
            size=(30, 30),
            allow_stretch=True,
        )

        self.add_widget(self.track)
        self.add_widget(self.thumb)

        # Bindings for updates
        self.bind(pos=self.update_positions, size=self.update_positions)
        self.bind(value=self.update_thumb_from_value)

    def on_touch_down(self, touch):
        """check if user touched the slider"""
        if self.collide_point(*touch.pos):
            self.is_active = True
            self.update_thumb_position(touch.x)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        """move the thumb when user drags"""
        if self.is_active:
            self.update_thumb_position(touch.x)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        """handle when user releases"""
        if self.is_active:
            self.is_active = False  # Mark this slider as inactive
            return True
        return super().on_touch_up(touch)

    def update_thumb_position(self, touch_x):
        """Move the thumb and update the slider value with steps."""
        x_min = self.x
        x_max = x_min + self.slider_length - self.thumb.width
        new_x = min(max(touch_x, x_min), x_max)
        
        # figure out what value we got
        raw_value = self.min + (self.max - self.min) * ((new_x - x_min) / (self.slider_length - self.thumb.width))
        
        # Snap to the nearest step
        snapped_value = round((raw_value - self.min) / self.step) * self.step + self.min
        self.value = max(self.min, min(snapped_value, self.max))
        
        self.thumb.pos = (x_min + (self.value - self.min) / (self.max - self.min) * (self.slider_length - self.thumb.width),
                          self.center_y - self.thumb.height / 2)

    def update_positions(self, *args):
        """update track and thumb positions"""
        self.slider_length = self.width  # resize to match how wide it is
        self.track.size = (self.slider_length, 10)  # update size too
        self.track.pos = (self.x, self.center_y - 5)  # Center the track vertically
        self.update_thumb_from_value()
        
    def update_thumb_from_value(self, *args):
        """move thumb based on slider value"""
        x_min = self.x
        self.thumb.pos = (
            x_min + (self.value - self.min) / (self.max - self.min) * (self.slider_length - self.thumb.width),
            self.center_y - self.thumb.height / 2,
        )
