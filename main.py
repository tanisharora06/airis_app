from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.camera import Camera

from plyer import tts
from plyer import audio
from plyer import camera as plyer_camera
from plyer import speechrecognition

import os
import time

class AIRISApp(App):

    def build(self):
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        self.label = Label(
            text="AIRIS Ready",
            font_size=24
        )

        self.btn = Button(
            text="Start AIRIS",
            size_hint=(1, 0.3)
        )
        self.btn.bind(on_press=self.start_airis)

        self.layout.add_widget(self.label)
        self.layout.add_widget(self.btn)

        return self.layout

    def speak(self, text):
        tts.speak(text)

    def start_airis(self, instance):
        self.speak("Starting camera and voice systems")
        self.label.text = "Opening camera..."
        Clock.schedule_once(self.auto_capture, 1)

    def auto_capture(self, dt):
        filename = f"/sdcard/airis_{int(time.time())}.jpg"

        try:
            plyer_camera.take_picture(
                filename=filename,
                on_complete=self.on_picture_taken
            )
        except Exception as e:
            self.label.text = "Camera failed"
            print("Camera error:", e)

    def on_picture_taken(self, filepath):
        self.label.text = "Image captured"
        self.speak("Image captured")

        # After image → start voice command
        Clock.schedule_once(self.listen_command, 1)

    def listen_command(self, dt):
        try:
            self.label.text = "Listening..."
            self.speak("Listening")

            speechrecognition.start(
                on_result=self.on_voice_result,
                on_error=self.on_voice_error
            )
        except Exception as e:
            print("Voice error:", e)

    def on_voice_result(self, text):
        text = text.lower()
        self.label.text = f"You said: {text}"

        if "scan" in text:
            self.speak("Scanning image")
            self.scan_image()
        elif "exit" in text:
            self.speak("Closing application")
            App.get_running_app().stop()
        else:
            self.speak("Command not recognized")

    def on_voice_error(self, error):
        self.label.text = "Voice error"
        print("Speech error:", error)

    def scan_image(self):
        # Placeholder for ML / OCR
        # TensorFlow Lite can be added later
        self.speak("Image scanning complete")
        self.label.text = "Scan complete"


if __name__ == "__main__":
    AIRISApp().run()
