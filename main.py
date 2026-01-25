from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.clock import Clock
from plyer import tts

from PIL import Image
import requests
import io


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

        scan_btn = Button(text="Scan", size_hint=(1, 0.15))
        scan_btn.bind(on_press=self.start_scan)
        root.add_widget(scan_btn)

        tts.speak("AIRIS is ready")
        return root

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

        self.send_to_ai(image)

    def send_to_ai(self, image):
        buf = io.BytesIO()
        image.save(buf, format="JPEG")
        buf.seek(0)

        try:
            response = requests.post(
                SERVER_URL,
                files={"image": buf},
                timeout=10
            )

            data = response.json()
            detected = data.get("detected", [])

            # filter only person & chair
            detected = [d for d in detected if d in ["person", "chair"]]

            if detected:
                result = "Detected " + " and ".join(detected)
            else:
                result = "No person or chair detected"

        except Exception:
            result = "AI server not reachable"

        self.status.text = result
        tts.speak(result)


if __name__ == "__main__":
    AirisApp().run()
