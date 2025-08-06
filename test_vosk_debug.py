#!/usr/bin/env python3
"""
Vosk Debugging Script

This script helps diagnose issues with Vosk speech recognition setup.
Run this to test your Vosk installation and identify problems.
"""

import os
import sys
import json

def test_vosk_installation():
    """Test if Vosk is properly installed and working"""
    print("🔍 Testing Vosk Installation")
    print("=" * 50)
    
    # Test 1: Import Vosk
    try:
        import vosk
        print("✅ Vosk import successful")
        vosk.SetLogLevel(-1)  # Reduce noise
    except ImportError as e:
        print(f"❌ Vosk import failed: {e}")
        print("💡 Solution: Install Vosk with: pip install vosk")
        return False
    
    # Test 2: Check model path
    model_path = os.path.join(os.path.dirname(__file__), 'StreamlitApp', 'tasks', 'vosk-model-small-en-us-0.15')
    model_path = os.path.abspath(model_path)
    
    print(f"🔍 Checking model path: {model_path}")
    
    if not os.path.exists(model_path):
        print("❌ Vosk model not found")
        print("💡 Solution: Run download_vosk_model.bat to download the model")
        
        # Check if download script exists
        download_script = os.path.join(os.path.dirname(__file__), 'download_vosk_model.bat')
        if os.path.exists(download_script):
            print(f"📁 Download script found at: {download_script}")
        else:
            print("❌ Download script not found")
            print("💡 Download manually from: https://alphacephei.com/vosk/models")
        return False
    else:
        print("✅ Vosk model found")
    
    # Test 3: Load model
    try:
        print("🔍 Loading Vosk model...")
        model = vosk.Model(model_path)
        print("✅ Vosk model loaded successfully")
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False
    
    # Test 4: Create recognizer
    try:
        print("🔍 Creating recognizer...")
        rec = vosk.KaldiRecognizer(model, 16000)
        print("✅ Recognizer created successfully")
    except Exception as e:
        print(f"❌ Recognizer creation failed: {e}")
        return False
    
    # Test 5: Test basic recognition (silent test)
    try:
        print("🔍 Testing recognition functionality...")
        # Create dummy audio data (silence)
        dummy_audio = b'\x00' * 3200  # 200ms of silence at 16kHz
        rec.AcceptWaveform(dummy_audio)
        result = rec.FinalResult()
        parsed_result = json.loads(result)
        print("✅ Recognition test successful")
    except Exception as e:
        print(f"❌ Recognition test failed: {e}")
        return False
    
    print("\n🎉 All Vosk tests passed!")
    return True

def test_audio_dependencies():
    """Test audio processing dependencies"""
    print("\n🔍 Testing Audio Dependencies")
    print("=" * 50)
    
    # Test wave module
    try:
        import wave
        print("✅ Wave module available")
    except ImportError:
        print("❌ Wave module not available")
        return False
    
    # Test FFmpeg
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg available")
        else:
            print("❌ FFmpeg not working properly")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("⚠️  FFmpeg not found (audio conversion may fail)")
        print("💡 Install FFmpeg from: https://ffmpeg.org/download.html")
    
    return True

def test_backend_connection():
    """Test backend API connection"""
    print("\n🔍 Testing Backend Connection")
    print("=" * 50)
    
    try:
        import requests
        
        # Test basic connection
        response = requests.get('http://localhost:5000/api/ai/test-camera', timeout=5)
        if response.status_code == 200:
            print("✅ Backend API accessible")
        else:
            print(f"⚠️  Backend API returned status {response.status_code}")
            
    except ImportError:
        print("⚠️  Requests module not available for testing")
    except requests.exceptions.ConnectionError:
        print("❌ Backend API not accessible")
        print("💡 Make sure the Flask backend is running on localhost:5000")
    except requests.exceptions.Timeout:
        print("❌ Backend API timeout")
    except Exception as e:
        print(f"❌ Backend test error: {e}")

def check_file_structure():
    """Check if all required files are in place"""
    print("\n🔍 Checking File Structure")
    print("=" * 50)
    
    required_files = [
        'new_backend/ai_assessment_routes.py',
        'new_backend/app.py',
        'new_frontend/src/components/ai/VoiceAssessment.tsx',
    ]
    
    optional_files = [
        'download_vosk_model.bat',
        'StreamlitApp/tasks/vosk-model-small-en-us-0.15/README',
    ]
    
    for file_path in required_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - REQUIRED FILE MISSING")
    
    for file_path in optional_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"⚠️  {file_path} - optional file missing")

def main():
    """Main debugging function"""
    print("🎤 Vosk Speech Recognition Debug Tool")
    print("=" * 60)
    
    all_good = True
    
    # Run all tests
    all_good &= test_vosk_installation()
    all_good &= test_audio_dependencies()
    check_file_structure()
    test_backend_connection()
    
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 All critical tests passed! Vosk should be working.")
        print("\n💡 If you're still having issues:")
        print("1. Check browser console for frontend errors")
        print("2. Check Flask backend logs for detailed error messages")
        print("3. Test with a short, clear word like 'hello'")
    else:
        print("❌ Some critical tests failed. Please fix the issues above.")
    
    print("\n📝 Debug Information:")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Script location: {os.path.dirname(__file__)}")

if __name__ == "__main__":
    main()
