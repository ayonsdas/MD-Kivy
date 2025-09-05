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

        self.root = FloatLayout()
        self.fade_overlay = FadeOverlay(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.root.add_widget(self.fade_overlay, index=100)

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
        self.root.add_widget(self.keep_clicking_label, index=101)

        self.add_background(self.root)
        self.add_buttons(self.root)
        self.add_video_player(self.root)

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

    def add_video_player(self, root):
        self.video_paths = [
            os.path.join(os.path.dirname(__file__), "m_to_nm title.mp4"),
            os.path.join(os.path.dirname(__file__), "m_to_nm_julian.mp4"),
            os.path.join(os.path.dirname(__file__), "m_to_nm_remote.mp4"),
            os.path.join(os.path.dirname(__file__), "m_to_nm_battery_outer.mp4"),
            os.path.join(os.path.dirname(__file__), "m_to_nm_battery_separator.mp4"),
            os.path.join(os.path.dirname(__file__), "m_to_nm_ions_still.mp4"),
            os.path.join(os.path.dirname(__file__), "m_to_nm_ions_moving.mp4")
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

        Window.bind(on_touch_down=self.on_touch_down_global)

    def play_intro_video(self):
        if self.video_index >= len(self.video_paths):
            self.play_loop_video()
            return

        if self.video:
            self.video.state = 'stop'
            self.video.unload()
            self.root.remove_widget(self.video)

        video_path = self.video_paths[self.video_index]

        self.video = Video(
            source=video_path,
            state='play',
            options={'eos': 'stop'},
            allow_stretch=True,
            keep_ratio=False,
            volume=0,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        self.video.opacity = 0
        self.video.bind(state=self.on_sequence_video_end)
        self.root.add_widget(self.video, index=1)
        self.bring_buttons_to_front()

        Animation(opacity=1, duration=0.5).start(self.video)
        Animation(opacity_level=0, duration=0.6).start(self.fade_overlay)

    def on_click_next_video(self, *args):
        if hasattr(self, 'video') and self.video and self.video.state == 'stop':
            self.video_index += 1
            old_video = self.video

            Animation(opacity=0, duration=0.3).start(self.keep_clicking_label)

            fade_black = Animation(opacity_level=1, duration=0.4)
            fade_black.bind(on_complete=lambda *_: self.transition_video(old_video))
            fade_black.start(self.fade_overlay)

    def transition_video(self, old_video):
        if self.video_index >= len(self.video_paths):
            self.fade_overlay.opacity_level = 1
            self.play_loop_video()
            return

        if old_video:
            old_video.state = 'stop'
            old_video.unload()
            self.root.remove_widget(old_video)

        new_video = Video(
            source=self.video_paths[self.video_index],
            state='play',
            options={'eos': 'stop'},
            allow_stretch=True,
            keep_ratio=False,
            volume=0,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        new_video.opacity = 0
        new_video.bind(state=self.on_sequence_video_end)
        self.root.add_widget(new_video, index=1)
        self.video = new_video
        self.bring_buttons_to_front()

        fade_in_new = Animation(opacity=1, duration=0.4)
        fade_in_new.start(new_video)

        def fade_out_overlay(*_):
            Animation(opacity_level=0, duration=0.5).start(self.fade_overlay)

        fade_in_new.bind(on_complete=fade_out_overlay)

    def on_sequence_video_end(self, instance, value):
        if value == 'stop':
            print(f"[INFO] Intro video {self.video_index + 1} finished.")
            if self.video_index == len(self.video_paths) - 1:
                # Calm transition: fade overlay up, swap, fade overlay down
                try:
                    self.keep_clicking_label.opacity = 0
                except Exception:
                    pass
                fade_up = Animation(opacity_level=1, duration=0.25)

                def _after_up(*_):
                    # Swap to loop video ("fixed m to nm.mp4") then fade overlay down smoothly
                    self.video_index += 1  # mark sequence complete
                    self.play_loop_video()
                    Animation(opacity_level=0, duration=0.8, t='out_quad').start(self.fade_overlay)

                fade_up.bind(on_complete=_after_up)
                fade_up.start(self.fade_overlay)
            else:
                Animation(opacity_level=1, duration=0.5).start(self.fade_overlay)
                Animation(opacity=1, duration=0.6).start(self.keep_clicking_label)

    def play_loop_video(self):
        Window.unbind(on_mouse_down=self.on_click_next_video)

        if self.video:
            self.video.state = 'stop'
            self.video.unload()
            self.root.remove_widget(self.video)
            self.video = None

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
            keep_ratio=False,
            volume=0,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        self.loop_video.opacity = 0
        self.root.add_widget(self.loop_video, index=1)
        self.bring_buttons_to_front()

        Animation(opacity=1, duration=0.5).start(self.loop_video)
        Animation(opacity_level=0, duration=0.5).start(self.fade_overlay)
        print("[INFO] Looping background video started.")

    # (idle fallback removed; restored previous behavior)

    def add_buttons(self, root):
        self.panel_wrapper = Widget(size_hint=(None, None), size=(1000, 100), pos=(root.width / 2 - 470, 10))
        with self.panel_wrapper.canvas:
            Color(0.0, 0.0, 0.0, 0.4)
            self.button_panel = RoundedRectangle(size=self.panel_wrapper.size, pos=self.panel_wrapper.pos, radius=[25])
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
        for widget in [self.panel_wrapper, self.start_button, self.tutorial_button, self.keep_clicking_label]:
            if widget.parent:
                self.root.remove_widget(widget)
                Clock.schedule_once(lambda dt, w=widget: self.root.add_widget(w), 0)

    def update_button_panel(self, *args):
        if hasattr(self, 'button_panel'):
            self.panel_wrapper.pos = (self.root.width / 2 - 470, 10)
            self.button_panel.pos = self.panel_wrapper.pos
            self.button_panel.size = (1000, 100)
            self.panel_wrapper.size = (1000, 100)

    def on_touch_down_global(self, window, touch):
        if hasattr(self, 'video') and self.video and self.video.state == 'stop':
            self.on_click_next_video()
        return False

    def start_game(self):
        if self.loop_video:
            self.loop_video.state = 'stop'
            self.loop_video.unload()
            self.root.remove_widget(self.loop_video)
            self.loop_video = None
        self.manager.current = "GameScreen"
