from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.clock import Clock
from plyer import tts
from android.permissions import request_permissions, Permission

import numpy as np
from PIL import Image
import tflite_runtime.interpreter as tflite


MODEL_PATH = "mobilenet_v2_1.0_224.tflite"
LABELS_PATH = "labels.txt"


class AirisApp(App):

    def build(self):
        request_permissions([
            Permission.CAMERA,
            Permission.RECORD_AUDIO
        ])

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
            size_hint=(1, 0.65)
        )
        self.root.add_widget(self.camera)

        controls = BoxLayout(size_hint=(1, 0.2))

        self.capture_btn = Button(text="Capture & Scan")
        self.capture_btn.bind(on_press=self.capture)
        controls.add_widget(self.capture_btn)

        self.root.add_widget(controls)

        self.load_ai()
        tts.speak("AIRIS ready with real AI")
        return self.root

    # ---------- AI SETUP ----------

    def load_ai(self):
        self.interpreter = tflite.Interpreter(model_path=MODEL_PATH)
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        with open(LABELS_PATH, "r") as f:
            self.labels = [line.strip() for line in f.readlines()]

    # ---------- FEATURES ----------

    def capture(self, instance):
        self.status.text = "Capturing image"
        tts.speak("Capturing image")
        Clock.schedule_once(self.scan_image, 1)

    def scan_image(self, dt):
        texture = self.camera.texture
        if not texture:
            self.status.text = "Camera error"
            tts.speak("Camera error")
            return

        image = Image.frombytes(
            "RGBA",
            texture.size,
            texture.pixels
        ).convert("RGB")

        image = image.resize((224, 224))
        image_array = np.array(image, dtype=np.float32)
        image_array = np.expand_dims(image_array, axis=0)
        image_array = image_array / 255.0

        self.interpreter.set_tensor(
            self.input_details[0]["index"],
            image_array
        )
        self.interpreter.invoke()

        output = self.interpreter.get_tensor(
            self.output_details[0]["index"]
        )[0]

        top_index = int(np.argmax(output))
        confidence = float(output[top_index])

        if confidence > 0.5:
            label = self.labels[top_index]
            result = f"{label} ({confidence:.2f})"
        else:
            result = "No clear object detected"

        self.status.text = result
        tts.speak(result)


if __name__ == "__main__":
    AirisApp().run()
