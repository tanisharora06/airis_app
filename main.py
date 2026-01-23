from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform

if platform == "android":
    from android.permissions import request_permissions, Permission
    from jnius import autoclass


class AIRIS(App):
    def build(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        self.label = Label(text="AIRIS Ready", font_size="22sp")
        btn = Button(text="Open Camera", size_hint=(1, 0.3))
        btn.bind(on_press=self.open_camera)

        layout.add_widget(self.label)
        layout.add_widget(btn)

        if platform == "android":
            request_permissions([Permission.CAMERA])

        return layout

    def open_camera(self, *args):
        if platform != "android":
            self.label.text = "Android only"
            return

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Intent = autoclass("android.content.Intent")
        MediaStore = autoclass("android.provider.MediaStore")
        Toast = autoclass("android.widget.Toast")

        activity = PythonActivity.mActivity
        intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)

        # 🔒 Critical check
        if intent.resolveActivity(activity.getPackageManager()) is None:
            Toast.makeText(activity, "No camera app found", Toast.LENGTH_LONG).show()
            self.label.text = "No camera app"
            return

        Toast.makeText(activity, "Opening camera…", Toast.LENGTH_SHORT).show()
        activity.startActivity(intent)


if __name__ == "__main__":
    AIRIS().run()
