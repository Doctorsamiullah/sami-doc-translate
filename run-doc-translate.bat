@echo off
title DocTranslate Android Launcher
echo ==============================================
echo   DocTranslate - Android Launcher
echo ==============================================
echo Ensuring device is ready...
"C:\Users\docto\AppData\Local\Android\Sdk\platform-tools\adb.exe" wait-for-device
echo Launching DocTranslate MainActivity...
"C:\Users\docto\AppData\Local\Android\Sdk\platform-tools\adb.exe" shell am start -n com.doctranslate.app/.MainActivity
echo Done! DocTranslate is running on your Android device.
timeout /t 3 >nul
