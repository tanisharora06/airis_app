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
            text="AIRIS initializing...",
            size_hint=(1, 0.15),
            font_size='18sp'
        )
        self.layout.add_widget(self.status)

        self.camera = Camera(
            play=True,
            resolution=(640, 480),
            size_hint=(1, 0.85)
        )
        self.layout.add_widget(self.camera)

        Clock.schedule_once(self.start_scan, 2)
        return self.layout

    def start_scan(self, dt):
        self.status.text = "Camera ready. Scanning environment."
        tts.speak("Scanning environment")

        Clock.schedule_once(self.capture_image, 2)

    def capture_image(self, dt):
        if not self.camera.texture:
            self.status.text = "Camera error"
            tts.speak("Camera error")
            return

        self.status.text = "Image captured. Analyzing."
        tts.speak("Image captured")

        Clock.schedule_once(self.fake_ai_result, 2)

    def fake_ai_result(self, dt):
        result = "Detected object: chair"
        self.status.text = result
        tts.speak(result)


if __name__ == "__main__":
    AirisApp().run()
