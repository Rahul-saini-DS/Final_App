"""
Enhanced Physical Task: One Leg Balance (Age 1-2)
Detects when child stands on one leg for balance
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

class OneLegBalanceTask:
    def __init__(self):
        self.task_name = "one_leg_balance"
        self.age_group = "1-2"
        self.title = "Can you stand on one leg?"
        self.description = "Show me your amazing balance skills!"
        self.instruction = "Stand on one foot for 3 seconds"
        self.icon = "🦵"
        
        # Detection parameters
        self.min_balance_time = 3.0  # seconds
        self.confidence_threshold = 0.75
        self.success_count = 0
        self.total_attempts = 0
        self.start_time = None
        self.balance_start = None
        self.last_balance_leg = None  # Track which leg was being balanced on
        
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
    
    def calculate_leg_lift(self, landmarks):
        """
        Calculate how much each leg is lifted and determine balance
        """
        if not landmarks or not MEDIAPIPE_AVAILABLE:
            return False, 0.0, None
        
        try:
            # Get key landmarks
            left_hip = landmarks.landmark[POSE_LMS.LEFT_HIP]
            right_hip = landmarks.landmark[POSE_LMS.RIGHT_HIP]
            left_knee = landmarks.landmark[POSE_LMS.LEFT_KNEE]
            right_knee = landmarks.landmark[POSE_LMS.RIGHT_KNEE]
            left_ankle = landmarks.landmark[POSE_LMS.LEFT_ANKLE]
            right_ankle = landmarks.landmark[POSE_LMS.RIGHT_ANKLE]
            left_heel = landmarks.landmark[POSE_LMS.LEFT_HEEL]
            right_heel = landmarks.landmark[POSE_LMS.RIGHT_HEEL]
            
            # Check visibility
            required_landmarks = [left_hip, right_hip, left_knee, right_knee, 
                                left_ankle, right_ankle, left_heel, right_heel]
            if any(lm.visibility < 0.5 for lm in required_landmarks):
                return False, 0.0, None
            
            # Calculate average hip height as reference
            avg_hip_y = (left_hip.y + right_hip.y) / 2
            
            # Calculate leg lift metrics
            left_knee_lift = avg_hip_y - left_knee.y  # Positive if knee is above hip level
            right_knee_lift = avg_hip_y - right_knee.y
            
            left_ankle_lift = avg_hip_y - left_ankle.y  # How high the ankle is
            right_ankle_lift = avg_hip_y - right_ankle.y
            
            # Determine if a leg is significantly raised
            knee_lift_threshold = 0.1  # Knee should be at least this much above average
            ankle_lift_threshold = 0.15  # Ankle should be this much above average
            
            left_leg_raised = (left_knee_lift > knee_lift_threshold and 
                             left_ankle_lift > ankle_lift_threshold)
            right_leg_raised = (right_knee_lift > knee_lift_threshold and 
                              right_ankle_lift > ankle_lift_threshold)
            
            # Additional stability check - supporting leg should be relatively straight
            left_leg_straight = abs(left_knee.x - left_ankle.x) < 0.1  # Vertical alignment
            right_leg_straight = abs(right_knee.x - right_ankle.x) < 0.1
            
            # Determine balance state
            balance_detected = False
            confidence = 0.0
            balanced_leg = None
            
            if left_leg_raised and right_leg_straight:
                # Standing on right leg
                balance_detected = True
                balanced_leg = 'right'
                confidence = min(1.0, (left_knee_lift + left_ankle_lift) * 2)
            elif right_leg_raised and left_leg_straight:
                # Standing on left leg
                balance_detected = True
                balanced_leg = 'left'
                confidence = min(1.0, (right_knee_lift + right_ankle_lift) * 2)
            
            # Boost confidence if leg is well lifted
            if balance_detected:
                if balanced_leg == 'right' and left_ankle_lift > 0.2:
                    confidence = min(1.0, confidence + 0.2)
                elif balanced_leg == 'left' and right_ankle_lift > 0.2:
                    confidence = min(1.0, confidence + 0.2)
            
            return balance_detected, confidence, balanced_leg
            
        except Exception as e:
            print(f"Leg balance calculation error: {e}")
            return False, 0.0, None
    
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
                detected, confidence, balanced_leg = self.calculate_leg_lift(results.pose_landmarks)
                
                # Track balance timing
                current_time = datetime.now()
                
                if detected and confidence >= self.confidence_threshold:
                    if self.balance_start is None or self.last_balance_leg != balanced_leg:
                        self.balance_start = current_time
                        self.last_balance_leg = balanced_leg
                    
                    balance_duration = (current_time - self.balance_start).total_seconds()
                    
                    if balance_duration >= self.min_balance_time:
                        self.success_count += 1
                        message = f"Amazing balance! You stood on your {balanced_leg} leg for {balance_duration:.1f} seconds!"
                        feedback = f"Perfect! You showed great balance standing on one foot."
                        self.balance_start = None  # Reset for next attempt
                        self.last_balance_leg = None
                    else:
                        remaining = self.min_balance_time - balance_duration
                        message = f"Great balance! Keep it up for {remaining:.1f} more seconds..."
                        feedback = f"Excellent! You're balancing on your {balanced_leg} leg. Keep steady!"
                else:
                    self.balance_start = None
                    self.last_balance_leg = None
                    if detected:
                        message = "Try to lift your leg higher and hold steady"
                        feedback = "Good attempt! Try lifting your leg a bit higher and hold it steady."
                    else:
                        message = "Stand on one leg like a flamingo"
                        feedback = "Lift one leg up and try to balance on the other leg. You can do it!"
                
                return {
                    'detected': detected,
                    'confidence': confidence,
                    'message': message,
                    'feedback': feedback,
                    'success_count': self.success_count,
                    'balanced_leg': balanced_leg,
                    'balance_duration': (current_time - self.balance_start).total_seconds() if self.balance_start else 0
                }
            else:
                return {
                    'detected': False,
                    'confidence': 0.0,
                    'message': 'Please stand in front of the camera',
                    'feedback': 'I can\'t see you clearly. Please move so your whole body is visible.',
                    'success_count': self.success_count,
                    'balanced_leg': None,
                    'balance_duration': 0
                }
                
        except Exception as e:
            return {
                'detected': False,
                'confidence': 0.0,
                'message': f'Detection error: {str(e)}',
                'feedback': 'There was a problem with the camera. Please try again.',
                'success_count': self.success_count,
                'balanced_leg': None,
                'balance_duration': 0
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
            'min_balance_time': self.min_balance_time,
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
        self.balance_start = None
        self.last_balance_leg = None
