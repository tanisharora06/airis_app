import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import platform

from plyer import camera, tts

# Android-only imports (safe guarded)
if platform == "android":
    from android.permissions import request_permissions, Permission
    from android.storage import app_storage_path


class AIRIS(App):

    def build(self):
        self.image_path = None

        self.layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=20
        )

        self.status = Label(
            text="AIRIS ready",
            font_size="20sp"
        )

        self.btn = Button(
            text="Scan",
            size_hint=(1, 0.3)
        )
        self.btn.bind(on_press=self.start_scan)

        self.layout.add_widget(self.status)
        self.layout.add_widget(self.btn)

        if platform == "android":
            Clock.schedule_once(self.request_android_permissions, 0)

        return self.layout

    def request_android_permissions(self, dt):
        try:
            request_permissions([
                Permission.CAMERA,
                Permission.RECORD_AUDIO,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])
            self.status.text = "Permissions granted"
        except Exception as e:
            print("Permission error:", e)
            self.status.text = "Permission error"

    def start_scan(self, *args):
        self.status.text = "Opening camera"
        tts.speak("Opening camera")
        Clock.schedule_once(self.open_camera, 1)

    def open_camera(self, dt):
        try:
            if platform == "android":
                base_path = app_storage_path()
            else:
                base_path = os.getcwd()

            self.image_path = os.path.join(base_path, "scan.jpg")

            # Android camera intent (NO CALLBACK — intentional)
            camera.take_picture(
                filename=self.image_path,
                on_complete=None
            )

            # Wait for camera app to return
            Clock.schedule_once(self.verify_image, 4)

        except Exception as e:
            print("Camera launch error:", e)
            self.status.text = "Camera failed"
            tts.speak("Camera failed")

    def verify_image(self, dt):
        try:
            if self.image_path and os.path.exists(self.image_path):
                self.status.text = "Image captured"
                tts.speak("Image captured successfully")
            else:
                self.status.text = "No image captured"
                tts.speak("Camera closed without image")
        except Exception as e:
            print("Verification error:", e)
            self.status.text = "Image check failed"


if __name__ == "__main__":
    AIRIS().run()
