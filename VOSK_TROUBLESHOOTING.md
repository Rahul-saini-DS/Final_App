# Vosk Speech Recognition Troubleshooting Guide

## Problem: Vosk gets stuck after 5 seconds

This issue typically occurs due to audio format conversion problems or missing dependencies. Here's how to fix it:

## Quick Fix Steps

### 1. Run the Debug Script
```bash
python test_vosk_debug.py
```

This will identify specific issues with your setup.

### 2. Install FFmpeg (Required for Audio Conversion)
Run the FFmpeg installer:
```bash
install_ffmpeg.bat
```

Or install manually:
- **Chocolatey**: `choco install ffmpeg`
- **Winget**: `winget install "FFmpeg (Essentials Build)"`
- **Manual**: Download from https://www.gyan.dev/ffmpeg/builds/

### 3. Verify Vosk Model
Make sure the Vosk model is downloaded:
```bash
download_vosk_model.bat
```

### 4. Check Dependencies
Ensure all required packages are installed:
```bash
cd new_backend
pip install -r requirements.txt
```

## Common Issues and Solutions

### Issue 1: "FFmpeg not found"
**Solution**: Install FFmpeg and add it to your PATH environment variable.

### Issue 2: "Audio must be mono (1 channel)"
**Solution**: The updated code now handles this automatically with proper audio conversion.

### Issue 3: "Vosk model not found"
**Solution**: Run `download_vosk_model.bat` to download the required model.

### Issue 4: Browser microphone permission denied
**Solution**: 
1. Allow microphone access in your browser
2. Use HTTPS or localhost (required for microphone access)
3. Check browser console for permission errors

### Issue 5: Audio processing timeout
**Solution**: The updated code includes:
- 30-second timeout for backend processing
- Better error handling and fallback methods
- Improved audio chunk processing

## Technical Details

### What Was Fixed

1. **Audio Format Conversion**: Added proper WebM to WAV conversion using FFmpeg
2. **Fallback Methods**: Added fallback audio conversion if FFmpeg is not available  
3. **Better Error Handling**: Added comprehensive error handling and logging
4. **Timeout Protection**: Added timeouts to prevent hanging
5. **Debug Information**: Added extensive logging for troubleshooting

### Updated Files

- `new_backend/ai_assessment_routes.py`: Improved audio conversion and error handling
- `new_frontend/src/components/ai/VoiceAssessment.tsx`: Better recording and processing
- `test_vosk_debug.py`: Debug script to identify issues
- `install_ffmpeg.bat`: Automatic FFmpeg installation

### Audio Processing Flow

1. **Frontend**: Records audio as WebM/Opus format
2. **Backend**: Receives base64-encoded audio
3. **Conversion**: Converts WebM to WAV format (16kHz, mono, 16-bit) using FFmpeg
4. **Processing**: Processes WAV audio with Vosk speech recognition
5. **Response**: Returns transcript and success status

## Testing Your Fix

### 1. Run Debug Script
```bash
python test_vosk_debug.py
```

### 2. Test in Browser
1. Open the assessment page
2. Try a linguistic task
3. Speak clearly into the microphone
4. Check browser console for any JavaScript errors
5. Check Flask backend console for detailed logs

### 3. Check Browser Console
Press F12 in your browser and look for:
- Microphone permission errors
- Audio recording errors
- Network request failures

### 4. Check Backend Logs
Look for detailed logs in your Flask backend console:
- Audio processing information
- FFmpeg conversion results
- Vosk model loading status

## Still Having Issues?

If the problem persists:

1. **Check microphone permissions** in your browser settings
2. **Try a different browser** (Chrome/Edge work best)
3. **Test with simple words** like "hello", "yes", "no"
4. **Check your audio setup** - test recording with other apps
5. **Review browser console errors** for additional clues

## Environment Requirements

- **Python 3.8+**
- **FFmpeg** (for audio conversion)
- **Modern browser** with microphone support
- **HTTPS or localhost** (required for microphone access)
- **Vosk model** (downloaded automatically by setup script)

## Advanced Debugging

### Enable Verbose Logging
Add this to your Flask app configuration:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Audio Format Manually
Use FFmpeg directly to test audio conversion:
```bash
ffmpeg -i input.webm -ar 16000 -ac 1 -sample_fmt s16 -f wav output.wav
```

### Check Vosk Model Integrity
Verify the model directory contains these files:
- `am/final.mdl`
- `graph/HCLG.fst`
- `graph/words.txt`
- `ivector/final.dubm`

With these fixes, your Vosk implementation should work without getting stuck after 5 seconds!
