from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from plyer import tts
from kivy.clock import Clock


class AirisApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        # Camera auto-start
        self.camera = Camera(
            play=True,
            resolution=(640, 480),
            size_hint=(1, 0.85)
        )
        self.layout.add_widget(self.camera)

        # Status label
        self.status = Label(
            text="Camera is running",
            size_hint=(1, 0.15)
        )
        self.layout.add_widget(self.status)

        # Speak AFTER app loads (important)
        Clock.schedule_once(self.say_ready, 1)

        return self.layout

    def say_ready(self, dt):
        tts.speak("Camera is ready")


if __name__ == "__main__":
    AirisApp().run()
