from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from plyer import tts


class AIRIS(App):
    def build(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        self.label = Label(
            text="AIRIS Loaded Successfully",
            font_size="22sp"
        )

        speak_btn = Button(text="Test Speak")
        speak_btn.bind(on_press=self.speak)

        layout.add_widget(self.label)
        layout.add_widget(speak_btn)

        return layout

    def speak(self, *args):
        self.label.text = "Speaking works"
        tts.speak("AIRIS is working correctly")


if __name__ == "__main__":
    AIRIS().run()
