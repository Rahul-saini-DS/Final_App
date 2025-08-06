from flask import Blueprint, request, jsonify
import json
import base64
import cv2
import numpy as np
import mediapipe as mp
import os
import wave
import tempfile
import logging
import io
from pydub import AudioSegment
import struct

# Import enhanced task manager
try:
    from tasks import get_task_manager
    ENHANCED_TASKS_AVAILABLE = True
    print("✅ Enhanced task system loaded successfully")
except ImportError as e:
    ENHANCED_TASKS_AVAILABLE = False
    print(f"⚠️  Enhanced tasks not available: {e}")

# Suppress MediaPipe warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
logging.getLogger('mediapipe').setLevel(logging.ERROR)

# Try to import vosk, provide fallback if not available
try:
    import vosk
    VOSK_AVAILABLE = True
    # Set log level for Vosk to reduce noise
    vosk.SetLogLevel(-1)
except ImportError:
    VOSK_AVAILABLE = False
    print("WARNING: Vosk not available. Speech recognition will be disabled.")

assessment_ai_bp = Blueprint('assessment_ai', __name__)

# MediaPipe setup with optimized settings
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
POSE_LMS = mp_pose.PoseLandmark

class ImprovedPoseDetector:
    def __init__(self):
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,  # Use lighter model for better performance
            enable_segmentation=False,  # Disable segmentation for speed
            min_detection_confidence=0.6,  # Lowered for better detection
            min_tracking_confidence=0.5
        )
        self.previous_landmarks = None
    
    def get_landmarks(self, frame):
        """Get pose landmarks with error handling"""
        try:
            # Ensure frame is valid
            if frame is None or frame.size == 0:
                return None
            
            # Convert BGR to RGB
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame
            results = self.pose.process(rgb)
            
            # Store for comparison
            if results.pose_landmarks:
                self.previous_landmarks = results.pose_landmarks
            
            return results.pose_landmarks
            
        except Exception as e:
            print(f"Pose detection error: {e}")
            return None

# Global pose detector instance
pose_detector = ImprovedPoseDetector()

def wrists_above_head(landmarks):
    """Check if both wrists are above the head with improved logic"""
    try:
        if not landmarks:
            return False
        
        # Get landmark positions
        nose = landmarks.landmark[POSE_LMS.NOSE]
        left_wrist = landmarks.landmark[POSE_LMS.LEFT_WRIST]
        right_wrist = landmarks.landmark[POSE_LMS.RIGHT_WRIST]
        
        # Check visibility (confidence)
        if (left_wrist.visibility < 0.5 or right_wrist.visibility < 0.5 or
            nose.visibility < 0.5):
            return False
        
        # Both wrists should be above nose level
        threshold = 0.05  # Small buffer for noise
        return (left_wrist.y < (nose.y - threshold) and 
                right_wrist.y < (nose.y - threshold))
                
    except Exception as e:
        print(f"Wrist detection error: {e}")
        return False

def one_leg_balance(landmarks):
    """Check if one leg is raised (balance pose) with improved detection"""
    try:
        if not landmarks:
            return False
        
        # Get key points
        left_knee = landmarks.landmark[POSE_LMS.LEFT_KNEE]
        right_knee = landmarks.landmark[POSE_LMS.RIGHT_KNEE]
        left_hip = landmarks.landmark[POSE_LMS.LEFT_HIP]
        right_hip = landmarks.landmark[POSE_LMS.RIGHT_HIP]
        left_ankle = landmarks.landmark[POSE_LMS.LEFT_ANKLE]
        right_ankle = landmarks.landmark[POSE_LMS.RIGHT_ANKLE]
        
        # Check visibility
        landmarks_to_check = [left_knee, right_knee, left_hip, right_hip, left_ankle, right_ankle]
        if any(lm.visibility < 0.5 for lm in landmarks_to_check):
            return False
        
        # Calculate if one leg is significantly raised
        left_leg_raised = (left_knee.y < (left_hip.y - 0.08) and 
                          left_ankle.y < (left_hip.y - 0.1))
        right_leg_raised = (right_knee.y < (right_hip.y - 0.08) and 
                           right_ankle.y < (right_hip.y - 0.1))
        
        return left_leg_raised or right_leg_raised
        
    except Exception as e:
        print(f"Balance detection error: {e}")
        return False

