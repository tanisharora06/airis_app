import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import platform

from plyer import camera, tts

# Android-specific imports
if platform == "android":
    from android.permissions import request_permissions, Permission
    from android.storage import app_storage_path


class AIRIS(App):

    def build(self):
        self.layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=20
        )

        self.status = Label(
            text="AIRIS ready",
            font_size="20sp"
        )

        self.scan_button = Button(
            text="Scan",
            size_hint=(1, 0.3)
        )
        self.scan_button.bind(on_press=self.on_scan_pressed)

        self.layout.add_widget(self.status)
        self.layout.add_widget(self.scan_button)

        # Request permissions after UI loads
        if platform == "android":
            Clock.schedule_once(self.request_android_permissions, 0.5)

        return self.layout

    def request_android_permissions(self, dt):
        request_permissions([
            Permission.CAMERA,
            Permission.RECORD_AUDIO,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
        ])
        self.status.text = "Permissions ready"

    def on_scan_pressed(self, *args):
        self.status.text = "Preparing camera"
        tts.speak("Opening camera")

        # Delay is REQUIRED on Android
        Clock.schedule_once(self.start_camera, 1.5)

    def start_camera(self, dt):
        try:
            if platform == "android":
                base_path = app_storage_path()
            else:
                base_path = os.getcwd()

            image_path = os.path.join(base_path, "scan.jpg")

            self.status.text = "Camera open"
            camera.take_picture(
                filename=image_path,
                on_complete=self.after_picture
            )

        except Exception as e:
            print("Camera error:", e)
            self.status.text = "Camera failed"
            tts.speak("Camera failed")

    def after_picture(self, image_path):
        if not image_path:
            self.status.text = "No image captured"
            tts.speak("No image captured")
            return

        self.status.text = "Image captured"
        tts.speak("Image captured successfully")


if __name__ == "__main__":
    AIRIS().run()
