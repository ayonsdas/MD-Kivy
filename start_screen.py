from kivy.uix.video import Video
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle
from HoverItem import HoverItem
from kivy.core.window import Window
from kivy.clock import Clock
import os

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "StartScreen"

        self.root = FloatLayout()
        self.add_background(self.root)
        self.add_buttons(self.root)          # add buttons first
        self.add_video_player(self.root)     # annd play video (so panel_wrapper exists)

        self.add_widget(self.root)

    def add_background(self, root):
        with root.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.ui_rect = RoundedRectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_ui_background, size=self.update_ui_background)

    def update_ui_background(self, instance, *args):
        self.ui_rect.pos = instance.pos
        self.ui_rect.size = instance.size

    def add_video_player(self, root):
        self.video_paths = [
            os.path.join(os.path.dirname(__file__), "25711-352026488_small.mp4"),
            os.path.join(os.path.dirname(__file__), "18910-297379533_small.mp4"),
            os.path.join(os.path.dirname(__file__), "10953-226983371_small.mp4")
        ]

        self.video_paths = [
            p if os.path.exists(p) else f"/home/anastasiia/Downloads/{os.path.basename(p)}"
            for p in self.video_paths
        ]
        self.video_paths = [p for p in self.video_paths if os.path.exists(p)]

        if not self.video_paths:
            print("[ERROR] No intro videos found.")
            return

        self.video_index = 0
        self.video = None
        self.loop_video = None
        self.play_intro_video()

        Window.bind(on_mouse_down=self.on_click_next_video)

    def play_intro_video(self):
        if self.video_index >= len(self.video_paths):
            self.play_loop_video()
            return

        video_path = self.video_paths[self.video_index]

        self.video = Video(
            source=video_path,
            state='play',
            options={'eos': 'stop'},
            allow_stretch=True,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        self.video.bind(state=self.on_sequence_video_end)
        self.root.add_widget(self.video, index=1)
        self.bring_buttons_to_front()

    def on_click_next_video(self, *args):
        if hasattr(self, 'video') and self.video and self.video.state == 'stop':
            self.root.remove_widget(self.video)
            self.video_index += 1
            self.play_intro_video()

    def on_sequence_video_end(self, instance, value):
        if value == 'stop':
            print(f"[INFO] Intro video {self.video_index + 1} finished. Click to continue.")

    def play_loop_video(self):
        Window.unbind(on_mouse_down=self.on_click_next_video)

        loop_local = os.path.join(os.path.dirname(__file__), "fixed m to nm.mp4")
        loop_backup = "/home/anastasiia/Downloads/fixed m to nm.mp4"
        loop_path = loop_local if os.path.exists(loop_local) else loop_backup

        if not os.path.exists(loop_path):
            print(f"[ERROR] Loop video not found: {loop_path}")
            return

        self.loop_video = Video(
            source=loop_path,
            state='play',
            options={'eos': 'loop'},
            allow_stretch=True,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        self.root.add_widget(self.loop_video, index=1)
        self.bring_buttons_to_front()
        print("[INFO] Looping background video started.")

    def add_buttons(self, root):
        # add black background panel as a widget bruh without it didnt work
        self.panel_wrapper = Widget(size_hint=(None, None), size=(1000, 100),
                                    pos=(root.width / 2 - 470, 10))
        with self.panel_wrapper.canvas:
            Color(0.0, 0.0, 0.0, 0.4)
            self.button_panel = RoundedRectangle(
                size=self.panel_wrapper.size,
                pos=self.panel_wrapper.pos,
                radius=[25]
            )
        root.bind(size=self.update_button_panel, pos=self.update_button_panel)
        root.add_widget(self.panel_wrapper)

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

    def bring_buttons_to_front(self):
        for widget in [self.panel_wrapper, self.start_button, self.tutorial_button]:
            if widget.parent:
                self.root.remove_widget(widget)
                self.root.add_widget(widget)

    def update_button_panel(self, *args):
        if hasattr(self, 'button_panel'):
            self.panel_wrapper.pos = (self.root.width / 2 - 470, 10)
            self.button_panel.pos = self.panel_wrapper.pos
            self.button_panel.size = (1000, 100)
            self.panel_wrapper.size = (1000, 100)

    def start_game(self):
        self.manager.current = "GameScreen"
