# AIRIS Android Object Detection

AIRIS is a Kivy Android app that performs **on-device object detection** with a TensorFlow Lite SSD model.

## What changed

- Real object detection now runs locally (no external server needed).
- UI updated for clearer status, live results, and scan controls.
- Continuous scanning mode with smoother, throttled updates and voice feedback.
- Android build config updated to include TensorFlow Lite dependency.

## Build

```bash
buildozer android debug
```

## Run

1. Install the APK on Android.
2. Grant camera + audio permissions.
3. Tap **Start scan** to run live detection.

## Model files

- `ssd_mobilenet_v2_fpnlite_320x320.tflite`
- `labels.txt`

These files are bundled into the app and loaded by the Android detector bridge.
