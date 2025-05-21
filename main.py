from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from simulation import GameScreen
from start_screen import StartScreen


class WindowManager(ScreenManager):
    def __init__(self, **kwargs):
        self.start_screen = kwargs.pop("start_screen")
        self.game_screen = kwargs.pop("game_screen")

        super().__init__(**kwargs)

        # add only the screens I use
        self.add_widget(self.start_screen)
        self.add_widget(self.game_screen)

        # start from the StartScreen
        self.current = self.start_screen.name

    def switch_to_start_screen(self):
        self.current = self.start_screen.name

    def start_game(self, name):
        if name == self.start_screen.name:
            self.current = self.game_screen.name

    def go_back(self, name):
        if name == self.game_screen.name:
            self.current = self.start_screen.name


# app launcher
class GameApp(App):
    def build(self):
        self.start_screen = StartScreen(name="StartScreen")
        self.game_screen = GameScreen(name="GameScreen")
        self.window_manager = WindowManager(start_screen=self.start_screen, game_screen=self.game_screen)
        return self.window_manager


if __name__ == "__main__":
    GameApp().run()
