from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivy.clock import Clock
from plyer import tts
from android.permissions import request_permissions, Permission


class AirisApp(App):

    def build(self):
        request_permissions([
            Permission.CAMERA,
            Permission.RECORD_AUDIO
        ])

        self.layout = BoxLayout(orientation='vertical')

        self.status = Label(
            text="AIRIS starting…",
            size_hint=(1, 0.15)
        )
        self.layout.add_widget(self.status)

        self.camera = Camera(
            play=True,
            resolution=(640, 480),
            size_hint=(1, 0.85)
        )
        self.layout.add_widget(self.camera)

        Clock.schedule_once(self.on_startup, 2)
        return self.layout

    def on_startup(self, dt):
        self.status.text = "Camera ready. Capturing image."
        tts.speak("Camera ready")

        Clock.schedule_once(self.capture_image, 2)

    def capture_image(self, dt):
        if not self.camera.texture:
            self.status.text = "Camera failed"
            tts.speak("Camera failed")
            return

        self.status.text = "Image captured"
        tts.speak("Image captured")


if __name__ == "__main__":
    AirisApp().run()
