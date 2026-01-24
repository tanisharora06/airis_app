from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform
from kivy.clock import Clock

from plyer import tts

if platform == "android":
    from android.permissions import request_permissions, Permission
    from jnius import autoclass


class AIRIS(App):

    def build(self):
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        self.status = Label(
            text="AIRIS Ready",
            font_size="22sp",
            size_hint=(1, 0.3)
        )

        self.camera_btn = Button(text="Open Camera")
        self.voice_btn = Button(text="Voice Command")

        self.camera_btn.bind(on_press=self.open_camera)
        self.voice_btn.bind(on_press=self.start_voice)

        self.layout.add_widget(self.status)
        self.layout.add_widget(self.camera_btn)
        self.layout.add_widget(self.voice_btn)

        if platform == "android":
            request_permissions([
                Permission.CAMERA,
                Permission.RECORD_AUDIO
            ])

        return self.layout

    # ---------- CAMERA ----------
    def open_camera(self, *args):
        if platform != "android":
            self.status.text = "Android only"
            return

        self.status.text = "Opening camera"
        tts.speak("Opening camera")

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Intent = autoclass("android.content.Intent")
        MediaStore = autoclass("android.provider.MediaStore")

        activity = PythonActivity.mActivity
        intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)

        activity.startActivity(intent)

    # ---------- VOICE ----------
    def start_voice(self, *args):
        if platform != "android":
            return

        self.status.text = "Listening"
        tts.speak("Listening")

        Clock.schedule_once(self.launch_voice_intent, 0.5)

    def launch_voice_intent(self, dt):
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Intent = autoclass("android.content.Intent")
        RecognizerIntent = autoclass("android.speech.RecognizerIntent")

        activity = PythonActivity.mActivity
        intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)

        intent.putExtra(
            RecognizerIntent.EXTRA_LANGUAGE_MODEL,
            RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
        )

        activity.startActivity(intent)


if __name__ == "__main__":
    AIRIS().run()
