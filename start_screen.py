from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle, Line
from game_layout import GameLayout
from HoverItem import HoverItem
from TextBlurb import TextBlurb
from CustomSlider import CustomSlider
from SliderBox import SliderBox
from SpinnerBox import SpinnerBox
from simulation import GameScreen


class StartScreen(Screen):
    
    def __init__(self, **kwargs):
        """Set up the start screen"""
        super(Screen, self).__init__(**kwargs)
        
        self.name = "StartScreen"
        
        self.root = FloatLayout()
        self.add_background(self.root)
        
        self.add_buttons(self.root)
        
        self.add_widget(self.root)
        
    def add_background(self, root):
        """Add a grey background and bind its size/position to root."""
        with root.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.ui_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_ui_background, size=self.update_ui_background)
        
    def update_ui_background(self, instance, *args):
        """Update background dynamically when the window size changes."""
        self.ui_rect.pos = instance.pos
        self.ui_rect.size = instance.size
        
    def add_buttons(self, root):
        """Add the buttons"""
        self.start_button = HoverItem(size_hint=(0.2, 0.1),
                            pos_hint={"center_x": 0.5, "center_y": 0.2}, 
                            hoverSource="Graphics/Start_Highlighted.png", 
                            defaultSource="Graphics/Start.png", 
                            function=lambda x : self.start_game())
        
        self.tutorial_button =  HoverItem(size_hint=(0.2, 0.1),
                                pos_hint={"center_x": 0.5, "center_y": 0.1}, 
                                hoverSource="Graphics/Tutorial_Highlighted.png", 
                                defaultSource="Graphics/Tutorial.png", 
                                function=lambda x : print('bruh'))
        root.add_widget(self.start_button)
        root.add_widget(self.tutorial_button)
        
    def start_game(self):
        """Make the Window Manager start the game."""
        self.parent.start_game(self.name)
        
