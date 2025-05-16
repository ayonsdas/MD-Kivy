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
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle, Line
from game_layout import GameLayout
from HoverItem import HoverItem
from TextBlurb import TextBlurb
from CustomSlider import CustomSlider
from SliderBox import SliderBox
from SpinnerBox import SpinnerBox
from simulation import GameScreen
from start_screen import StartScreen
from usage_graph import CPUUsageGraph
from performance_monitor import PerformanceMonitor

class WindowManager(ScreenManager):

    # ionic bond strongest show that bond strngth ==> indicate more strength
    # 4bonds represented ==> in terms of strenth ==> ==> show regarding teh bodn breaking
    # Some imperfections for fluctuation ==>
    
    def __init__(self, **kwargs):
        """Set up WindowManager"""
        
        self.start_screen = kwargs.pop("start_screen")
        self.game_screen = kwargs.pop("game_screen")
        super().__init__(**kwargs)
        
        self.add_widget(self.start_screen)
        self.add_widget(self.game_screen)
        
        # self.current = self.start_screen.name
    
    def start_game(self, name):
        if name == self.start_screen.name:
            # self.game_screen.reset()
            self.current = self.game_screen.name
            
    def go_back(self, name):
        if name == self.game_screen.name:
            self.current = self.start_screen.name

class GameApp(App):

    def build(self):
        
        self.start_screen = StartScreen()
        self.game_screen = GameScreen()
        self.window_manager = WindowManager(start_screen=self.start_screen, game_screen=self.game_screen)
        return self.window_manager


if __name__ == "__main__":
    GameApp().run()
