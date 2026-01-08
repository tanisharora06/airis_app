[app]
title = AIRIS
package.name = airis
package.domain = org.airis
version = 0.1
source.dir = .
source.include_exts = py
requirements = python3,kivy,plyer,pyjnius
orientation = portrait

android.permissions = CAMERA,RECORD_AUDIO
android.api = 33
android.minapi = 21

android.gradle_dependencies = org.tensorflow:tensorflow-lite:2.14.0
