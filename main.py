import json
import os
import tempfile
import threading
import time
from collections import deque

from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar

from plyer import tts

from PIL import Image

from android.permissions import Permission, request_permissions
from jnius import autoclass


MIN_CONFIDENCE = 0.40
ANNOUNCE_GAP_SECONDS = 2.0


class AirisApp(App):
    def build(self):
        self.last_announcement = ""
        self.last_announcement_time = 0.0
        self.is_scanning = False
        self.recent_results = deque(maxlen=5)
        self.detector_ready = False

        root = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(10),
        )

        self.status = Label(
            text="Requesting permissions…",
            size_hint=(1, None),
            height=dp(42),
            font_size="18sp",
            bold=True,
            halign="left",
            valign="middle",
            text_size=(0, None),
        )
        self.status.bind(size=self._fit_status)
        root.add_widget(self.status)

        self.camera = Camera(
            play=False,
            resolution=(1280, 720),
            size_hint=(1, 0.72),
        )
        root.add_widget(self.camera)

        controls = BoxLayout(size_hint=(1, None), height=dp(110), spacing=dp(8))
        self.scan_btn = Button(text="Start scan", disabled=True)
        self.scan_btn.bind(on_press=self.toggle_scan)
        controls.add_widget(self.scan_btn)

        self.result = Label(
            text="Detected objects will appear here",
            halign="left",
            valign="top",
            text_size=(0, None),
            size_hint=(1, 1),
            font_size="15sp",
        )
        self.result.bind(size=self._fit_result)
        controls.add_widget(self.result)
        root.add_widget(controls)

        self.progress = ProgressBar(max=100, value=0, size_hint=(1, None), height=dp(8))
        root.add_widget(self.progress)

        Clock.schedule_once(self.ask_permissions, 0.2)
        return root

    def _fit_status(self, *_):
        self.status.text_size = (self.status.width, None)

    def _fit_result(self, *_):
        self.result.text_size = (self.result.width, None)

    def ask_permissions(self, _dt):
        request_permissions(
            [
                Permission.CAMERA,
                Permission.RECORD_AUDIO,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
            ],
            self.on_permissions_result,
        )

    def on_permissions_result(self, _permissions, grants):
        if all(grants):
            self.camera.play = True
            self.status.text = "Initializing detector…"
            threading.Thread(target=self.init_detector, daemon=True).start()
            return

        self.status.text = "Permissions denied"

    def init_detector(self):
        try:
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Detector = autoclass("org.airis.Detector")
            current_activity = PythonActivity.mActivity
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, "ssd_mobilenet_v2_fpnlite_320x320.tflite")
            labels_path = os.path.join(base_dir, "labels.txt")
            ok = Detector.initialize(current_activity, model_path, labels_path)
            self.detector_ready = bool(ok)
        except Exception:
            self.detector_ready = False

        self.on_detector_ready()

    @mainthread
    def on_detector_ready(self):
        if self.detector_ready:
            self.status.text = "AIRIS ready"
            self.scan_btn.disabled = False
            self.safe_tts("AIRIS is ready")
        else:
            self.status.text = "Detector failed to initialize"

    def toggle_scan(self, *_args):
        if not self.is_scanning:
            self.is_scanning = True
            self.scan_btn.text = "Stop scan"
            self.status.text = "Scanning continuously"
            self.safe_tts("Scanning started")
            self.progress.value = 5
            Clock.schedule_interval(self.scan_once, 0.9)
        else:
            self.is_scanning = False
            self.scan_btn.text = "Start scan"
            self.status.text = "Scan stopped"
            self.progress.value = 0
            Clock.unschedule(self.scan_once)

    def scan_once(self, _dt):
        if not self.camera.texture or not self.detector_ready:
            return

        self.progress.value = min(95, self.progress.value + 15)
        threading.Thread(target=self.detect_from_camera, daemon=True).start()

    def detect_from_camera(self):
        try:
            texture = self.camera.texture
            image = Image.frombytes("RGBA", texture.size, texture.pixels).convert("RGB")
            image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as fp:
                tmp_path = fp.name
            image.save(tmp_path, format="JPEG", quality=88)

            detections = self.run_detector(tmp_path)
            os.remove(tmp_path)
            self.update_result(detections)
        except Exception:
            self.update_result([])

    def run_detector(self, image_path):
        Detector = autoclass("org.airis.Detector")
        raw = Detector.analyze(image_path)

        try:
            parsed = json.loads(raw)
        except Exception:
            return []

        return [
            item
            for item in parsed
            if item.get("score", 0.0) >= MIN_CONFIDENCE
        ]

    @mainthread
    def update_result(self, detections):
        self.progress.value = 100 if detections else 30

        if not detections:
            message = "No confident objects detected"
            self.status.text = message
            self.result.text = message
            self._announce(message)
            return

        labels = []
        for item in detections[:4]:
            label = item.get("label", "object")
            score = float(item.get("score", 0.0))
            labels.append(f"{label} ({score:.0%})")

        stable = self._stabilized_label(labels)
        message = f"Detected: {stable}"
        self.status.text = "Live detection active"
        self.result.text = message
        self._announce(stable)
        self.progress.value = 55

    def _stabilized_label(self, labels):
        label_text = ", ".join(labels)
        self.recent_results.append(label_text)

        counts = {}
        for item in self.recent_results:
            counts[item] = counts.get(item, 0) + 1

        return max(counts, key=counts.get)

    def _announce(self, text):
        now = time.time()
        if text == self.last_announcement and (now - self.last_announcement_time) < ANNOUNCE_GAP_SECONDS:
            return

        self.last_announcement = text
        self.last_announcement_time = now
        self.safe_tts(text)

    @staticmethod
    def safe_tts(text):
        try:
            tts.speak(text)
        except Exception:
            pass


if __name__ == "__main__":
    AirisApp().run()
