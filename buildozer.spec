[app]

# (str) Title of your application
title = 机械施工记账

# (str) Package name
package.name = mechbookkeeping

# (str) Package domain (needed for android/ios packaging)
package.domain = org.aisha

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,otf,json

# (str) Application versioning (method 1)
version = 3.0.0

# (list) Application requirements
requirements = python3,kivy==2.3.0,sqlite3,pyjnius,android,openpyxl,fpdf2

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Accept SDK license
android.accept_sdk_license = True

# (str) python-for-android branch or tag
p4a.branch = v2024.01.21

# (str) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme
android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Pattern to whitelist for the whole project
android.whitelist = []

# (str) The Android arch to build for
android.archs = arm64-v8a,armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) The format used to package the app for release mode (aab or apk)
android.release_artifact = apk

# (str) The format used to package the app for debug mode (apk)
android.debug_artifact = apk

# (int) Android logging level (0=disabled, 1=error, 2=warning, 3=info, 4=debug)
android.logging_level = 2

# (bool) If True, then ignore the src integrity check, useful if you want to use a local p4a
android.reduce_package = True

# (str) Add extra Java jars to the libs directory
# android.add_src =

# (str) Add extra AIDL files
# android.add_aidl =

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage
build_dir = ./.buildozer

# (str) Path to build output
bin_dir = ./bin

# (str) Additional arguments for pip install
pip_install_args = --break-system-packages
