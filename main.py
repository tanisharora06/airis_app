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

from android.permissions import request_permissions, Permission

SERVER_URL = "https://YOUR_SERVER_URL/detect"


class AirisApp(App):

    def build(self):
        self.root = BoxLayout(
            orientation="vertical",
            padding=8,
            spacing=8
        )

        self.status = Label(
            text="Requesting permissions...",
            size_hint=(1, 0.15),
            font_size="18sp"
        )
        self.root.add_widget(self.status)

        self.scan_btn = Button(
            text="Scan",
            size_hint=(1, 0.15),
            disabled=True
        )
        self.scan_btn.bind(on_press=self.start_scan)
        self.root.add_widget(self.scan_btn)

        # ASK PERMISSIONS FIRST
        Clock.schedule_once(self.ask_permissions, 0.5)

        return self.root

    def ask_permissions(self, dt):
        request_permissions(
            [
                Permission.CAMERA,
                Permission.INTERNET,
                Permission.RECORD_AUDIO
            ],
            self.on_permissions_result
        )

    def on_permissions_result(self, permissions, grants):
        if all(grants):
            Clock.schedule_once(self.init_camera, 0)
        else:
            self.status.text = "Permissions denied"

    def init_camera(self, dt):
        self.status.text = "AIRIS ready"

        self.camera = Camera(
            play=True,
            resolution=(640, 480),
            size_hint=(1, 0.7)
        )
        self.root.add_widget(self.camera, index=1)

        self.scan_btn.disabled = False

        self.safe_tts("AIRIS is ready")

    def start_scan(self, *args):
        self.status.text = "Scanning"
        self.safe_tts("Scanning")
        Clock.schedule_once(self.capture_image, 1.2)

    def capture_image(self, dt):
        if not self.camera.texture:
            self.update_result("Camera not ready")
            return

        try:
            texture = self.camera.texture
            image = Image.frombytes(
                "RGBA",
                texture.size,
                texture.pixels
            ).convert("RGB")

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
