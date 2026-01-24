from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.clock import Clock
from plyer import tts
from android.permissions import request_permissions, Permission


class AirisApp(App):

    def build(self):
        request_permissions([
            Permission.CAMERA,
            Permission.RECORD_AUDIO
        ])

        self.root = BoxLayout(orientation='vertical')

        self.status = Label(
            text="AIRIS ready",
            size_hint=(1, 0.15),
            font_size='18sp'
        )
        self.root.add_widget(self.status)

        self.camera = Camera(
            play=True,
            resolution=(640, 480),
            size_hint=(1, 0.7)
        )
        self.root.add_widget(self.camera)

        controls = BoxLayout(size_hint=(1, 0.15))

        self.scan_btn = Button(text="Scan Now")
        self.scan_btn.bind(on_press=self.manual_scan)
        controls.add_widget(self.scan_btn)

        self.auto_btn = Button(text="Auto Scan")
        self.auto_btn.bind(on_press=self.start_auto_scan)
        controls.add_widget(self.auto_btn)

        self.root.add_widget(controls)

        tts.speak("AIRIS is ready")
        return self.root

    def manual_scan(self, instance):
        self.status.text = "Capturing image"
        tts.speak("Capturing image")
        Clock.schedule_once(self.analyze_image, 1)

    def start_auto_scan(self, instance):
        self.status.text = "Auto scan started"
        tts.speak("Auto scan started")
        self.auto_event = Clock.schedule_interval(self.auto_scan, 6)

    def auto_scan(self, dt):
        if not self.camera.texture:
            self.status.text = "Camera unavailable"
            return
        self.status.text = "Scanning environment"
        Clock.schedule_once(self.analyze_image, 1)

    def analyze_image(self, dt):
        if not self.camera.texture:
            self.status.text = "Capture failed"
            tts.speak("Capture failed")
            return

        # SAFE fake AI result (real ML comes next)
        detected = self.fake_detection()
        self.status.text = detected
        tts.speak(detected)

    def fake_detection(self):
        # Rotate fake results to feel real
        results = [
            "Detected object: chair",
            "Detected object: table",
            "Detected object: person",
            "Detected object: bottle"
        ]
        from random import choice
        return choice(results)


if __name__ == "__main__":
    AirisApp().run()
