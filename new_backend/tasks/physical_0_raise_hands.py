"""
Enhanced Physical Task: Raise Hands (Age 0-1)
Detects when both wrists are raised above the head level
"""

import cv2
import numpy as np
import mediapipe as mp
from datetime import datetime

# MediaPipe setup
try:
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    POSE_LMS = mp_pose.PoseLandmark
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("WARNING: MediaPipe not available for physical assessments")

class RaiseHandsTask:
    def __init__(self):
        self.task_name = "raise_hands"
        self.age_group = "0-1"
        self.title = "Can baby raise both hands high?"
        self.description = "Show me you can lift both hands above your head!"
        self.instruction = "Raise both hands above your head"
        self.icon = "🖐️"
        
        # Detection parameters
        self.min_detection_time = 2.0  # seconds
        self.confidence_threshold = 0.7
        self.success_count = 0
        self.total_attempts = 0
        self.start_time = None
        self.detection_start = None
        
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
    
    def detect_raised_hands(self, landmarks):
        """
        Enhanced detection for raised hands with multiple criteria
        """
        if not landmarks or not MEDIAPIPE_AVAILABLE:
            return False, 0.0
        
        try:
            # Get key landmarks
            nose = landmarks.landmark[POSE_LMS.NOSE]
            left_wrist = landmarks.landmark[POSE_LMS.LEFT_WRIST]
            right_wrist = landmarks.landmark[POSE_LMS.RIGHT_WRIST]
            left_shoulder = landmarks.landmark[POSE_LMS.LEFT_SHOULDER]
            right_shoulder = landmarks.landmark[POSE_LMS.RIGHT_SHOULDER]
            
            # Check visibility
            if (left_wrist.visibility < 0.5 or right_wrist.visibility < 0.5 or
                nose.visibility < 0.5 or left_shoulder.visibility < 0.5 or
                right_shoulder.visibility < 0.5):
                return False, 0.0
            
            # Calculate confidence based on multiple factors
            confidence_factors = []
            
            # Factor 1: Wrists above nose (primary)
            head_threshold = 0.08
            left_above_head = left_wrist.y < (nose.y - head_threshold)
            right_above_head = right_wrist.y < (nose.y - head_threshold)
            both_above_head = left_above_head and right_above_head
            
            if both_above_head:
                confidence_factors.append(0.4)  # 40% weight
            
            # Factor 2: Wrists above shoulders
            left_above_shoulder = left_wrist.y < left_shoulder.y
            right_above_shoulder = right_wrist.y < right_shoulder.y
            both_above_shoulders = left_above_shoulder and right_above_shoulder
            
            if both_above_shoulders:
                confidence_factors.append(0.3)  # 30% weight
            
            # Factor 3: Arm extension (check if arms are extended upward)
            left_extended = abs(left_wrist.x - left_shoulder.x) < 0.2  # Not too far from shoulder horizontally
            right_extended = abs(right_wrist.x - right_shoulder.x) < 0.2
            arms_extended = left_extended and right_extended
            
            if arms_extended:
                confidence_factors.append(0.2)  # 20% weight
            
            # Factor 4: Symmetry (both hands at similar height)
            height_diff = abs(left_wrist.y - right_wrist.y)
            symmetric = height_diff < 0.1
            
            if symmetric:
                confidence_factors.append(0.1)  # 10% weight
            
            # Calculate total confidence
            total_confidence = sum(confidence_factors)
            success = total_confidence >= self.confidence_threshold
            
            return success, total_confidence
            
        except Exception as e:
            print(f"Raised hands detection error: {e}")
            return False, 0.0
    
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
            
            if results.pose_landmarks:
                detected, confidence = self.detect_raised_hands(results.pose_landmarks)
                
                # Track detection timing
                current_time = datetime.now()
                
                if detected:
                    if self.detection_start is None:
                        self.detection_start = current_time
                    
                    detection_duration = (current_time - self.detection_start).total_seconds()
                    
                    if detection_duration >= self.min_detection_time:
                        self.success_count += 1
                        message = f"Great job! You raised your hands for {detection_duration:.1f} seconds!"
                        feedback = "Perfect hand raising! Both hands were high above your head."
                        self.detection_start = None  # Reset for next attempt
                    else:
                        remaining = self.min_detection_time - detection_duration
                        message = f"Keep your hands up! {remaining:.1f} seconds to go..."
                        feedback = "Good! Keep holding your hands high above your head."
                else:
                    self.detection_start = None
                    message = "Raise both hands above your head"
                    feedback = "Lift both hands up high above your head like you're reaching for the sky!"
                
                return {
                    'detected': detected,
                    'confidence': confidence,
                    'message': message,
                    'feedback': feedback,
                    'success_count': self.success_count,
                    'detection_duration': (current_time - self.detection_start).total_seconds() if self.detection_start else 0
                }
            else:
                return {
                    'detected': False,
                    'confidence': 0.0,
                    'message': 'Please stand in front of the camera',
                    'feedback': 'I can\'t see you clearly. Please move so your whole body is visible.',
                    'success_count': self.success_count,
                    'detection_duration': 0
                }
                
        except Exception as e:
            return {
                'detected': False,
                'confidence': 0.0,
                'message': f'Detection error: {str(e)}',
                'feedback': 'There was a problem with the camera. Please try again.',
                'success_count': self.success_count,
                'detection_duration': 0
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
            'min_detection_time': self.min_detection_time,
            'confidence_threshold': self.confidence_threshold,
            'available': MEDIAPIPE_AVAILABLE
        }
    
    def reset(self):
        """
        Reset task state for a new attempt
        """
        self.success_count = 0
        self.total_attempts = 0
        self.start_time = None
        self.detection_start = None
