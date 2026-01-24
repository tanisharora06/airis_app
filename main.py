from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.clock import Clock
from plyer import tts, audio

from PIL import Image
import os
import tempfile


class AirisApp(App):

    def build(self):
        root = BoxLayout(
            orientation="vertical",
            padding=8,
            spacing=8
        )

        self.status = Label(
            text="AIRIS ready",
            size_hint=(1, 0.15),
            font_size="18sp"
        )
        root.add_widget(self.status)

        self.camera = Camera(
            play=True,
            resolution=(640, 480),
            size_hint=(1, 0.65)
        )
        root.add_widget(self.camera)

        buttons = BoxLayout(
            size_hint=(1, 0.2),
            spacing=8
        )

        scan_btn = Button(text="Scan")
        scan_btn.bind(on_press=self.start_scan)

        voice_btn = Button(text="Voice")
        voice_btn.bind(on_press=self.start_voice)

        buttons.add_widget(scan_btn)
        buttons.add_widget(voice_btn)
        root.add_widget(buttons)

        self.last_result = "Nothing scanned yet"

        tts.speak("AIRIS is ready")
        return root

    # ---------------- SCAN ----------------
    def start_scan(self, *args):
        self.status.text = "Scanning"
        tts.speak("Scanning")
        Clock.schedule_once(self.capture_image, 1)

    def capture_image(self, dt):
        if not self.camera.texture:
            self.status.text = "Camera not ready"
            tts.speak("Camera not ready")
            return

        texture = self.camera.texture
        image = Image.frombytes(
            "RGBA",
            texture.size,
            texture.pixels
        ).convert("RGB")

        self.analyze_image(image)

    def analyze_image(self, image):
        w, h = image.size
        self.last_result = f"I see an image of size {w} by {h}"
        self.status.text = self.last_result
        tts.speak(self.last_result)

    # ---------------- VOICE ----------------
    def start_voice(self, *args):
        self.status.text = "Listening"
        tts.speak("Listening")

        self.audio_path = tempfile.mktemp(suffix=".wav")

        # Record safely
        audio.record(self.audio_path, duration=3)

        # After recording, trigger action
        Clock.schedule_once(self.after_voice, 3.5)

    def after_voice(self, dt):
        self.status.text = "Voice command received"
        tts.speak("Voice command received")

        # Default safe action
        self.start_scan()

        if os.path.exists(self.audio_path):
            os.remove(self.audio_path)


if __name__ == "__main__":
    AirisApp().run()
