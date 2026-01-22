from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import platform

from plyer import camera, tts

import os

# ANDROID PERMISSIONS (RUNTIME)
if platform == "android":
    from android.permissions import request_permissions, Permission


class AIRIS(App):

    def request_android_permissions(self):
        if platform != "android":
            return

        request_permissions([
            Permission.CAMERA,
            Permission.RECORD_AUDIO,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
        ])

    def build(self):
        # 🔥 MUST be first
        self.request_android_permissions()

        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        self.label = Label(
            text="Tap Scan to use camera",
            font_size="20sp"
        )

        btn = Button(
            text="Scan",
            size_hint=(1, 0.3)
        )
        btn.bind(on_press=self.start_scan)

        layout.add_widget(self.label)
        layout.add_widget(btn)

        return layout

    def start_scan(self, *args):
        self.label.text = "Opening camera..."

        try:
            if platform == "android":
                from android.storage import app_storage_path
                path = app_storage_path()
            else:
                path = os.getcwd()

            image_path = os.path.join(path, "scan.jpg")

            camera.take_picture(
                filename=image_path,
                on_complete=self.after_picture
            )

        except Exception as e:
            self.label.text = "Camera failed"
            print("Camera error:", e)
            tts.speak("Camera failed")

    def after_picture(self, image_path):
        if not image_path:
            self.label.text = "No image captured"
            return

        self.label.text = "Image captured"
        tts.speak("Image captured successfully")


if __name__ == "__main__":
    AIRIS().run()
