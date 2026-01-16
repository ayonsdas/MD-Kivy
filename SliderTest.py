from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from CustomSlider import CustomSlider


class TestApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=20)
        slider = CustomSlider(
            min=0,
            max=100,
            value=50,
            step=5,
            size=(100,50),
            track_image="Graphics/SliderTrack.png",
            thumb_image="Graphics/SliderThumb.png"
        )
        slider.bind(value=self.on_slider_change)
        layout.add_widget(slider)
        return layout

    def on_slider_change(self, slider, value):
        print(f"Slider value: {value}")


if __name__ == '__main__':
    TestApp().run()
