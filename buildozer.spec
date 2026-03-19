[app]
title = AIRIS
package.name = airis
package.domain = org.airis
version = 0.2

source.dir = .
source.include_exts = py,tflite,txt

requirements = python3,kivy,plyer,pyjnius,pillow

orientation = portrait
fullscreen = 0

android.permissions = CAMERA,RECORD_AUDIO,INTERNET
android.api = 33
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
android.gradle_dependencies = org.tensorflow:tensorflow-lite:2.14.0

p4a.bootstrap = sdl2