def detect_jump(landmarks):
    """Simplified jump detection based on hip position"""
    try:
        if not landmarks:
            return False
            
        left_hip = landmarks.landmark[POSE_LMS.LEFT_HIP]
        right_hip = landmarks.landmark[POSE_LMS.RIGHT_HIP]
        
        if left_hip.visibility < 0.5 or right_hip.visibility < 0.5:
            return False
        
        # Check if hips are high (indicating a jump)
        avg_hip_y = (left_hip.y + right_hip.y) / 2
        return avg_hip_y < 0.4  # Threshold for jump detection
        
    except Exception as e:
        print(f"Jump detection error: {e}")
        return False

def decode_base64_frame(frame_data):
    """Safely decode base64 frame data"""
    try:
        # Handle data URL format
        if ',' in frame_data:
            header, data = frame_data.split(',', 1)
        else:
            data = frame_data
        
        # Decode base64
        frame_bytes = base64.b64decode(data)
        
        # Convert to numpy array
        nparr = np.frombuffer(frame_bytes, np.uint8)
        
        # Decode image
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise ValueError("Failed to decode image")
        
        return frame
        
    except Exception as e:
        raise ValueError(f"Frame decode error: {str(e)}")

def convert_audio_to_wav(audio_data):
    """Convert audio data to proper WAV format for Vosk with improved error handling"""
    try:
        # Decode base64 audio
        if ',' in audio_data:
            header, data = audio_data.split(',', 1)
        else:
            data = audio_data
        
        audio_bytes = base64.b64decode(data)
        
        # Check if it's already a proper WAV file
        if audio_bytes.startswith(b'RIFF') and b'WAVE' in audio_bytes[:20]:
            # Validate WAV header
            try:
                wav_io = io.BytesIO(audio_bytes)
                with wave.open(wav_io, 'rb') as wf:
                    channels = wf.getnchannels()
                    sample_width = wf.getsampwidth()
                    frame_rate = wf.getframerate()
                    
                    # If already in correct format, return as-is
                    if channels == 1 and sample_width == 2 and frame_rate == 16000:
                        return audio_bytes
            except wave.Error:
                pass  # Continue to conversion
        
        # Try to load with pydub for format conversion
        try:
            # Load audio with pydub
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            
            # Convert to mono, 16kHz, 16-bit
            audio = audio.set_channels(1)  # Mono
            audio = audio.set_frame_rate(16000)  # 16kHz
            audio = audio.set_sample_width(2)  # 16-bit
            
            # Export to WAV bytes
            wav_buffer = io.BytesIO()
            audio.export(wav_buffer, format="wav")
            wav_bytes = wav_buffer.getvalue()
            
            return wav_bytes
            
        except Exception as pydub_error:
            print(f"Pydub conversion failed: {pydub_error}")
            
            # Advanced fallback: Try to create a simple WAV manually if it's raw PCM
            try:
                # Assume raw 16-bit PCM at 16kHz mono
                return create_wav_header(audio_bytes, 16000, 1, 2) + audio_bytes
            except Exception:
                # Last fallback: assume it's already WAV format
                return audio_bytes
            
    except Exception as e:
        raise ValueError(f"Audio conversion error: {str(e)}")

def create_wav_header(pcm_data, sample_rate=16000, channels=1, bits_per_sample=16):
    """Create a WAV header for raw PCM data"""
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    data_size = len(pcm_data)
    file_size = data_size + 36
    
    header = struct.pack('<4sI4s4sIHHIIHH4sI',
        b'RIFF', file_size, b'WAVE', b'fmt ',
        16, 1, channels, sample_rate, byte_rate, block_align, bits_per_sample,
        b'data', data_size
    )
    return header

