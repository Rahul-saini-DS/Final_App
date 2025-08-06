@echo off
echo Installing FFmpeg for audio conversion...
echo.

REM Check if Chocolatey is installed
choco --version >nul 2>&1
if %errorlevel% == 0 (
    echo Chocolatey found, installing FFmpeg...
    choco install ffmpeg -y
    if %errorlevel% == 0 (
        echo FFmpeg installed successfully via Chocolatey!
        goto :success
    )
)

REM Check if winget is available (Windows 10/11)
winget --version >nul 2>&1
if %errorlevel% == 0 (
    echo Winget found, installing FFmpeg...
    winget install "FFmpeg (Essentials Build)"
    if %errorlevel% == 0 (
        echo FFmpeg installed successfully via Winget!
        goto :success
    )
)

echo.
echo ❌ Could not install FFmpeg automatically.
echo.
echo Please install FFmpeg manually:
echo 1. Download from: https://www.gyan.dev/ffmpeg/builds/
echo 2. Extract to a folder (e.g., C:\ffmpeg)
echo 3. Add C:\ffmpeg\bin to your system PATH
echo.
echo Alternative installations:
echo - Via Chocolatey: choco install ffmpeg
echo - Via Winget: winget install "FFmpeg (Essentials Build)"
echo.
pause
goto :end

:success
echo.
echo ✅ FFmpeg installation completed!
echo.
echo You may need to restart your command prompt or IDE
echo for the PATH changes to take effect.
echo.
pause

:end
