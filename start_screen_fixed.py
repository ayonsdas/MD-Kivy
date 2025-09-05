from kivy.uix.video import Video
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.uix.label import Label
from HoverItem import HoverItem
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import NumericProperty
import os

# Set this much higher to prevent the error
Clock.max_iteration = 200

class FadeOverlay(Widget):
    opacity_level = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0, 0, 0, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect, opacity_level=self.update_opacity)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def update_opacity(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0, 0, 0, self.opacity_level)
            self.rect = Rectangle(pos=self.pos, size=self.size)

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "StartScreen"
        print("[INFO] Initializing StartScreen")
        
        # Initialize all variables first
        self.video = None
        self.loop_video = None
        self.video_index = 0
        self.panel_wrapper = None
        self.start_button = None
        self.tutorial_button = None
        self.keep_clicking_label = None
        self.button_panel = None
        
        # Create root layout
        self.root = FloatLayout()
        
        # Add fade overlay
        self.fade_overlay = FadeOverlay(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.root.add_widget(self.fade_overlay)
        
        # Add keep clicking label
        self.keep_clicking_label = Label(
            text="KEEP CLICKING",
            font_size="64sp",
            bold=True,
            opacity=0,
            color=(1, 1, 1, 1),
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0.47},
            halign="center",
            valign="middle"
        )
        self.keep_clicking_label.bind(size=self.update_label_text_size)
        self.root.add_widget(self.keep_clicking_label)
        
        # Add background, buttons and video in order
        self.add_background(self.root)
        self.add_buttons(self.root)
        self.play_loop_video()
        
        # Add root to screen
        self.add_widget(self.root)

    def update_label_text_size(self, instance, value):
        instance.text_size = value

    def add_background(self, root):
        with root.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.ui_rect = RoundedRectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_ui_background, size=self.update_ui_background)

    def update_ui_background(self, instance, *args):
        self.ui_rect.pos = instance.pos
        self.ui_rect.size = instance.size

    def play_loop_video(self):
        """Play a single video in a loop without transitions"""
        # Cleanup any existing video
        if self.video:
            self.video.state = 'stop'
            self.video.unload()
            self.root.remove_widget(self.video)
            self.video = None
            
        if self.loop_video:
            self.loop_video.state = 'stop'
            self.loop_video.unload()
            self.root.remove_widget(self.loop_video)
            self.loop_video = None
            
        # Try various video files that may exist
        possible_paths = [
            # Try original filenames first
            os.path.join(os.path.dirname(__file__), "fixed m to nm.mp4"),
            "/home/anastasiia/Downloads/fixed m to nm.mp4",
            
            # Try alternative videos from Downloads folder
            "/home/anastasiia/Downloads/m_to_nm title.mp4",
            "/home/anastasiia/Downloads/m_to_nm_julian.mp4",
            "/home/anastasiia/Downloads/m_to_nm_remote.mp4",
            "/home/anastasiia/Downloads/m_to_nm_battery_outer.mp4",
            "/home/anastasiia/Downloads/m_to_nm_ions_still.mp4"
        ]
        
        print(f"[DEBUG] Looking for video in these locations:")
        for path in possible_paths:
            print(f" - {path} (exists: {os.path.exists(path)})")
            
        # Find first valid path
        video_path = None
        for path in possible_paths:
            if os.path.exists(path):
                video_path = path
                break

        if not video_path:
            print("[ERROR] No video file found")
            return
            
        print(f"[INFO] Playing video: {video_path}")
            
        # Create video widget
        self.loop_video = Video(
            source=video_path,
            state='play',
            options={'eos': 'loop'},  # Loop the video
            allow_stretch=True,
            keep_ratio=False,
            volume=0,  # Mute the video
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        
        # Add at index 1 (behind controls)
        self.root.add_widget(self.loop_video, index=1)
        
        # Fade out overlay
        Animation(opacity_level=0, duration=0.5).start(self.fade_overlay)
        
        print("[INFO] Video started playing")

    def add_buttons(self, root):
        # Create panel
        self.panel_wrapper = Widget(size_hint=(None, None), size=(1000, 100), pos=(root.width / 2 - 470, 10))
        with self.panel_wrapper.canvas:
            Color(0.0, 0.0, 0.0, 0.4)
            self.button_panel = RoundedRectangle(size=self.panel_wrapper.size, pos=self.panel_wrapper.pos, radius=[25])
        root.bind(size=self.update_button_panel, pos=self.update_button_panel)
        
        # Create buttons
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
        
        # Add in proper order to avoid z-index issues
        root.add_widget(self.panel_wrapper)
        root.add_widget(self.start_button)
        root.add_widget(self.tutorial_button)

    def update_button_panel(self, *args):
        if hasattr(self, 'button_panel') and self.button_panel:
            self.panel_wrapper.pos = (self.root.width / 2 - 470, 10)
            self.button_panel.pos = self.panel_wrapper.pos
            self.button_panel.size = (1000, 100)
            self.panel_wrapper.size = (1000, 100)

    def start_game(self):
        if self.loop_video:
            self.loop_video.state = 'stop'
            self.loop_video.unload()
            self.root.remove_widget(self.loop_video)
            self.loop_video = None
        self.manager.current = "GameScreen"
