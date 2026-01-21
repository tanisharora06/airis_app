from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class AIRIS(App):
    def build(self):
        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=20
        )

        self.label = Label(
            text="AIRIS is running",
            font_size="22sp"
        )

        button = Button(
            text="Press Me",
            font_size="20sp"
        )
        button.bind(on_press=self.on_button)

        layout.add_widget(self.label)
        layout.add_widget(button)

        return layout

    def on_button(self, *args):
        self.label.text = "AIRIS speaking..."

        try:
            from plyer import tts
            tts.speak("AIRIS is now active")
        except Exception as e:
            self.label.text = "Text to speech failed"
            print(e)


if __name__ == "__main__":
    AIRIS().run()
