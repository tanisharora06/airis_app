from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.uix.popup import Popup

import platform
import threading
import os
import time
from PIL import Image as PILImage

IS_ANDROID = platform.system() == "Linux" and "ANDROID_STORAGE" in os.environ
LANGUAGE = 'hi-IN'
KNOWN_VOICE_NAME = "your_name"

if not IS_ANDROID:
    try:
        import speech_recognition as sr
        desktop_voice = True
    except ImportError:
        desktop_voice = False
else:
    from plyer import speech
    desktop_voice = False

if IS_ANDROID:
    from plyer import tts
else:
    try:
        import pyttsx3
        tts_engine = pyttsx3.init('sapi5')
        tts_engine.setProperty('rate', 175)
        tts_engine.setProperty('volume', 1.0)
        has_tts = True
    except ImportError:
        has_tts = False

try:
    import cv2
    has_cv2 = True
except ImportError:
    has_cv2 = False

try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
    import torch
    has_caption = True
except ImportError:
    has_caption = False

from ultralytics import YOLO

Window.size = (360, 640)
Window.clearcolor = get_color_from_hex('#113768')  # background color

class TFLiteRoadAnalyzer:
    def __init__(self):
        self.caption_model = None
        self.caption_processor = None
        self.caption_loaded = False

        self.important_classes = {
            'person', 'dog', 'cat', 'car', 'bus', 'truck', 'motorbike', 'bicycle',
            'auto rickshaw', 'traffic light', 'stop sign', 'fire hydrant', 'cow',
            'horse', 'pothole', 'pillar', 'zebra crossing', 'wheelchair', 'rickshaw',
            'shopping cart', 'construction barrier', 'open manhole', 'ramp',
            'stairs', 'walker', 'cane', 'guide dog', 'traffic signal', 'barrier',
            'bollard', 'manhole', 'school bus', 'ambulance', 'police car', 'container'
        }

        self.alert_classes = {
            'pothole', 'pillar', 'open manhole', 'construction barrier',
            'bollard', 'barrier', 'cow', 'rickshaw'
        }

        print("[A.I.ris] Loading YOLOv8n model...")
        self.model = YOLO("yolov8n.pt")

    def load_caption_model(self):
        if self.caption_loaded or not has_caption:
            return
        try:
            self.caption_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.caption_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            self.caption_loaded = True
        except Exception as e:
            print(f"Captioning load failed: {e}")

    def generate_caption(self, image_path):
        self.load_caption_model()
        if not self.caption_loaded:
            return ""
        try:
            image = PILImage.open(image_path).convert("RGB")
            inputs = self.caption_processor(images=image, return_tensors="pt")
            out = self.caption_model.generate(**inputs, max_length=50)
            return self.caption_processor.decode(out[0], skip_special_tokens=True)
        except Exception as e:
            return f"(captioning error: {e})"

    def analyze(self, image_path):
        results = self.model(image_path, imgsz=640, verbose=False)
        detections = results[0]
        if detections is None or detections.boxes is None:
            return "The road ahead looks clear."

        boxes = detections.boxes.xyxy.cpu().numpy()
        labels = [self.model.names[int(cls)] for cls in detections.boxes.cls]
        image_width = detections.orig_shape[1]

        return self.describe_objects(labels, boxes, image_width)

    def describe_objects(self, labels, boxes, image_width):
        summary = []
        alerts = []

        for i, label in enumerate(labels):
            if label not in self.important_classes:
                continue

            x1, y1, x2, y2 = boxes[i]
            obj_center_x = (x1 + x2) / 2
            obj_height = y2 - y1

            if obj_center_x < image_width * 0.33:
                direction = "to your left"
            elif obj_center_x > image_width * 0.66:
                direction = "to your right"
            else:
                direction = "straight ahead"

            if obj_height > 300:
                distance = "less than 1 meter"
            elif obj_height > 150:
                distance = "about 2 meters"
            elif obj_height > 80:
                distance = "around 5 meters"
            else:
                distance = "further ahead"

            phrase = f"There is a {label} {direction}, {distance}."
            summary.append(phrase)
            if label in self.alert_classes:
                alerts.append(f"\u26a0\ufe0f Be cautious: {label} {direction}, {distance}.")

        if not summary:
            return "The road ahead looks clear."

        return " ".join(alerts + summary)

class HomeScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        # Simple blank background instead of PNG
        from kivy.uix.widget import Widget
        self.add_widget(Widget())

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20, size_hint=(1, 1))

        self.label = Label(text='A.I.ris is starting...', font_size='24sp', color=get_color_from_hex('#FFFFFF'), size_hint=(1, 0.4))

        scan_btn = Button(text="Tap for Force Scan", font_size='20sp', background_color=get_color_from_hex('#6C3483'), color=get_color_from_hex('#FFFFFF'), size_hint=(1, 0.2))
        scan_btn.bind(on_press=self.force_scan)

        test_btn = Button(text="Choose Image to Analyze", font_size='20sp', background_color=get_color_from_hex('#884EA0'), color=get_color_from_hex('#FFFFFF'), size_hint=(1, 0.2))
        test_btn.bind(on_press=self.choose_image)

        layout.add_widget(self.label)
        layout.add_widget(scan_btn)
        layout.add_widget(test_btn)

        self.add_widget(layout)

    def force_scan(self, instance):
        self.app.update_status("Manual scan initiated...")
        self.app.speak("Manual scan initiated")
        self.app.capture_photo()

    def choose_image(self, instance):
        chooser = FileChooserIconView(path='.')
        popup = Popup(title="Select Image", size_hint=(0.9, 0.9))

        def select_path(_):
            if chooser.selection:
                selected = chooser.selection[0]
                self.app.analyze_image_from_path(selected)
                popup.dismiss()

        confirm = Button(text="Analyze Selected", size_hint_y=None, height=50)
        confirm.bind(on_press=select_path)

        box = BoxLayout(orientation='vertical')
        box.add_widget(chooser)
        box.add_widget(confirm)

        popup.content = box
        popup.open()

class AIRISApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.home_screen = HomeScreen(self, name='home')
        self.sm.add_widget(self.home_screen)
        self.listening_enabled = True
        self.analyzer = TFLiteRoadAnalyzer()
        self.update_status("Model loaded. Say scan or tap button.")
        self.speak("Models loaded. Say scan or tap the button.")
        if desktop_voice:
            threading.Thread(target=self.continuous_listen, daemon=True).start()
        return self.sm

    def speak(self, text):
        if IS_ANDROID:
            tts.speak(text)
        elif has_tts:
            threading.Thread(target=lambda: (tts_engine.say(text), tts_engine.runAndWait()), daemon=True).start()

    def update_status(self, text):
        Clock.schedule_once(lambda dt: setattr(self.home_screen.label, 'text', text))
        print("[A.I.ris]:", text)

    def continuous_listen(self):
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = False
        trigger_phrases = ["scan", "स्कैन करो", "मेरे आगे क्या है", "look ahead", "scan my surroundings"]

        while True:
            if not self.listening_enabled:
                time.sleep(1)
                continue
            try:
                with sr.Microphone() as source:
                    self.update_status("Listening...")
                    recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)
                try:
                    text = recognizer.recognize_google(audio, language=LANGUAGE).lower()
                    print("Heard:", text)
                    if KNOWN_VOICE_NAME.lower() in text or any(phrase in text for phrase in trigger_phrases):
                        self.update_status("Scanning surroundings...")
                        self.speak("Scanning your surroundings")
                        self.capture_photo()
                except sr.UnknownValueError:
                    self.speak("Sorry, I didn't catch that")
                except sr.RequestError:
                    self.speak("Speech recognition error")
            except Exception as e:
                self.speak(f"Mic error: {e}")

    def capture_photo(self):
        if not has_cv2:
            self.update_status("Camera not available.")
            self.speak("Camera not available.")
            return

        def task():
            self.listening_enabled = False
            self.update_status("Opening camera...")
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.update_status("Camera failed to open.")
                self.speak("Camera failed to open.")
                self.listening_enabled = True
                return
            ret, frame = cap.read()
            cap.release()
            if ret:
                path = os.path.join(os.getcwd(), "scan.jpg")
                cv2.imwrite(path, frame)
                self.analyze_and_speak(path)
            else:
                self.update_status("Failed to capture photo.")
                self.speak("Failed to capture photo.")
            self.listening_enabled = True

        threading.Thread(target=task, daemon=True).start()

    def analyze_and_speak(self, image_path):
        self.update_status("Analyzing image...")
        self.speak("Analyzing image.")
        description = self.analyzer.analyze(image_path)
        caption = self.analyzer.generate_caption(image_path)
        result = f"{caption}. {description}" if caption else description
        self.update_status(result)
        self.speak(result)

    def analyze_image_from_path(self, path):
        if not os.path.isfile(path):
            self.update_status("Invalid image path.")
            self.speak("Invalid image file.")
            return
        self.analyze_and_speak(path)

if __name__ == '__main__':
    AIRISApp().run()
