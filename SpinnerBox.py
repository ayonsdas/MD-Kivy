from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from HoverItem import HoverItem
from kivy.graphics import Color, Rectangle, Line
import os


class SpinnerBox(FloatLayout):
    """A widget that encapsulates a slider with a label, a background, and a border."""
    
    def __init__(self, defaultValue, possibleValues, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.font_path = os.path.join(os.path.dirname(__file__), "Fonts/Impact.ttf")
        self.base_font_size = 10
        self.font_scale_factor = 1
        # self.size_hint = (None, None)
        # self.size = (300, 100)

        # Add background and border
        # with self.canvas.before:
        #     Color(0.2, 0.2, 0.2, 1)  # Background color
        #     self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            # Color(67/255, 157/255, 1, 1)  # Blue border
            # self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=2)

        # Bind position and size changes to update the background and border
        # self.bind(pos=self.update_graphics, size=self.update_graphics)
        # self.bind(size=self._update_label_text_size)

        # Add label
        # self.label = Label(
        #     text=label_text,
        #     size_hint=(1, 0.2),
        #     font_name=self.font_path,
        #     font_size=12,
        #     pos_hint={"center_x" : 0.5, "center_y" : 0.8}
        # )
        # self.add_widget(self.label)

        # # Add slider
        # self.slider = CustomSlider(
        #     min=min_value,
        #     max=max_value,
        #     value=default_value,
        #     step=step,
        #     track_image="Graphics/SliderTrack.png",
        #     thumb_image="Graphics/SliderThumb.png",
        #     size_hint=(0.7,None),
        #     pos_hint={"center_x" : 0.5, "center_y" : 0.3},
        #     height=10
        # )
        
        self.possibleValues = possibleValues
        self.value = defaultValue
        
        self.spinner = Image(size_hint=(0.6, 0.6), pos_hint={"center_x": 0.5, "center_y": 0.5}, source=f"Graphics/{possibleValues[defaultValue]}.png")
        
        self.left_arrow = HoverItem(size_hint=(0.2, 0.6), pos_hint={"center_x": 0.1, "center_y": 0.5}, hoverSource="Graphics/Left-Arrow_Highlighted.png", defaultSource="Graphics/Left-Arrow.png", function=lambda x : self.updateState(-1))
        self.right_arrow = HoverItem(size_hint=(0.2, 0.6), pos_hint={"center_x": 0.9, "center_y": 0.5}, hoverSource="Graphics/Right-Arrow_Highlighted.png", defaultSource="Graphics/Right-Arrow.png", function=lambda x : self.updateState(1))        
        
        # self.slider.bind(value=lambda instance, value: callback(value))
        # self.add_widget(self.slider)
        
        self.add_widget(self.spinner)
        self.add_widget(self.left_arrow)
        self.add_widget(self.right_arrow)
        
        
    def updateState(self, delta):
        self.value = (self.value + delta) % len(self.possibleValues)
        self.spinner.source = f"Graphics/{self.possibleValues[self.value]}.png"

    # def update_graphics(self, *args):
    #     """Update the background and border dimensions."""
    #     self.bg_rect.pos = self.pos
    #     self.bg_rect.size = self.size
    #     # self.border.rectangle = (self.x, self.y, self.width, self.height)

    # def _update_label_text_size(self, *args):
    #     """Ensure the label text fits within the box."""
    #     self.label.height = self.height * .3
    #     self.label.font_size = self.height * .2
