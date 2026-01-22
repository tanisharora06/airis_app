from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock

from plyer import camera
import time


class AIRISApp(App):

    def build(self):
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        self.label = Label(
            text="AIRIS Ready",
            font_size=24
        )

        self.button = Button(
            text="Start Camera",
            size_hint=(1, 0.3)
        )
        self.button.bind(on_press=self.start_camera)

        self.layout.add_widget(self.label)
        self.layout.add_widget(self.button)

        return self.layout

    def start_camera(self, instance):
        self.label.text = "Opening camera..."
        Clock.schedule_once(self.take_picture, 1)

    def take_picture(self, dt):
        filename = f"/sdcard/airis_{int(time.time())}.jpg"

        try:
            camera.take_picture(
                filename=filename,
                on_complete=self.on_picture_taken
            )
        except Exception as e:
            self.label.text = "Camera failed"
            print(e)

    def on_picture_taken(self, filepath):
        self.label.text = "Image captured successfully"


if __name__ == "__main__":
    AIRISApp().run()
