@echo off
echo 🎙️ Downloading Vosk Speech Recognition Model...

REM Create directory if it doesn't exist
if not exist "StreamlitApp\tasks\" mkdir "StreamlitApp\tasks\"

REM Download the Vosk model (small English model - about 40MB)
echo 📥 Downloading vosk-model-small-en-us-0.15.zip...
curl -L -o "vosk-model-small-en-us-0.15.zip" "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"

if %errorlevel% neq 0 (
    echo ❌ Download failed. Please check your internet connection.
    echo 🌐 Manual download: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    pause
    exit /b 1
)

echo 📦 Extracting model...
powershell -Command "Expand-Archive -Path 'vosk-model-small-en-us-0.15.zip' -DestinationPath 'StreamlitApp\tasks\' -Force"

if %errorlevel% neq 0 (
    echo ❌ Extraction failed.
    pause
    exit /b 1
)

REM Clean up zip file
del "vosk-model-small-en-us-0.15.zip"

echo ✅ Vosk model installed successfully!
echo 📁 Location: StreamlitApp\tasks\vosk-model-small-en-us-0.15\
echo 🎉 Speech recognition is now ready!

pause
