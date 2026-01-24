from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.clock import Clock
from plyer import tts

import numpy as np
from PIL import Image
import tflite_runtime.interpreter as tflite


MODEL_PATH = "mobilenet_v2_1.0_224.tflite"
LABELS_PATH = "labels.txt"


class AirisApp(App):

    def build(self):
        self.root = BoxLayout(orientation="vertical")

        self.status = Label(
            text="AIRIS ready",
            size_hint=(1, 0.15),
            font_size="18sp"
        )
        self.root.add_widget(self.status)

        self.camera = Camera(
            play=True,
            resolution=(640, 480),
            size_hint=(1, 0.7)
        )
        self.root.add_widget(self.camera)

        btn = Button(
            text="Scan",
            size_hint=(1, 0.15)
        )
        btn.bind(on_press=self.scan)
        self.root.add_widget(btn)

        self.load_ai()
        tts.speak("AIRIS is ready")

        return self.root

    def load_ai(self):
        self.interpreter = tflite.Interpreter(model_path=MODEL_PATH)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        with open(LABELS_PATH, "r") as f:
            self.labels = [l.strip() for l in f.readlines()]

    def scan(self, instance):
        self.status.text = "Scanning"
        tts.speak("Scanning")
        Clock.schedule_once(self.analyze, 1)

    def analyze(self, dt):
        if not self.camera.texture:
            self.status.text = "Camera error"
            return

        texture = self.camera.texture
        image = Image.frombytes(
            "RGBA",
            texture.size,
            texture.pixels
        ).convert("RGB")

        image = image.resize((224, 224))
        input_data = np.expand_dims(image, axis=0).astype(np.float32) / 255.0

        self.interpreter.set_tensor(
            self.input_details[0]["index"],
            input_data
        )
        self.interpreter.invoke()

        output = self.interpreter.get_tensor(
            self.output_details[0]["index"]
        )[0]

        top = int(np.argmax(output))
        label = self.labels[top]

        result = f"I see {label}"
        self.status.text = result
        tts.speak(result)


if __name__ == "__main__":
    AirisApp().run()
