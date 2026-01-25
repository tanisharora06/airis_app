from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.clock import Clock, mainthread

from plyer import tts

from PIL import Image
import io
import threading
import requests

SERVER_URL = "https://YOUR_SERVER_URL/detect"


class AirisApp(App):

    def build(self):
        root = BoxLayout(orientation="vertical", padding=8, spacing=8)

        self.status = Label(
            text="AIRIS ready",
            size_hint=(1, 0.15),
            font_size="18sp"
        )
        root.add_widget(self.status)

        self.camera = Camera(
            play=True,
            resolution=(640, 480),
            size_hint=(1, 0.7)
        )
        root.add_widget(self.camera)

        scan_btn = Button(
            text="Scan",
            size_hint=(1, 0.15)
        )
        scan_btn.bind(on_press=self.start_scan)
        root.add_widget(scan_btn)

        Clock.schedule_once(lambda dt: self.safe_tts("AIRIS is ready"), 1)
        return root

    def start_scan(self, *args):
        self.status.text = "Scanning"
        self.safe_tts("Scanning")

        # let camera stabilize
        Clock.schedule_once(self.capture_image, 1.2)

    def capture_image(self, dt):
        if not self.camera.texture:
            self.status.text = "Camera not ready"
            self.safe_tts("Camera not ready")
            return

        try:
            texture = self.camera.texture
            size = texture.size
            pixels = texture.pixels

            image = Image.frombytes(
                "RGBA",
                size,
                pixels
            ).convert("RGB")

            # run AI in background (CRITICAL)
            threading.Thread(
                target=self.send_to_ai,
                args=(image,),
                daemon=True
            ).start()

        except Exception:
            self.update_result("Camera error")

    def send_to_ai(self, image):
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=80)
        buf.seek(0)

        try:
            response = requests.post(
                SERVER_URL,
                files={"image": buf},
                timeout=8
            )

            data = response.json()
            detected = data.get("detected", [])

            # Only what we care about
            detected = [d for d in detected if d in ("person", "chair")]

            if detected:
                result = "Detected " + " and ".join(detected)
            else:
                result = "No person or chair detected"

        except Exception:
            result = "AI server not reachable"

        self.update_result(result)

    @mainthread
    def update_result(self, text):
        self.status.text = text
        self.safe_tts(text)

    def safe_tts(self, text):
        try:
            tts.speak(text)
        except Exception:
            pass


if __name__ == "__main__":
    AirisApp().run()