@assessment_ai_bp.route('/api/ai/physical-assessment', methods=['POST'])
def physical_assessment():
    """Enhanced physical assessment using individual task modules"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        task_type = data.get('task_type')
        frame_data = data.get('frame')
        age_group = data.get('age_group', '1-2')  # Default age group
        
        if not frame_data:
            return jsonify({'error': 'No frame data provided'}), 400
        
        if not task_type:
            return jsonify({'error': 'No task type provided'}), 400
        
        # Try enhanced task system first
        if ENHANCED_TASKS_AVAILABLE:
            try:
                task_manager = get_task_manager()
                result = task_manager.process_physical_frame(age_group, frame_data)
                
                if not result.get('fallback', False):
                    # Enhanced processing successful
                    return jsonify({
                        'success': result.get('detected', False),
                        'message': result.get('message', 'Processing...'),
                        'feedback': result.get('feedback', ''),
                        'confidence': result.get('confidence', 0.0),
                        'enhanced': True,
                        'task_name': result.get('task_name', task_type),
                        'age_group': age_group,
                        'success_count': result.get('success_count', 0),
                        'detection_duration': result.get('detection_duration', 0),
                        'balanced_leg': result.get('balanced_leg'),
                        'jump_state': result.get('jump_state'),
                        'additional_data': {
                            k: v for k, v in result.items() 
                            if k not in ['detected', 'message', 'feedback', 'confidence']
                        }
                    })
            except Exception as e:
                print(f"Enhanced physical assessment error: {e}")
                # Fall back to basic assessment
        
        # Fallback to basic physical assessment
        try:
            frame = decode_base64_frame(frame_data)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        # Get pose landmarks using basic detector
        landmarks = pose_detector.get_landmarks(frame)
        
        success = False
        message = "No pose detected"
        confidence = 0.0
        
        if landmarks:
            # Calculate average confidence
            confidence = sum(lm.visibility for lm in landmarks.landmark) / len(landmarks.landmark)
            
            if task_type == 'raise_hands':
                success = wrists_above_head(landmarks)
                message = "Great! Both hands above head!" if success else "Raise both hands above your head"
                
            elif task_type == 'one_leg':
                success = one_leg_balance(landmarks)
                message = "Perfect balance!" if success else "Try standing on one leg"
                
            elif task_type == 'turn_around':
                # For turning, check if pose is detected (simplified)
                success = confidence > 0.6
                message = "Good turning motion!" if success else "Keep turning around"
                
            elif task_type == 'stand_still':
                # Check if pose is stable (simplified)
                success = confidence > 0.7
                message = "Standing very still!" if success else "Try to stand still"
                
            elif task_type in ['frog_jump', 'kangaroo_jump']:
                success = detect_jump(landmarks)
                message = "Nice jump!" if success else "Try jumping higher"
        
        return jsonify({
            'success': success,
            'message': message,
            'feedback': message,  # Use message as feedback for basic mode
            'landmarks_detected': landmarks is not None,
            'confidence': round(confidence, 2),
            'enhanced': False,
            'task_type': task_type,
            'age_group': age_group
        })
        
    except Exception as e:
        print(f"Physical assessment error: {e}")
        return jsonify({'error': f'Physical assessment error: {str(e)}'}), 500

@assessment_ai_bp.route('/api/ai/speech-assessment', methods=['POST'])
def speech_assessment():
    """Enhanced speech assessment using individual linguistic task modules"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        audio_data = data.get('audio')
        target_words = data.get('target_words', [])
        task_type = data.get('task_type')
        age_group = data.get('age_group', '1-2')  # Default age group
        
        if not audio_data:
            return jsonify({'error': 'No audio data provided'}), 400
        
        # Try enhanced task system first
        if ENHANCED_TASKS_AVAILABLE:
            try:
                task_manager = get_task_manager()
                result = task_manager.process_linguistic_audio(age_group, audio_data)
                
                if not result.get('fallback', False):
                    # Enhanced processing successful
                    return jsonify({
                        'success': result.get('success', False),
                        'transcript': result.get('transcript', ''),
                        'message': result.get('message', 'Processing...'),
                        'feedback': result.get('feedback', ''),
                        'confidence': result.get('confidence', 0.0),
                        'target_words': result.get('target_words', target_words),
                        'matched_words': result.get('matches', []),
                        'enhanced': True,
                        'task_name': result.get('task_name', task_type),
                        'age_group': age_group,
                        'success_count': result.get('success_count', 0),
                        'total_attempts': result.get('total_attempts', 0),
                        'analysis': result.get('analysis'),
                        'available': result.get('available', True)
                    })
            except Exception as e:
                print(f"Enhanced speech assessment error: {e}")
                # Fall back to basic assessment
        
        # Fallback to basic speech assessment
        if not VOSK_AVAILABLE:
            return jsonify({'error': 'Speech recognition not available - Vosk not installed'}), 500
        
        # Convert audio to proper format
        try:
            wav_bytes = convert_audio_to_wav(audio_data)
        except ValueError as e:
            return jsonify({
                'error': f'Audio format error: {str(e)}',
                'suggestion': 'Please ensure audio is in a supported format (WAV, MP3, etc.)',
                'success': False
            }), 400
        except Exception as e:
            return jsonify({
                'error': f'Audio conversion failed: {str(e)}',
                'suggestion': 'Audio processing issue - may be related to FFmpeg installation',
                'success': False
            }), 500
        
        # Save to temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            temp_audio.write(wav_bytes)
            temp_audio_path = temp_audio.name
        
        try:
            # Load Vosk model - using nested directory structure
            model_path = r'D:\born_genious\Final_App\new_backend\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15'
            
            if not os.path.exists(model_path):
                # Try alternative paths
                alt_paths = [
                    r'D:\born_genious\Final_App\new_backend\vosk-model-small-en-us-0.15',
                    os.path.join(os.path.dirname(__file__), 'vosk-model-small-en-us-0.15', 'vosk-model-small-en-us-0.15'),
                    os.path.join(os.path.dirname(__file__), 'vosk-model-small-en-us-0.15')
                ]
                
                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        model_path = alt_path
                        break
                else:
                    return jsonify({
                        'error': 'Vosk model not found. Please ensure model is at the correct path.',
                        'expected_path': model_path,
                        'download_needed': True
                    }), 500
            
            # Initialize model and recognizer
            model = vosk.Model(model_path)
            
            # Open and validate audio file
            try:
                with wave.open(temp_audio_path, 'rb') as wf:
                    channels = wf.getnchannels()
                    sample_width = wf.getsampwidth()
                    frame_rate = wf.getframerate()
                    
                    print(f"Audio info: channels={channels}, width={sample_width}, rate={frame_rate}")
                    
                    if channels != 1:
                        return jsonify({
                            'error': f'Audio must be mono (1 channel), got {channels}',
                            'success': False,
                            'audio_info': {'channels': channels, 'width': sample_width, 'rate': frame_rate}
                        }), 400
                    if sample_width != 2:
                        return jsonify({
                            'error': f'Audio must be 16-bit (2 bytes), got {sample_width}',
                            'success': False,
                            'audio_info': {'channels': channels, 'width': sample_width, 'rate': frame_rate}
                        }), 400
                    
                    # Create recognizer with correct sample rate
                    rec = vosk.KaldiRecognizer(model, frame_rate)
                    
                    # Process audio in chunks
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
                    
                    # Combine all transcript parts
                    transcript = ' '.join(transcript_parts).strip().lower()
                    
            except wave.Error as wave_error:
                return jsonify({
                    'error': f'Invalid WAV file: {str(wave_error)}',
                    'success': False,
                    'suggestion': 'Audio file may be corrupt or in wrong format'
                }), 400
            except Exception as processing_error:
                return jsonify({
                    'error': f'Audio processing failed: {str(processing_error)}',
                    'success': False,
                    'suggestion': 'Speech recognition processing error'
                }), 500
            
            # Check if transcript contains target words
            success = False
            matched_words = []
            
            if transcript:
                for word in target_words:
                    if word.lower() in transcript:
                        success = True
                        matched_words.append(word)
            
            # Generate appropriate message
            if success:
                message = f"Great job! I heard: '{transcript}'"
            elif transcript:
                message = f"I heard: '{transcript}'. Try saying: {', '.join(target_words)}"
            else:
                message = f"I couldn't hear anything clearly. Try saying: {', '.join(target_words)}"
            
            return jsonify({
                'success': success,
                'transcript': transcript,
                'message': message,
                'feedback': message,  # Use message as feedback for basic mode
                'target_words': target_words,
                'matched_words': matched_words,
                'task_type': task_type,
                'enhanced': False,
                'age_group': age_group
            })
            
        finally:
            # Clean up temporary file
            try:
                if 'temp_audio_path' in locals() and os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)
            except Exception as cleanup_error:
                print(f"Cleanup error: {cleanup_error}")
        
    except Exception as e:
        print(f"Speech assessment error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Speech assessment error: {str(e)}',
            'success': False,
            'message': 'Sorry, speech recognition failed. Please try again.',
            'suggestion': 'Check audio input and ensure microphone is working'
        }), 500

