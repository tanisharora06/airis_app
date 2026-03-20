# AIRIS Android Object Detection

AIRIS is a Kivy Android app that performs **on-device object detection** with a TensorFlow Lite SSD model and supports **hands-free capture**.

## Features

- Requests camera + microphone permission at startup.
- Opens the camera automatically after permissions are granted.
- Continuous object detection with spoken feedback.
- Voice trigger phrase **"scan my surroundings"** captures a picture and analyzes it.

## Build

```bash
buildozer android debug
```

## Run

1. Install the APK on Android.
2. Grant camera + microphone permissions.
3. Wait for the app to say it is ready.
4. Say **"scan my surroundings"** to capture and analyze a photo.
5. Optional: Tap **Start scan** for continuous scanning mode.

## Model files

- `ssd_mobilenet_v2_fpnlite_320x320.tflite`
- `labels.txt`

These files are bundled into the app and loaded by the Android detector bridge.
