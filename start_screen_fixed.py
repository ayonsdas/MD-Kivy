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
import gc  # for garbage collection stuff

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

        self.add_background(self.root)
        self.add_buttons(self.root)
        self.add_video_player(self.root)

        self.add_widget(self.root)

        # keep track if we bound the touch event
        self._touch_bound = True

    def force_cleanup(self):
        try:
            gc.collect()
            gc.collect()
        except Exception:
            pass

    def schedule_periodic_cleanup(self):
        Clock.schedule_interval(lambda dt: self.force_cleanup(), 30)

    def add_background(self, root):
        with root.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.ui_rect = RoundedRectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_ui_background, size=self.update_ui_background)

    def update_ui_background(self, instance, *args):
        self.ui_rect.pos = instance.pos
        self.ui_rect.size = instance.size

    def add_video_player(self, root):
        # look for videos in local dir first then in Downloads
        local_dir = os.path.dirname(__file__)
        downloads_dirs = [
            os.path.join(os.path.expanduser('~'), 'Downloads'),
            r'C:\Users\Vislab Admin\Downloads',
        ]

        video_filenames = [
            "m_to_nm_title.mp4",
            "m_to_nm_julian.mp4",
            "m_to_nm_remote.mp4",
            "m_to_nm_battery_outer.mp4",
            "m_to_nm_battery_separator.mp4",
            "m_to_nm_ions_still.mp4",
            "m_to_nm_ions_moving.mp4"
        ]

        self.video_paths = []
        for fname in video_filenames:
            local_path = os.path.join(local_dir, fname)
            if os.path.exists(local_path):
                self.video_paths.append(local_path)
                continue
            for downloads_dir in downloads_dirs:
                downloads_path = os.path.join(downloads_dir, fname)
                if os.path.exists(downloads_path):
                    self.video_paths.append(downloads_path)
                    break

        if not self.video_paths:
            print("[ERROR] No intro videos found.")
            return

        self.video_index = 0
        self.video = None
        self.loop_video = None
        self.play_intro_video()

        Window.bind(on_touch_down=self.on_touch_down_global)
        self.schedule_periodic_cleanup()

    def play_intro_video(self):
        if self.video_index >= len(self.video_paths):
            self.play_loop_video()
            return

        if self.video:
            self.video.state = 'stop'
            self.video.unload()
            self.root.remove_widget(self.video)
            self.force_cleanup()

        video_path = self.video_paths[self.video_index]

        self.video = Video(
            source=video_path,
            state='play',
            options={'eos': 'stop', 'buffer_size': 2048},
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
        pass

    def transition_video(self, old_video):
        if self.video_index >= len(self.video_paths):
            self.fade_overlay.opacity_level = 1
            self.play_loop_video()
            return

        if old_video:
            old_video.state = 'stop'
            old_video.unload()
            self.root.remove_widget(old_video)
            self.force_cleanup()

        new_video = Video(
            source=self.video_paths[self.video_index],
            state='play',
            options={'eos': 'stop', 'buffer_size': 2048},
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

        fade_in_new = Animation(opacity=1, duration=0.6, t='out_quad')
        fade_in_new.start(new_video)

        def fade_out_overlay(*_):
            Animation(opacity_level=0, duration=0.6, t='out_quad').start(self.fade_overlay)

        fade_in_new.bind(on_complete=fade_out_overlay)

    def on_sequence_video_end(self, instance, value):
        if value == 'stop':
            self.play_loop_video()

    def play_loop_video(self):
        Window.unbind(on_mouse_down=self.on_click_next_video)

        # stop and remove the old loop video if there is one
        if self.loop_video:
            try:
                self.loop_video.state = 'stop'
                self.loop_video.unload()
                self.root.remove_widget(self.loop_video)
            except Exception:
                pass
            self.loop_video = None

        if self.video:
            self.video.state = 'stop'
            self.video.unload()
            self.root.remove_widget(self.video)
            self.video = None

        local_dir = os.path.dirname(__file__)
        downloads_dirs = [
            os.path.join(os.path.expanduser('~'), 'Downloads'),
            r'C:\Users\Vislab Admin\Downloads',
        ]

        loop_local = os.path.join(local_dir, "fixed m to nm.mp4")
        if os.path.exists(loop_local):
            loop_path = loop_local
        else:
            loop_path = None
            for downloads_dir in downloads_dirs:
                loop_downloads = os.path.join(downloads_dir, "fixed m to nm.mp4")
                if os.path.exists(loop_downloads):
                    loop_path = loop_downloads
                    break

        if not loop_path:
            print("[ERROR] Loop video not found in any folder.")
            return

        self.loop_video = Video(
            source=loop_path,
            state='play',
            options={
                'eos': 'loop',
                'buffer_size': 1024,
                'autoplay': True,
                'allow_cache': False
            },
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

    def add_buttons(self, root):
        panel_w = root.width * 0.50
        panel_h = root.height * 0.11
        panel_x = root.width / 2 - panel_w / 2
        self.panel_wrapper = Widget(size_hint=(None, None),
                                    size=(panel_w, panel_h),
                                    pos=(panel_x, 0))
        with self.panel_wrapper.canvas:
            Color(0.0, 0.0, 0.0, 0.4)
            self.button_panel = RoundedRectangle(size=self.panel_wrapper.size,
                                                 pos=self.panel_wrapper.pos,
                                                 radius=[25])
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
                Clock.schedule_once(lambda dt, w=widget: self.root.add_widget(w), 0)

    def update_button_panel(self, *args):
        if hasattr(self, 'button_panel'):
            panel_w = self.root.width * 0.50
            panel_h = self.root.height * 0.11
            panel_x = self.root.width / 2 - panel_w / 2
            self.panel_wrapper.size = (panel_w, panel_h)
            self.panel_wrapper.pos = (panel_x, 0)
            self.button_panel.size = self.panel_wrapper.size
            self.button_panel.pos  = self.panel_wrapper.pos

    def on_touch_down_global(self, window, touch):
        if hasattr(self, 'video') and self.video and self.video.state == 'stop':
            self.on_click_next_video()
        return False

    def start_game(self):
        def switch_screen(*args):
            self.manager.current = "GameScreen"
        fade_out = Animation(opacity_level=1, duration=0.4)
        fade_out.bind(on_complete=switch_screen)
        fade_out.start(self.fade_overlay)

    def on_pre_leave(self, *args):
        # pause whichever video is playing so we can resume it when coming back
        for attr in ('video', 'loop_video'):
            vid = getattr(self, attr, None)
            if vid and vid.state == 'play':
                try:
                    vid.state = 'pause'
                except Exception:
                    pass

        if self._touch_bound:
            try:
                Window.unbind(on_touch_down=self.on_touch_down_global)
            except Exception:
                pass
            self._touch_bound = False

    def on_pre_enter(self, *args):
        # rebind touch if we left
        if not self._touch_bound:
            try:
                Window.bind(on_touch_down=self.on_touch_down_global)
                self._touch_bound = True
            except Exception:
                pass

        # try to resume whichever video was paused
        video_resumed = False
        for attr in ('video', 'loop_video'):
            vid = getattr(self, attr, None)
            if vid and vid.state == 'pause':
                try:
                    vid.state = 'play'
                    video_resumed = True
                except Exception:
                    pass

        # nothing to resume — start fresh
        if not video_resumed:
            try:
                if hasattr(self, 'video_paths') and hasattr(self, 'video_index'):
                    if self.video_index >= len(self.video_paths):
                        self.play_loop_video()
                    else:
                        self.play_intro_video()
                else:
                    self.add_video_player(self.root)
            except Exception:
                pass

        # always fade the black overlay away when coming back here
        Animation(opacity_level=0, duration=0.5).start(self.fade_overlay)
