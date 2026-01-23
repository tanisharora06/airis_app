from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivy.clock import Clock
import speech_recognition as sr
from plyer import tts, audio
import numpy as np
from PIL import Image
import tflite_runtime.interpreter as tflite
import tempfile
import os

# Load the TensorFlow Lite model for object recognition (MobileNetV2)
MODEL_PATH = 'mobilenet_v2_1.0_224.tflite'
LABELS_PATH = 'labels.txt'

class AirisApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        
        self.camera = Camera(play=True, resolution=(640, 480))
        self.layout.add_widget(self.camera)
        
        self.listen_button = Button(text='Start Voice Listening', size_hint=(1, 0.1))
        self.listen_button.bind(on_press=self.start_listening)
        self.layout.add_widget(self.listen_button)
        
        self.status_label = Label(text='Say "take photo" to capture', size_hint=(1, 0.1))
        self.layout.add_widget(self.status_label)
        
        self.recognizer = sr.Recognizer()
        
        self.interpreter = tflite.Interpreter(model_path=MODEL_PATH)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        with open(LABELS_PATH, 'r') as f:
            self.labels = [line.strip() for line in f.readlines()]
        
        return self.layout
    
    def start_listening(self, instance):
        self.status_label.text = 'Listening for command...'
        tts.speak('Listening for command')
        
        Clock.schedule_once(self.listen_for_command, 0)
    
    def listen_for_command(self, dt):
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            audio.record(filename=temp_path, duration=5)
            
            with sr.AudioFile(temp_path) as source:
                audio_data = self.recognizer.record(source)
                command = self.recognizer.recognize_google(audio_data).lower()
                
                if 'take photo' in command or 'capture' in command:
                    self.capture_and_process_photo()
                else:
                    self.status_label.text = f'Command not recognized: {command}'
            
            os.unlink(temp_path)
        except sr.UnknownValueError:
            self.status_label.text = 'Could not understand audio'
        except sr.RequestError:
            self.status_label.text = 'Speech recognition service unavailable'
        except Exception as e:
            self.status_label.text = f'Error: {str(e)}'
    
    def capture_and_process_photo(self):
        self.status_label.text = 'Capturing photo...'
        tts.speak('Capturing photo')
        
        texture = self.camera.texture
        if texture:
            size = texture.size
            pixels = texture.pixels
            image = Image.frombytes('RGBA', size, pixels).convert('RGB')
            
            image = image.resize((224, 224))
            image_array = np.array(image).astype(np.float32)
            image_array = np.expand_dims(image_array, axis=0)
            image_array = image_array / 255.0
            
            self.interpreter.set_tensor(self.input_details[0]['index'], image_array)
            self.interpreter.invoke()
            output = self.interpreter.get_tensor(self.output_details[0]['index'])
            
            top_indices = np.argsort(output[0])[-5:][::-1]
            detected_objects = [self.labels[i] for i in top_indices if output[0][i] > 0.5]
            
            if detected_objects:
                result_text = f'Detected: {", ".join(detected_objects)}'
                self.status_label.text = result_text
                tts.speak(result_text)
            else:
                self.status_label.text = 'No objects detected'
                tts.speak('No objects detected')
        else:
            self.status_label.text = 'Failed to capture photo'
            tts.speak('Failed to capture photo')

if __name__ == '__main__':
    AirisApp().run()
