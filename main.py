from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from simulation import GameScreen
from start_screen import StartScreen
from play_videos import VideoPlayerApp


# wrapper screen for the video player
class VideoScreen(Screen):
    def __init__(self, switch_callback, **kwargs):
        super().__init__(**kwargs)
        self.name = "VideoScreen"
        self.video_player = VideoPlayerApp(switch_callback=switch_callback)
        self.add_widget(self.video_player)


# custom screen manager
class WindowManager(ScreenManager):
    def __init__(self, **kwargs):
        self.start_screen = kwargs.pop("start_screen")
        self.game_screen = kwargs.pop("game_screen")

        super().__init__(**kwargs)

        # create video screen and provide callback
        self.video_screen = VideoScreen(switch_callback=self.switch_to_start_screen)

        # add all screens
        self.add_widget(self.video_screen)
        self.add_widget(self.start_screen)
        self.add_widget(self.game_screen)

        # start from the video screen
        self.current = self.video_screen.name

    def switch_to_start_screen(self):
        self.current = "StartScreen"

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
