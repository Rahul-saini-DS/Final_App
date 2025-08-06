"""
Enhanced Physical Task: Frog Jump (Age 4-5)
Detects jumping movements with squat preparation
"""

import cv2
import numpy as np
import mediapipe as mp
from datetime import datetime
import math

# MediaPipe setup
try:
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    POSE_LMS = mp_pose.PoseLandmark
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("WARNING: MediaPipe not available for physical assessments")

class FrogJumpTask:
    def __init__(self):
        self.task_name = "frog_jump"
        self.age_group = "4-5"
        self.title = "Can you do a frog jump?"
        self.description = "Jump like a frog!"
        self.instruction = "Squat down low, then jump forward like a frog"
        self.icon = "🐸"
        
        # Detection parameters
        self.confidence_threshold = 0.7
        self.success_count = 0
        self.total_attempts = 0
        self.jump_state = "waiting"  # waiting, squatting, jumping, landed
        self.state_start_time = None
        
        # Jump detection parameters
        self.squat_threshold = 0.3  # How low hips need to be for squatting
        self.jump_threshold = 0.2   # How high hips need to be for jumping
        self.min_squat_time = 0.5   # Minimum time in squat position
        self.jump_timeout = 2.0     # Max time to complete jump after squat
        
        # State tracking
        self.baseline_hip_y = None
        self.squat_detected = False
        self.jump_detected = False
        
        # Pose detector
        if MEDIAPIPE_AVAILABLE:
            self.pose = mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                enable_segmentation=False,
                min_detection_confidence=0.6,
                min_tracking_confidence=0.5
            )
        else:
            self.pose = None
    
    def analyze_body_position(self, landmarks):
        """
        Analyze body position to detect squat and jump phases
        """
        if not landmarks or not MEDIAPIPE_AVAILABLE:
            return None
        
        try:
            # Get key landmarks
            left_hip = landmarks.landmark[POSE_LMS.LEFT_HIP]
            right_hip = landmarks.landmark[POSE_LMS.RIGHT_HIP]
            left_knee = landmarks.landmark[POSE_LMS.LEFT_KNEE]
            right_knee = landmarks.landmark[POSE_LMS.RIGHT_KNEE]
            left_ankle = landmarks.landmark[POSE_LMS.LEFT_ANKLE]
            right_ankle = landmarks.landmark[POSE_LMS.RIGHT_ANKLE]
            left_shoulder = landmarks.landmark[POSE_LMS.LEFT_SHOULDER]
            right_shoulder = landmarks.landmark[POSE_LMS.RIGHT_SHOULDER]
            
            # Check visibility
            required_landmarks = [left_hip, right_hip, left_knee, right_knee, 
                                left_ankle, right_ankle, left_shoulder, right_shoulder]
            if any(lm.visibility < 0.5 for lm in required_landmarks):
                return None
            
            # Calculate average positions
            avg_hip_y = (left_hip.y + right_hip.y) / 2
            avg_knee_y = (left_knee.y + right_knee.y) / 2
            avg_ankle_y = (left_ankle.y + right_ankle.y) / 2
            avg_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
            
            # Calculate body ratios for position analysis
            torso_length = avg_hip_y - avg_shoulder_y
            thigh_length = avg_knee_y - avg_hip_y
            shin_length = avg_ankle_y - avg_knee_y
            
            # Detect squatting (hips low, knees bent)
            hip_knee_ratio = (avg_knee_y - avg_hip_y) / torso_length if torso_length > 0 else 0
            knee_ankle_ratio = (avg_ankle_y - avg_knee_y) / torso_length if torso_length > 0 else 0
            
            # Initialize baseline if not set
            if self.baseline_hip_y is None:
                self.baseline_hip_y = avg_hip_y
            
            # Calculate relative hip position
            hip_movement = self.baseline_hip_y - avg_hip_y  # Positive = higher than baseline
            
            return {
                'avg_hip_y': avg_hip_y,
                'avg_knee_y': avg_knee_y,
                'avg_ankle_y': avg_ankle_y,
                'hip_movement': hip_movement,
                'hip_knee_ratio': hip_knee_ratio,
                'knee_ankle_ratio': knee_ankle_ratio,
                'is_squatting': hip_movement < -self.squat_threshold,  # Hips below baseline
                'is_jumping': hip_movement > self.jump_threshold,      # Hips above baseline
                'knee_bend': avg_knee_y > avg_hip_y + 0.1  # Knees below hips indicates bend
            }
            
        except Exception as e:
            print(f"Body position analysis error: {e}")
            return None
    
    def update_jump_state(self, body_analysis, current_time):
        """
        Update the jump state machine based on body analysis
        """
        if not body_analysis:
            return "error", "Cannot analyze body position"
        
        state_duration = (current_time - self.state_start_time).total_seconds() if self.state_start_time else 0
        
        if self.jump_state == "waiting":
            if body_analysis['is_squatting'] and body_analysis['knee_bend']:
                self.jump_state = "squatting"
                self.state_start_time = current_time
                return "squatting", "Great! Now jump up like a frog!"
            else:
                return "waiting", "Squat down low like a frog preparing to jump"
        
        elif self.jump_state == "squatting":
            if body_analysis['is_jumping']:
                self.jump_state = "jumping"
                self.state_start_time = current_time
                return "jumping", "Fantastic jump! You're flying like a frog!"
            elif state_duration >= self.min_squat_time and not body_analysis['is_squatting']:
                # Lost squat position without jumping
                self.jump_state = "waiting"
                self.state_start_time = current_time
                return "waiting", "Try squatting down lower before jumping"
            elif state_duration > self.jump_timeout:
                # Timeout in squat position
                self.jump_state = "waiting"
                self.state_start_time = current_time
                return "waiting", "Good squat! Now jump up high!"
            else:
                return "squatting", f"Perfect squat! Now jump up! ({self.min_squat_time - state_duration:.1f}s)"
        
        elif self.jump_state == "jumping":
            if not body_analysis['is_jumping']:
                # Landed
                self.jump_state = "landed"
                self.state_start_time = current_time
                self.success_count += 1
                return "landed", "Amazing frog jump! You did it perfectly!"
            else:
                return "jumping", "Flying high like a frog!"
        
        elif self.jump_state == "landed":
            if state_duration > 2.0:  # Give 2 seconds to celebrate
                self.jump_state = "waiting"
                self.state_start_time = current_time
                return "waiting", "Ready for another frog jump?"
            else:
                return "landed", "Excellent landing! What a great frog jump!"
        
        return self.jump_state, "Processing..."
    
    def process_frame(self, frame):
        """
        Process a single frame and return detection results
        """
        if not MEDIAPIPE_AVAILABLE or self.pose is None:
            return {
                'detected': False,
                'confidence': 0.0,
                'message': 'MediaPipe not available',
                'feedback': 'Physical assessment requires MediaPipe installation'
            }
        
        try:
            # Convert BGR to RGB
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame
            results = self.pose.process(rgb)
            
            current_time = datetime.now()
            if self.state_start_time is None:
                self.state_start_time = current_time
            
            if results.pose_landmarks:
                body_analysis = self.analyze_body_position(results.pose_landmarks)
                
                if body_analysis:
                    new_state, message = self.update_jump_state(body_analysis, current_time)
                    
                    # Calculate confidence based on state and movement quality
                    confidence = 0.0
                    if new_state == "squatting":
                        confidence = 0.5 + (0.3 if body_analysis['knee_bend'] else 0)
                    elif new_state == "jumping":
                        confidence = 0.8 + (0.2 if body_analysis['hip_movement'] > 0.3 else 0)
                    elif new_state == "landed":
                        confidence = 1.0
                    
                    detected = new_state in ["squatting", "jumping", "landed"]
                    
                    # Generate appropriate feedback
                    if new_state == "squatting":
                        feedback = "Perfect frog position! Your knees are bent and you're low to the ground."
                    elif new_state == "jumping":
                        feedback = "Wow! You're jumping high in the air like a real frog!"
                    elif new_state == "landed":
                        feedback = "Outstanding frog jump! You squatted low and jumped high!"
                    else:
                        feedback = "Get ready to be a frog! Squat down low first, then jump high!"
                    
                    return {
                        'detected': detected,
                        'confidence': confidence,
                        'message': message,
                        'feedback': feedback,
                        'success_count': self.success_count,
                        'jump_state': new_state,
                        'hip_movement': body_analysis['hip_movement'],
                        'is_squatting': body_analysis['is_squatting'],
                        'is_jumping': body_analysis['is_jumping']
                    }
                else:
                    return {
                        'detected': False,
                        'confidence': 0.0,
                        'message': 'Move so I can see your whole body',
                        'feedback': 'I need to see your whole body to track your frog jump.',
                        'success_count': self.success_count,
                        'jump_state': self.jump_state
                    }
            else:
                return {
                    'detected': False,
                    'confidence': 0.0,
                    'message': 'Please stand in front of the camera',
                    'feedback': 'I can\'t see you clearly. Please move so your whole body is visible.',
                    'success_count': self.success_count,
                    'jump_state': self.jump_state
                }
                
        except Exception as e:
            return {
                'detected': False,
                'confidence': 0.0,
                'message': f'Detection error: {str(e)}',
                'feedback': 'There was a problem with the camera. Please try again.',
                'success_count': self.success_count,
                'jump_state': 'error'
            }
    
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
            'type': 'pose_detection',
            'confidence_threshold': self.confidence_threshold,
            'available': MEDIAPIPE_AVAILABLE,
            'phases': ['squat', 'jump', 'land']
        }
    
    def reset(self):
        """
        Reset task state for a new attempt
        """
        self.success_count = 0
        self.total_attempts = 0
        self.jump_state = "waiting"
        self.state_start_time = None
        self.baseline_hip_y = None
        self.squat_detected = False
        self.jump_detected = False
