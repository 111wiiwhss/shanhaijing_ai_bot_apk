[app]

# (str) Title of your application
title = 山海经异变AI代练

# (str) Package name
package.name = shanhaijing_ai_bot

# (str) Package domain (needed for android/ios packaging)
package.domain = com.shanhaijing

# (str) Source code where the main.py live
source.dir = ./kivy_app

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,txt,json

# (list) List of inclusions using pattern matching
#source.include_patterns = license,data/*

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec,md

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = venv,.git

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,data/audio/*.wav,data/images/original/*

# (str) Application versioning (method 1)
version = 1.0.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,numpy,opencv,pillow,pyyaml,requests,loguru

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# OSX Specific
#
#
# author = © Copyright Info

# change the major version of python used by the app
osx.python_version = 3

# Kivy version to use
osx.kivy_version = 1.9.1

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for android toolchain)
# Supported formats are: #RRGGBB #AARRGGBB or one of the following names:
# red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray, darkgray, grey,
# lightgrey, darkgrey, aqua, fuchsia, lime, maroon, navy, olive, purple, silver, teal.
android.presplash_color = #FFFFFF

# (string) Presplash animation using Lottie format.
# see https://lottiefiles.com/ for examples and https://airbnb.design/lottie/ for general documentation.
# Lottie files can be created using various tools, like Adobe After Effect or Synfig.
#android.presplash_lottie = %(source.dir)s/data/presplash.lottie

# (str) Adaptive icon of the application (used if Android API level is 26+ at runtime)
#icon.adaptive_foreground.filename = %(source.dir)s/data/icon_fg.png
#icon.adaptive_background.filename = %(source.dir)s/data/icon_bg.png

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,SYSTEM_ALERT_WINDOW

# (list) features (adds uses-feature -tags to manifest)
#android.features = android.hardware.usb.host

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25.1.8937393

# (int) Android NDK API to use. This is the minimum API your app will support, it should usually match android.minapi.
android.ndk_api = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path = 

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path = 

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path = 

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time when an update is due and you just want to test/build your package
#android.skip_update = False

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (str) Android entry point, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Android Activity
# use that parameter together with android.entrypoint to set custom Java class instead of PythonActivity
#android.activity_class_name = org.kivy.android.PythonActivity

# (str) Extra xml to write directly inside the <manifest> element of AndroidManifest.xml
# use that parameter to provide a filename from where to load your custom XML code
#android.extra_manifest_xml = ./src/android/extra_manifest.xml

# (str) Extra xml to write directly inside the <manifest><application> tag of AndroidManifest.xml
# use that parameter to provide a filename from where to load your custom XML arguments:
#android.extra_manifest_application_arguments = ./src/android/extra_manifest_application_arguments.xml

# (str) Full name including package path of the Java class that implements Python Service
# use that parameter to set custom Java class instead of PythonService
#android.service_class_name = org.kivy.android.PythonService

# (str) Android app theme, default is ok for Kivy-based app
# android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Android additional libraries to copy into libs/armeabi
#android.add_libs_armeabi = libs/android/*.so
#android.add_libs_armeabi_v7a = libs/android-v7/*.so
#android.add_libs_arm64_v8a = libs/android-v8/*.so
#android.add_libs_x86 = libs/android-x86/*.so
#android.add_libs_mips = libs/android-mips/*.so

# (bool) Indicate whether the screen should stay on
# Don't forget to add the WAKE_LOCK permission if you set this to True
android.wakelock = False

# (list) Android application meta-data to set (key=value format)
#android.meta_data = 

# (list) Android library project to add (will be added in the
# project.properties automatically.)
#android.library_references = 

# (list) Android shared libraries which will be added to AndroidManifest.xml using <uses-library> tag
#android.uses_library = 

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Android logcat only display log for activity's pid
android.logcat_pid_only = False

# (str) Android additional adb arguments
#android.adb_args = -H host.docker.internal

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = 1

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# In past, was `android.arch` as we weren't supporting builds for multiple archs at the same time.
android.archs = arm64-v8a, armeabi-v7a

# (int) overrides automatic versionCode computation (used in build.gradle)
# this is not the same as app version and should only be edited if you know what you're doing
# android.numeric_version = 1

# (bool) enables Android's bundle format for app distribution
# android.enable_aab = False

# (str) path to the certificate used for signing the debug APK
#android.debug_keystore_path = ~/.android/debug.keystore

# (str) password for the debug keystore
#android.debug_keystore_password = android

# (str) path to the certificate used for signing the release APK
#android.release_keystore_path = ~/.android/release.keystore

# (str) password for the release keystore
#android.release_keystore_password =

# (str) alias of the release key
#android.release_key_alias =

# (str) password for the release key
#android.release_key_password =

# (bool) attempts to use Google Play App Signing
# see https://developer.android.com/studio/publish/app-signing.html#app-signing-by-google-play
#android.play_app_signing = False

# (str) The package name for the play store
#android.play_store_package_name = com.example.myapp

# (str) The adb server to use (if specific port)
#android.adb_server_port = 5037

# (bool) If True, your app will be available to be installed from USB in debug mode
# android.install_mode = debug

# (list) List of APK alias to generate, usefull to build multiple APKs per arch
# android.apk_alias = debug,release

# (list) List of APK alias to exclude, usefull to exclude specific APKs
# android.apk_ignore_arch = x86

#
# Python for android (p4a) specific
#

# (str) python-for-android fork to use, defaults to upstream (kivy)
#p4a.fork = kivy

# (str) python-for-android branch to use, defaults to master
#p4a.branch = master

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
#p4a.source_dir = 

# (str) The directory in which python-for-android should look for your own build recipes (if any)
#p4a.local_recipes = 

# (str) Filename to the hook for p4a
#p4a.hook = 

# (str) Bootstrap to use for android builds
# p4a.bootstrap = sdl2

# (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask)
#p4a.port = 

# Control passing the --use-setup-py vs --ignore-setup-py to p4a
# "in the future" --use-setup-py is going to be the default behaviour in p4a, right now it is not
# Setting this to false will pass --ignore-setup-py, true will pass --use-setup-py
# NOTE: this is general setuptools integration, having pyproject.toml is enough, no need to generate setup.py
# p4a.setup_py = false

# (str) extra command line arguments to pass when invoking pythonforandroid.toolchain
#p4a.extra_args = 

#
# iOS specific
#

# (str) Path to a custom kivy-ios folder
#ios.kivy_ios_dir = ../kivy-ios
# Alternately, specify the URL and branch of a git checkout:
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master

# (int) Version of Python to use (2=2.7, 3=3.7)
ios.python_version = 3

# (int) The SDK version to use
#ios.sdk = 11.1

# (str) The name of the certificate to use for signing the debug version
# Get a list of available identities: buildozer ios list_identities
#ios.codesign.debug = "iPhone Developer: <lastname> <firstname> (<hexstring>)"

# (str) The name of the certificate to use for signing the release version
#ios.codesign.release = %(ios.codesign.debug)s

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa)
# bin_dir = ./bin

#    -----------------------------------------------------------------------------#    List as sections
#
# You can define all the "list" as [section:key].
# Each line will be considered as a option to the list.
# Let's take [app] / source.exclude_patterns.
# Instead of doing:
#
#source.exclude_patterns = license,data/audio/*.wav,data/images/original/*
#
# This can be translated into:
#
#[app:source.exclude_patterns]
#license
#data/audio/*.wav
data/images/original/*

#    -----------------------------------------------------------------------------#    Profiles
#
# You can extend section / key with a profile.
# For example, you want to deploy a demo version of your application without
# HD content. You could first change the title to add "[Demo]" in the name
# and extend the excluded directories to remove the HD content.
#
#[app@demo]
title = My Application Demo

#[app:source.exclude_patterns@demo]
data/images/hd/*

#    -----------------------------------------------------------------------------#    Variables
#
# You can set environment variables here. The environment variables will be
# available in the app section via %(var_name)s.
#
#[env]
#MY_VAR = my_value
