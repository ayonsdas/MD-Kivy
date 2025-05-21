from kivy.uix.video import Video
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from HoverItem import HoverItem
import os

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "StartScreen"

        self.root = FloatLayout()
        self.add_background(self.root)
        self.add_video_player(self.root)
        self.add_buttons(self.root)

        self.add_widget(self.root)

    def add_background(self, root):
        with root.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.ui_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_ui_background, size=self.update_ui_background)

    def update_ui_background(self, instance, *args):
        self.ui_rect.pos = instance.pos
        self.ui_rect.size = instance.size

    # this one will be played forever the ones in play_videos will be played only ones
    def add_video_player(self, root):
        local_path = os.path.join(os.path.dirname(__file__), "fixed m to nm.mp4")  
        backup_path = "/home/anastasiia/Downloads/fixed m to nm.mp4"  # set double path just in case

        video_path = local_path if os.path.exists(local_path) else backup_path
          # make sure it's in the same folder
        if not os.path.exists(video_path):
            print(f"[ERROR] Video not found: {video_path}")
            return

        self.video = Video(source=video_path, state='play',
                           options={'eos': 'loop'},  # loop so it keeps playing after the person watched and clicked through
                           allow_stretch=True,
                           size_hint=(1, 1),
                           pos_hint={"x": 0, "y": 0})
        root.add_widget(self.video)

    def add_buttons(self, root):
        self.start_button = HoverItem(
            size_hint=(0.2, 0.1),
            pos_hint={"center_x": 0.35, "center_y": 0.05},
            hoverSource="Graphics/Start_Highlighted.png",
            defaultSource="Graphics/Start.png",
            function=lambda x: self.start_game()
        )

        self.tutorial_button = HoverItem(
            size_hint=(0.2, 0.1),
            pos_hint={"center_x": 0.65, "center_y": 0.05},
            hoverSource="Graphics/Tutorial_Highlighted.png",
            defaultSource="Graphics/Tutorial.png",
            function=lambda x: print("Tutorial clicked")
        )

        root.add_widget(self.start_button)
        root.add_widget(self.tutorial_button)

    def start_game(self):
        self.manager.current = "GameScreen"
