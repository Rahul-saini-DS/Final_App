"""
Enhanced Linguistic Task: Tell a Story about a Kite (Age 5-6)
Advanced speech recognition with narrative analysis
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

class StoryKiteTask:
    def __init__(self):
        self.task_name = "story_kite"
        self.age_group = "5-6"
        self.title = "Tell a short story about a kite"
        self.description = "Tell me what happens with a kite"
        self.instruction = "Tell a story about flying a kite"
        self.icon = "🪁"
        
        # Story analysis keywords
        self.essential_words = ["kite"]  # Must have
        self.story_words = ["fly", "flying", "flies", "flew", "wind", "sky", "air", "high", "up"]
        self.action_words = ["run", "running", "pull", "hold", "catch", "string", "tail"]
        self.descriptive_words = ["colorful", "beautiful", "big", "small", "red", "blue", "yellow", "bright"]
        self.narrative_words = ["then", "next", "after", "first", "finally", "when", "because"]
        
        # Analysis parameters
        self.min_story_length = 5  # Minimum words for a story
        self.min_sentences = 2     # Minimum sentences
        self.confidence_threshold = 0.6
        
        # Tracking
        self.success_count = 0
        self.total_attempts = 0
        self.story_history = []
        
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
    
    def analyze_story_content(self, text):
        """
        Analyze story content for narrative elements and vocabulary
        """
        if not text or len(text.strip()) < 3:
            return {
                'has_essential': False,
                'word_count': 0,
                'sentence_count': 0,
                'vocabulary_score': 0.0,
                'narrative_score': 0.0,
                'overall_confidence': 0.0,
                'feedback_points': ['Story too short']
            }
        
        text_lower = text.lower().strip()
        words = text_lower.split()
        
        # Count sentences (rough estimation)
        sentence_count = max(1, len(re.findall(r'[.!?]+', text)))
        
        # Check for essential words
        has_kite = any(word in text_lower for word in ["kite", "kites"])
        
        # Count vocabulary categories
        story_word_count = sum(1 for word in self.story_words if word in text_lower)
        action_word_count = sum(1 for word in self.action_words if word in text_lower)
        descriptive_word_count = sum(1 for word in self.descriptive_words if word in text_lower)
        narrative_word_count = sum(1 for word in self.narrative_words if word in text_lower)
        
        # Calculate scores
        vocabulary_score = min(1.0, (story_word_count * 0.3 + action_word_count * 0.2 + 
                                   descriptive_word_count * 0.2 + narrative_word_count * 0.3))
        
        # Narrative structure score
        narrative_score = min(1.0, (sentence_count / self.min_sentences) * 0.5 + 
                             (len(words) / self.min_story_length) * 0.5)
        
        # Overall confidence
        essential_bonus = 0.4 if has_kite else 0.0
        overall_confidence = essential_bonus + vocabulary_score * 0.4 + narrative_score * 0.2
        overall_confidence = min(1.0, overall_confidence)
        
        # Generate feedback points
        feedback_points = []
        if not has_kite:
            feedback_points.append("Remember to mention the kite!")
        if len(words) < self.min_story_length:
            feedback_points.append("Try to make your story a bit longer")
        if sentence_count < self.min_sentences:
            feedback_points.append("Try to tell more about what happens")
        if story_word_count == 0:
            feedback_points.append("Tell me about flying the kite")
        if narrative_word_count == 0:
            feedback_points.append("Use words like 'then' or 'next' to connect your story")
        
        if not feedback_points:
            if overall_confidence >= 0.8:
                feedback_points.append("Excellent story with great details!")
            elif overall_confidence >= 0.6:
                feedback_points.append("Good story! You included nice details.")
            else:
                feedback_points.append("Nice start! Try adding more details.")
        
        return {
            'has_essential': has_kite,
            'word_count': len(words),
            'sentence_count': sentence_count,
            'vocabulary_score': vocabulary_score,
            'narrative_score': narrative_score,
            'overall_confidence': overall_confidence,
            'feedback_points': feedback_points,
            'story_words_used': story_word_count,
            'action_words_used': action_word_count,
            'descriptive_words_used': descriptive_word_count,
            'narrative_words_used': narrative_word_count
        }
    
    def process_audio(self, audio_data):
        """
        Process audio data and return story analysis results
        """
        if not VOSK_AVAILABLE or not self.model:
            return {
                'success': False,
                'confidence': 0.0,
                'transcript': '',
                'message': 'Speech recognition not available',
                'feedback': 'Voice recognition requires Vosk installation',
                'analysis': None,
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
                
                # Analyze the story
                analysis = self.analyze_story_content(transcript)
                
                # Track attempt
                self.total_attempts += 1
                success = analysis['overall_confidence'] >= self.confidence_threshold
                if success:
                    self.success_count += 1
                
                # Add to history
                self.story_history.append({
                    'timestamp': datetime.now(),
                    'transcript': transcript,
                    'analysis': analysis,
                    'success': success
                })
                
                # Generate response message
                if success:
                    if analysis['overall_confidence'] >= 0.9:
                        message = "What an amazing story! You're a wonderful storyteller!"
                        feedback = f"Perfect! {' '.join(analysis['feedback_points'])}"
                    elif analysis['overall_confidence'] >= 0.7:
                        message = "Great story! You told me about the kite beautifully!"
                        feedback = f"Excellent work! {' '.join(analysis['feedback_points'])}"
                    else:
                        message = "Good story! You included the kite and some details."
                        feedback = f"Nice job! {' '.join(analysis['feedback_points'])}"
                else:
                    if transcript:
                        message = f"I heard your story! {' '.join(analysis['feedback_points'][:2])}"
                        feedback = "Keep practicing storytelling - you're doing great!"
                    else:
                        message = "I couldn't hear your story clearly. Please try again!"
                        feedback = "Speak clearly and tell me a story about flying a kite."
                
                return {
                    'success': success,
                    'confidence': analysis['overall_confidence'],
                    'transcript': transcript,
                    'message': message,
                    'feedback': feedback,
                    'analysis': analysis,
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
                'analysis': None,
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
            'essential_words': self.essential_words,
            'story_words': self.story_words,
            'min_story_length': self.min_story_length,
            'confidence_threshold': self.confidence_threshold,
            'available': VOSK_AVAILABLE and self.model is not None,
            'model_path': self.model_path
        }
    
    def get_story_quality_feedback(self, analysis):
        """
        Generate detailed feedback about story quality
        """
        if not analysis:
            return "No story analysis available."
        
        feedback_parts = []
        
        # Word count feedback
        if analysis['word_count'] >= 20:
            feedback_parts.append("Your story was nice and long!")
        elif analysis['word_count'] >= 10:
            feedback_parts.append("Good story length!")
        else:
            feedback_parts.append("Try making your story a bit longer next time.")
        
        # Vocabulary feedback
        if analysis['vocabulary_score'] >= 0.7:
            feedback_parts.append("You used wonderful descriptive words!")
        elif analysis['vocabulary_score'] >= 0.4:
            feedback_parts.append("Nice use of story words!")
        
        # Narrative feedback
        if analysis['narrative_score'] >= 0.7:
            feedback_parts.append("Your story had great structure!")
        
        return " ".join(feedback_parts)
    
    def reset(self):
        """
        Reset task state for a new attempt
        """
        self.success_count = 0
        self.total_attempts = 0
        self.story_history = []
