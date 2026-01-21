from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import platform
from plyer import camera

if platform == "android":
    from android.permissions import request_permissions, Permission


class AIRIS(App):
    def build(self):
        self.layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=20
        )

        self.label = Label(
            text="AIRIS ready",
            font_size="22sp"
        )

        self.button = Button(
            text="Take Photo",
            font_size="20sp"
        )
        self.button.bind(on_press=self.start_camera)

        self.layout.add_widget(self.label)
        self.layout.add_widget(self.button)

        if platform == "android":
            request_permissions([
                Permission.CAMERA,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])

        return self.layout

    def start_camera(self, *args):
        self.label.text = "Opening camera..."

        try:
            camera.take_picture(
                filename="/sdcard/airis_test.jpg",
                on_complete=self.after_photo
            )
        except Exception as e:
            self.label.text = "Camera error"
            print("Camera exception:", e)

    def after_photo(self, path):
        if path:
            self.label.text = "Photo saved!"
            print("Saved to:", path)
        else:
            self.label.text = "No photo taken"


if __name__ == "__main__":
    AIRIS().run()
