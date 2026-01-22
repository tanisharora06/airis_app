from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform

# Android-only imports (SAFE)
if platform == "android":
    from android.permissions import request_permissions, Permission
    from jnius import autoclass


class AIRIS(App):

    def build(self):
        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=20
        )

        self.label = Label(
            text="AIRIS ready",
            font_size="22sp"
        )

        btn = Button(
            text="Open Camera",
            size_hint=(1, 0.3)
        )
        btn.bind(on_press=self.open_camera)

        layout.add_widget(self.label)
        layout.add_widget(btn)

        # Request permission once app loads
        if platform == "android":
            request_permissions([Permission.CAMERA])

        return layout

    def open_camera(self, *args):
        if platform != "android":
            self.label.text = "Camera only works on Android"
            return

        self.label.text = "Opening camera..."

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Intent = autoclass("android.content.Intent")
        MediaStore = autoclass("android.provider.MediaStore")

        activity = PythonActivity.mActivity
        intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        activity.startActivity(intent)


if __name__ == "__main__":
    AIRIS().run()
