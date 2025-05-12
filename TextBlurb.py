from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import BooleanProperty, StringProperty, NumericProperty, ListProperty
from kivy.graphics import Color, Rectangle
import os


class TextBlurb(BoxLayout):
    """A reusable text blurb widget constrained to a box with toggleable visibility and dynamic resizing."""
    is_visible = BooleanProperty(False)  # Track visibility state
    text = StringProperty("This is a text blurb.")  # Text for the blurb
    font_size = NumericProperty(14)  # Font size for the text
    padding = ListProperty([10, 10, 10, 10])  # Padding around the text
    background_color = [0.2, 0.2, 0.2, 0]  # Default background color (dark gray)
    font_path = os.path.join(os.path.dirname(__file__), "Fonts/Impact.ttf")

    def __init__(self, **kwargs):
        self.parent_size_prop = kwargs.pop("parent_size_prop")
        self.parent_pos_prop = kwargs.pop("parent_pos_prop")
        super().__init__(orientation='vertical', **kwargs)
        self.size_hint = (None, None)  # Explicit size control
        self.size = (400, 200)  # Initial size of the widget

        # Add a background rectangle
        with self.canvas.before:
            self.bg_color = Color(*self.background_color)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_background, size=self._update_background)

        # Label for the text blurb
        self.text_label = Label(
            text=self.text,
            font_size=self.font_size * self.width // 400,
            font_name=self.font_path,
            opacity=0,  # Initially hidden
            size_hint=(None, None),
            text_size=(self.width - 2 * self.padding[0], None),  # Constrain text to fit inside the widget
            pos_hint={"center_x":0.5, "center_y":0.5} 
        )
        self.text_label.bind(size=self._update_text_size)
        self.add_widget(self.text_label)

        # Trigger initial layout update
        self._update_text_layout()
        self.bind(parent=self._bind_parent_events)

    def toggle_visibility(self):
        """Toggle the visibility of the text blurb."""
        self.is_visible = not self.is_visible
        self.text_label.opacity = 1 if self.is_visible else 0
        self.bg_color.a = 1 if self.is_visible else 0

    def _update_background(self, *args):
        """Update the background rectangle size and position."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self._update_text_layout()

    def _update_text_size(self, instance, value):
        """Adjust the text size dynamically based on the label size."""
        self.text_label.text_size = (self.width - 2 * self.padding[0], None)
        self.text_label.size = self.text_label.texture_size

    def _update_text_layout(self, *args):
        """Update the layout dynamically when text or font size changes."""
        # Update label properties
        self.text_label.font_size = self.font_size * self.width // 400
        self.text_label.text_size = (self.width - 2 * self.padding[0], None)

        # Force texture update to calculate size
        self.text_label.texture_update()

        # Resize the widget based on text and padding
        # self.size = (
        #     self.text_label.texture_size[0] + 2 * self.padding[0],
        #     self.text_label.texture_size[1] + 2 * self.padding[0],
        # )

        # Center the label within the widget
        self.text_label.size = self.text_label.texture_size
        self.text_label.pos = (
            self.x + self.padding[0],
            self.y + self.padding[0],
        )
        
    def _bind_parent_events(self, instance, parent):
        """Bind size and position changes of the parent."""
        if parent:
            parent.bind(size=self._resize_with_parent, pos=self._resize_with_parent)
            self._resize_with_parent()

    def _resize_with_parent(self, *args):
        """Resize and reposition the widget dynamically with its parent."""
        if self.parent:
            self.size = (self.parent.width * self.parent_size_prop[0], self.parent.height * self.parent_size_prop[1])  # Scale size relative to parent
            self.pos = (self.parent.width * (self.parent_pos_prop[0] - self.parent_size_prop[0] * .5), self.parent.height * (self.parent_pos_prop[1] - self.parent_size_prop[1] * .5))  # Position relative to parent

            # Update the background rectangle
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size

            # Update the label text size
            self.text_label.text_size = (self.width - self.padding[0] - self.padding[2], None)
