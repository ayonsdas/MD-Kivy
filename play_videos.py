# from kivy.uix.video import Video
# from kivy.uix.floatlayout import FloatLayout
# from kivy.uix.label import Label
# from kivy.core.window import Window
# from kivy.clock import Clock
# import os
# from kivy.utils import get_color_from_hex


# class VideoPlayerApp(FloatLayout):
#     def __init__(self, switch_callback=None, **kwargs):
#         self.switch_callback = switch_callback
#         kwargs.pop('switch_callback', None)
#         super().__init__(**kwargs)

#         self.video_paths = [  # the videos where broken thats why it didnt work
            
#         ]
#         self.current_stage = 0

#         # Making nice gradient color here
#         self.continue_label = Label(
#             text="[b]"
#                 "[color=#99CCFF]C[/color]"
#                 "[color=#88BBFF]L[/color]"
#                 "[color=#77AAFF]I[/color]"
#                 "[color=#66A0FF]C[/color]"
#                 "[color=#5590FF]K[/color] "
#                 "[color=#4490FF]T[/color]"
#                 "[color=#3399FF]O[/color] "
#                 "[color=#22AAFF]C[/color]"
#                 "[color=#11BBFF]O[/color]"
#                 "[color=#00CCFF]N[/color]"
#                 "[color=#00CCEE]T[/color]"
#                 "[color=#00CCDD]I[/color]"
#                 "[color=#00CCCC]N[/color]"
#                 "[color=#00CCBB]U[/color]"
#                 "[color=#00CCAA]E[/color]"
#                 "[/b]",
#             markup=True,
#             font_size="32sp",
#             color=(1, 1, 1, 0),  # Still fades in
#             pos_hint={"center_x": 0.5, "center_y": 0.1}
#         )

#         Window.unbind(on_mouse_down=self.on_mouse_down)
#         Window.bind(on_mouse_down=self.on_mouse_down)

#         self.play_current_stage()

#     def get_video_path(self, filename):
#         local_path = os.path.join(os.path.dirname(__file__), filename)
#         backup_path = f"/home/anastasiia/Downloads/{filename}"
#         return local_path if os.path.exists(local_path) else backup_path

#     def play_current_stage(self):
#         if hasattr(self, 'video') and self.video:
#             self.remove_widget(self.video)

#         if self.continue_label.parent:
#             self.remove_widget(self.continue_label)

#         if self.current_stage >= len(self.video_paths):
#             print("[INFO] All videos played.")
#             Window.unbind(on_mouse_down=self.on_mouse_down)
#             if self.switch_callback:
#                 Clock.schedule_once(lambda dt: self.switch_callback())
#             return

#         video_file = self.video_paths[self.current_stage]
#         video_path = self.get_video_path(video_file)

#         if not os.path.exists(video_path):
#             print(f"[ERROR] File not found: {video_path}")
#             self.current_stage += 1
#             self.play_current_stage()
#             return

#         eos_mode = 'stop'

#         if self.current_stage == len(self.video_paths) - 1:
#             size = (1, 1)
#             pos = {"x": 0, "y": 0}
#         else:
#             size = (1, 1)
#             pos = {"x": 0, "y": 0}

#         self.video = Video(
#             source=video_path,
#             state='play',
#             options={'eos': eos_mode},
#             allow_stretch=True,
#             size_hint=size,
#             pos_hint=pos
#         )

#         self.video.bind(state=self.on_video_state_change)
#         self.add_widget(self.video)

#     def on_video_state_change(self, instance, value):
#         if value == 'stop':
#             if not self.continue_label.parent:
#                 self.continue_label.color = (1, 1, 1, 0.9)
#                 self.add_widget(self.continue_label)

#     def on_mouse_down(self, window, x, y, button, modifiers):
#         # if playing, stop and wait before going to next
#         if self.video.state == 'play':
#             self.video.state = 'stop'

#             # Delay advancing to make sure video is done stopping
#             Clock.schedule_once(self._go_to_next_stage, 0.2)
#         elif self.video.state == 'stop':
#             # If already stopped, go immediately
#             self._go_to_next_stage()

#     def _go_to_next_stage(self, *args):
#         if self.continue_label.parent:
#             self.remove_widget(self.continue_label)
#             self.continue_label.color = (1, 1, 1, 0)

#         self.current_stage += 1
#         self.play_current_stage()