@assessment_ai_bp.route('/api/ai/enhanced-tasks', methods=['GET'])
def get_enhanced_tasks():
    """Get information about available enhanced tasks"""
    try:
        if not ENHANCED_TASKS_AVAILABLE:
            return jsonify({
                'available': False,
                'message': 'Enhanced task system not available',
                'tasks': {
                    'physical_tasks': {},
                    'linguistic_tasks': {},
                    'total_physical': 0,
                    'total_linguistic': 0
                }
            })
        
        task_manager = get_task_manager()
        tasks_summary = task_manager.get_all_available_tasks()
        
        return jsonify({
            'available': True,
            'message': 'Enhanced task system loaded successfully',
            'tasks': tasks_summary
        })
        
    except Exception as e:
        return jsonify({
            'available': False,
            'error': str(e),
            'message': 'Error loading enhanced task system'
        })

@assessment_ai_bp.route('/api/ai/task-progress/<age_group>/<task_type>', methods=['GET'])
def get_task_progress(age_group, task_type):
    """Get progress information for a specific task"""
    try:
        if not ENHANCED_TASKS_AVAILABLE:
            return jsonify({'error': 'Enhanced task system not available'}), 400
        
        task_manager = get_task_manager()
        progress = task_manager.get_task_progress(age_group, task_type)
        
        if progress:
            return jsonify(progress)
        else:
            return jsonify({'error': f'No progress data for {task_type} task in age group {age_group}'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Progress retrieval error: {str(e)}'}), 500

@assessment_ai_bp.route('/api/ai/reset-task/<age_group>/<task_type>', methods=['POST'])
def reset_task(age_group, task_type):
    """Reset a specific task for a new attempt"""
    try:
        if not ENHANCED_TASKS_AVAILABLE:
            return jsonify({'error': 'Enhanced task system not available'}), 400
        
        task_manager = get_task_manager()
        success = task_manager.reset_task(age_group, task_type)
        
        if success:
            return jsonify({'message': f'Task {task_type} for age group {age_group} reset successfully'})
        else:
            return jsonify({'error': f'Failed to reset {task_type} task for age group {age_group}'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Task reset error: {str(e)}'}), 500

@assessment_ai_bp.route('/api/ai/test-camera', methods=['GET'])
def test_camera():
    """Test endpoint to verify camera and MediaPipe functionality"""
    try:
        # Test camera access
        cap = cv2.VideoCapture(0)
        camera_ok = cap.isOpened()
        
        frame_info = None
        pose_ok = False
        
        if camera_ok:
            ret, frame = cap.read()
            if ret:
                frame_info = {
                    'shape': frame.shape,
                    'dtype': str(frame.dtype)
                }
                
                # Test pose detection
                landmarks = pose_detector.get_landmarks(frame)
                pose_ok = landmarks is not None
            
            cap.release()
        
        return jsonify({
            'camera_available': camera_ok,
            'frame_info': frame_info,
            'pose_detection_working': pose_ok,
            'mediapipe_ready': True
        })
        
    except Exception as e:
        return jsonify({
            'camera_available': False,
            'error': str(e),
            'mediapipe_ready': False
        })

@assessment_ai_bp.route('/api/ai/test-microphone', methods=['GET'])
def test_microphone():
    """Test endpoint to verify microphone and Vosk functionality"""
    model_path = r'D:\born_genious\Final_App\new_backend\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15'
    
    # Try alternative paths if not found
    if not os.path.exists(model_path):
        alt_paths = [
            r'D:\born_genious\Final_App\new_backend\vosk-model-small-en-us-0.15',
            os.path.join(os.path.dirname(__file__), 'vosk-model-small-en-us-0.15', 'vosk-model-small-en-us-0.15'),
            os.path.join(os.path.dirname(__file__), 'vosk-model-small-en-us-0.15')
        ]
        
        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                model_path = alt_path
                break
    
    model_exists = os.path.exists(model_path)
    
    vosk_model_ok = False
    if VOSK_AVAILABLE and model_exists:
        try:
            model = vosk.Model(model_path)
            rec = vosk.KaldiRecognizer(model, 16000)
            vosk_model_ok = True
        except Exception as e:
            print(f"Vosk model test failed: {e}")
    
    return jsonify({
        'message': 'Microphone test endpoint ready',
        'vosk_available': VOSK_AVAILABLE,
        'model_exists': model_exists,
        'model_path': model_path,
        'vosk_model_ok': vosk_model_ok,
        'speech_ready': VOSK_AVAILABLE and model_exists and vosk_model_ok
    })

@assessment_ai_bp.route('/api/ai/download-model-status', methods=['GET'])
def download_model_status():
    """Check if Vosk model needs to be downloaded"""
    model_path = os.path.join(os.path.dirname(__file__), '..', 'StreamlitApp', 'tasks', 'vosk-model-small-en-us-0.15')
    model_path = os.path.abspath(model_path)
    model_exists = os.path.exists(model_path)
    
    return jsonify({
        'model_exists': model_exists,
        'model_path': model_path,
        'vosk_available': VOSK_AVAILABLE,
        'speech_ready': VOSK_AVAILABLE and model_exists,
        'download_script': 'download_vosk_model.bat'
    })
