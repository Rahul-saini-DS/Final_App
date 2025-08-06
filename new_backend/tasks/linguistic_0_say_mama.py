"""
Enhanced Linguistic Task: Say Mama (Age 0-1)
Advanced speech recognition with phonetic analysis
"""

import json
import tempfile
import os
import wave
from datetime import datetime
import re

# Try to import vosk, provide fallback if not available
try:
    import vosk
    VOSK_AVAILABLE = True
    vosk.SetLogLevel(-1)  # Reduce logging
except ImportError:
    VOSK_AVAILABLE = False
    print("WARNING: Vosk not available. Speech recognition will be disabled.")

class SayMamaTask:
    def __init__(self):
        self.task_name = "say_mama"
        self.age_group = "0-1"
        self.title = "Say 'ma‑ma'"
        self.description = "Can you say mama?"
        self.instruction = "Say 'mama' clearly"
        self.icon = "👶"
        
        # Target recognition
        self.target_words = ["ma", "mama", "mumma", "mummy", "mam", "mom"]
        self.phonetic_patterns = [
            r'\bm+a+m*a*\b',    # mama, maamaa, etc.
            r'\bm+u+m+\w*\b',   # mum, mumma, etc.
            r'\bm+o+m+\w*\b',   # mom, mommy, etc.
        ]
        
        # Detection parameters
        self.confidence_threshold = 0.6
        self.success_count = 0
        self.total_attempts = 0
        self.recognition_history = []
        
        # Vosk model setup
        self.model = None
        self.model_path = None
        self._setup_model()
    
    def _setup_model(self):
        """Setup Vosk model for speech recognition"""
        if not VOSK_AVAILABLE:
            return
        
        # Try different model paths with the correct nested path first
        possible_paths = [
            r'D:\born_genious\Final_App\new_backend\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15',
            r'D:\born_genious\Final_App\new_backend\vosk-model-small-en-us-0.15',
            os.path.join(os.path.dirname(__file__), '..', 'vosk-model-small-en-us-0.15', 'vosk-model-small-en-us-0.15'),
            os.path.join(os.path.dirname(__file__), '..', 'vosk-model-small-en-us-0.15'),
            os.path.join(os.path.dirname(__file__), '..', 'models', 'vosk-model-small-en-us-0.15'),
            os.path.join(os.path.dirname(__file__), '..', 'StreamlitApp', 'tasks', 'vosk-model-small-en-us-0.15'),
            os.path.join(os.getcwd(), 'models', 'vosk-model-small-en-us-0.15')
        ]
        
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                self.model_path = abs_path
                break
        
        if self.model_path:
            try:
                self.model = vosk.Model(self.model_path)
            except Exception as e:
                print(f"Error loading Vosk model: {e}")
                self.model = None
    
    def analyze_phonetics(self, text):
        """
        Analyze text for phonetic similarity to target words
        """
        if not text:
            return False, 0.0, []
        
        text_lower = text.lower().strip()
        matches = []
        max_confidence = 0.0
        
        # Direct word matching
        for target in self.target_words:
            if target in text_lower:
                matches.append(target)
                max_confidence = max(max_confidence, 1.0)
        
        # Phonetic pattern matching
        for pattern in self.phonetic_patterns:
            pattern_matches = re.findall(pattern, text_lower)
            if pattern_matches:
                matches.extend(pattern_matches)
                # Calculate confidence based on pattern quality
                for match in pattern_matches:
                    if 'ma' in match:
                        confidence = min(1.0, len(match) * 0.3)  # Longer matches get higher confidence
                        max_confidence = max(max_confidence, confidence)
        
        # Syllable analysis for baby speech
        syllables = re.findall(r'ma+|mu+|mo+', text_lower)
        if syllables:
            # Baby might say "ma ma" or "mama" - both are good
            if len(syllables) >= 1:
                matches.extend(syllables)
                max_confidence = max(max_confidence, 0.8)
        
        # Character-level analysis for unclear speech
        if 'm' in text_lower and 'a' in text_lower:
            matches.append("ma-sound")
            max_confidence = max(max_confidence, 0.5)
        
        return len(matches) > 0, max_confidence, matches
    
    def process_audio(self, audio_data):
        """
        Process audio data and return recognition results
        """
        if not VOSK_AVAILABLE or not self.model:
            return {
                'success': False,
                'confidence': 0.0,
                'transcript': '',
                'message': 'Speech recognition not available',
                'feedback': 'Voice recognition requires Vosk installation',
                'matches': [],
                'available': False
            }
        
        try:
            # Convert audio to WAV format if needed
            wav_bytes = self._convert_to_wav(audio_data)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                temp_audio.write(wav_bytes)
                temp_audio_path = temp_audio.name
            
            try:
                # Process with Vosk
                transcript = self._recognize_with_vosk(temp_audio_path)
                
                # Analyze the transcript
                has_match, confidence, matches = self.analyze_phonetics(transcript)
                
                # Track attempt
                self.total_attempts += 1
                if has_match:
                    self.success_count += 1
                
                # Add to history
                self.recognition_history.append({
                    'timestamp': datetime.now(),
                    'transcript': transcript,
                    'confidence': confidence,
                    'matches': matches,
                    'success': has_match
                })
                
                # Generate response
                if has_match and confidence >= self.confidence_threshold:
                    if confidence >= 0.9:
                        message = f"Perfect! I heard you say '{transcript}' - that's mama!"
                        feedback = "Excellent! You said mama very clearly!"
                    elif confidence >= 0.7:
                        message = f"Great job! I heard '{transcript}' - I can hear mama!"
                        feedback = "Good work! I can hear you trying to say mama!"
                    else:
                        message = f"Good try! I heard '{transcript}' - keep practicing mama!"
                        feedback = "Nice attempt! Try saying 'ma-ma' a bit more clearly."
                else:
                    if transcript:
                        message = f"I heard '{transcript}'. Try saying 'ma-ma'!"
                        feedback = "I can hear you talking! Now try saying 'mama' for me."
                    else:
                        message = "I couldn't hear anything clearly. Try saying 'mama'!"
                        feedback = "Speak a little louder and say 'ma-ma' for me!"
                
                return {
                    'success': has_match and confidence >= self.confidence_threshold,
                    'confidence': confidence,
                    'transcript': transcript,
                    'message': message,
                    'feedback': feedback,
                    'matches': matches,
                    'target_words': self.target_words,
                    'success_count': self.success_count,
                    'total_attempts': self.total_attempts,
                    'available': True
                }
                
            finally:
                # Clean up temp file
                try:
                    if os.path.exists(temp_audio_path):
                        os.unlink(temp_audio_path)
                except Exception:
                    pass
                    
        except Exception as e:
            return {
                'success': False,
                'confidence': 0.0,
                'transcript': '',
                'message': f'Speech processing error: {str(e)}',
                'feedback': 'There was a problem processing your voice. Please try again.',
                'matches': [],
                'available': False
            }
    
    def _convert_to_wav(self, audio_data):
        """
        Convert audio data to WAV format
        """
        # For now, assume audio_data is already in the correct format
        # In a real implementation, you'd use pydub or similar to convert
        if isinstance(audio_data, str):
            # If it's base64 encoded
            import base64
            return base64.b64decode(audio_data)
        return audio_data
    
    def _recognize_with_vosk(self, wav_path):
        """
        Use Vosk to recognize speech from WAV file
        """
        try:
            with wave.open(wav_path, 'rb') as wf:
                # Validate audio format
                if wf.getnchannels() != 1:
                    raise ValueError("Audio must be mono")
                if wf.getsampwidth() != 2:
                    raise ValueError("Audio must be 16-bit")
                
                # Create recognizer
                rec = vosk.KaldiRecognizer(self.model, wf.getframerate())
                
                # Process audio
                transcript_parts = []
                
                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text = result.get('text', '').strip()
                        if text:
                            transcript_parts.append(text)
                
                # Get final result
                final_result = json.loads(rec.FinalResult())
                final_text = final_result.get('text', '').strip()
                if final_text:
                    transcript_parts.append(final_text)
                
                return ' '.join(transcript_parts).strip()
                
        except Exception as e:
            print(f"Vosk recognition error: {e}")
            return ""
    
    def get_task_info(self):
        """
        Return task configuration information
        """
        return {
            'task_name': self.task_name,
            'age_group': self.age_group,
            'title': self.title,
            'description': self.description,
            'instruction': self.instruction,
            'icon': self.icon,
            'type': 'speech_recognition',
            'target_words': self.target_words,
            'confidence_threshold': self.confidence_threshold,
            'available': VOSK_AVAILABLE and self.model is not None,
            'model_path': self.model_path
        }
    
    def get_progress_summary(self):
        """
        Get a summary of recognition progress
        """
        if not self.recognition_history:
            return {
                'total_attempts': 0,
                'successful_attempts': 0,
                'success_rate': 0.0,
                'best_confidence': 0.0,
                'recent_transcripts': []
            }
        
        successful = [h for h in self.recognition_history if h['success']]
        recent_transcripts = [h['transcript'] for h in self.recognition_history[-5:] if h['transcript']]
        
        return {
            'total_attempts': len(self.recognition_history),
            'successful_attempts': len(successful),
            'success_rate': len(successful) / len(self.recognition_history) * 100,
            'best_confidence': max(h['confidence'] for h in self.recognition_history),
            'recent_transcripts': recent_transcripts
        }
    
    def reset(self):
        """
        Reset task state for a new attempt
        """
        self.success_count = 0
        self.total_attempts = 0
        self.recognition_history = []
