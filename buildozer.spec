[app]

title = AIRIS

package.name = airis

package.domain = org.test

source.dir = .

source.include_exts = py,png,jpg,kv,atlas,tflite,txt


version = 0.1


requirements = kivy,speech-recognition,plyer,tflite-runtime,pillow,numpy

fullscreen = 0

android.permissions = CAMERA,RECORD_AUDIO,INTERNET

android.api = 31

android.minapi = 21
android.accept_sdk_license = True

android.archs = arm64-v8a, armeabi-v7a

android.allow_backup = True

android.enable_androidx = True
android.enable_androidx_recyclerview = True
