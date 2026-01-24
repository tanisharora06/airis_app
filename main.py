from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.clock import Clock
from plyer import tts

from PIL import Image
import io
import time


class AirisApp(App):

    def build(self):
        self.root = BoxLayout(orientation="vertical")

        self.status = Label(
            text="AIRIS ready",
            size_hint=(1, 0.15),
            font_size="18sp"
        )
        self.root.add_widget(self.status)

        self.camera = Camera(
            play=True,
            resolution=(640, 480),
            size_hint=(1, 0.7)
        )
        self.root.add_widget(self.camera)

        scan_btn = Button(
            text="Scan Automatically",
            size_hint=(1, 0.15)
        )
        scan_btn.bind(on_press=self.start_scan)
        self.root.add_widget(scan_btn)

        tts.speak("AIRIS launched successfully")
        return self.root

    def start_scan(self, instance):
        self.status.text = "Scanning environment"
        tts.speak("Scanning")
        Clock.schedule_once(self.capture_image, 1)

    def capture_image(self, dt):
        if not self.camera.texture:
            self.status.text = "Camera error"
            tts.speak("Camera error")
            return

        texture = self.camera.texture
        image = Image.frombytes(
            "RGBA",
            texture.size,
            texture.pixels
        ).convert("RGB")

        # simulate analysis
        self.analyze_image(image)

    def analyze_image(self, image):
        width, height = image.size

        # very lightweight “analysis” (safe placeholder)
        description = f"I see an image of size {width} by {height}"

        self.status.text = description
        tts.speak(description)


if __name__ == "__main__":
    AirisApp().run()
