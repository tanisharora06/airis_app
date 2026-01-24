from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.clock import Clock
from plyer import tts
from android.permissions import request_permissions, Permission
from random import choice


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

        self.auto_btn = Button(text="Auto Scan")
        self.auto_btn.bind(on_press=self.toggle_auto_scan)
        controls.add_widget(self.auto_btn)

        self.voice_btn = Button(text="Voice Command")
        self.voice_btn.bind(on_press=self.voice_command)
        controls.add_widget(self.voice_btn)

        self.root.add_widget(controls)

        self.auto_event = None
        tts.speak("AIRIS is ready")
        return self.root

    # ---------- FEATURES ----------

    def capture(self, instance):
        self.status.text = "Capturing image"
        tts.speak("Capturing image")
        Clock.schedule_once(self.scan_image, 1)

    def toggle_auto_scan(self, instance):
        if self.auto_event:
            self.auto_event.cancel()
            self.auto_event = None
            self.status.text = "Auto scan stopped"
            tts.speak("Auto scan stopped")
        else:
            self.status.text = "Auto scan started"
            tts.speak("Auto scan started")
            self.auto_event = Clock.schedule_interval(self.auto_scan, 6)

    def auto_scan(self, dt):
        if not self.camera.texture:
            self.status.text = "Camera unavailable"
            return
        self.status.text = "Scanning environment"
        Clock.schedule_once(self.scan_image, 1)

    def voice_command(self, instance):
        # SAFE voice feature (Android-friendly)
        self.status.text = "Voice command activated"
        tts.speak("Say scan or auto scan")

        # Simulated recognition (real mic processing comes later)
        command = choice(["scan", "auto"])

        if command == "scan":
            self.capture(None)
        elif command == "auto":
            self.toggle_auto_scan(None)

    def scan_image(self, dt):
        if not self.camera.texture:
            self.status.text = "Capture failed"
            tts.speak("Capture failed")
            return

        result = self.ai_detect()
        self.status.text = result
        tts.speak(result)

    def ai_detect(self):
        # Placeholder AI (real ML plugs in HERE)
        results = [
            "Detected: person",
            "Detected: chair",
            "Detected: table",
            "Detected: phone",
            "Detected: bottle"
        ]
        return choice(results)


if __name__ == "__main__":
    AirisApp().run()
