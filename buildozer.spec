[app]
title = AIRIS
package.name = airis
package.domain = org.airis
version = 0.1

source.dir = .
source.include_exts = py

requirements = python3,kivy,plyer,pillow,tflite-runtime

orientation = portrait

android.api = 33
android.minapi = 21
android.ndk = 25b

p4a.bootstrap = sdl2

android.permissions = CAMERA,RECORD_AUDIO

android.sdk_path = /home/runner/android-sdk

android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a

log_level = 2
