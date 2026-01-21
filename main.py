from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.utils import platform

IS_ANDROID = platform == "android"


class AIRIS(App):
    def build(self):
        layout = BoxLayout(
            orientation="vertical",
            padding=30,
            spacing=20
        )

        self.label = Label(
            text="AIRIS is running ✅",
            font_size="22sp",
            halign="center",
            valign="middle"
        )
        self.label.bind(size=self.label.setter("text_size"))

        btn = Button(
            text="Test Button",
            size_hint=(1, 0.3)
        )
        btn.bind(on_press=self.on_button)

        layout.add_widget(self.label)
        layout.add_widget(btn)

        if IS_ANDROID:
            self.request_android_permissions()

        return layout

    def on_button(self, *args):
        self.label.text = "Button works 🎉"

    def request_android_permissions(self):
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.CAMERA,
                Permission.RECORD_AUDIO,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])
        except Exception as e:
            print("Permission error:", e)


if __name__ == "__main__":
    AIRIS().run()
