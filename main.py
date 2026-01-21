from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from plyer import camera


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

        button = Button(
            text="Take Photo",
            font_size="20sp"
        )
        button.bind(on_press=self.take_photo)

        layout.add_widget(self.label)
        layout.add_widget(button)

        return layout

    def take_photo(self, *args):
        try:
            self.label.text = "Opening camera..."
            camera.take_picture(
                filename="/sdcard/airis_test.jpg",
                on_complete=self.after_photo
            )
        except Exception as e:
            self.label.text = "Camera failed"
            print(e)

    def after_photo(self, path):
        self.label.text = "Photo saved!"
        print("Saved to:", path)


if __name__ == "__main__":
    AIRIS().run()
