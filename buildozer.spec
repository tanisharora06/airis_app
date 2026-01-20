[app]
android.sdk_path = /home/runner/android-sdk
title = AIRIS
package.name = airis
package.domain = org.airis
version = 0.1
version.code = 1

source.dir = .
source.include_exts = py,kv,tflite

requirements = python3,kivy,plyer,pillow,tflite-runtime

orientation = portrait

android.permissions = CAMERA,RECORD_AUDIO
p4a.bootstrap = sdl2
android.api = 33
android.minapi = 21
android.ndk = 25b
