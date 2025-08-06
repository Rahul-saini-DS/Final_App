"""
Enhanced Task Manager for Physical and Linguistic Assessments
Coordinates individual task modules and provides unified API
"""

import os
import sys
import importlib
from datetime import datetime
import json

class EnhancedTaskManager:
    def __init__(self):
        self.physical_tasks = {}
        self.linguistic_tasks = {}
        self.task_modules = {}
        self.current_tasks = {}
        
        # Load all available task modules
        self._load_task_modules()
    
    def _load_task_modules(self):
        """
        Dynamically load all task modules from the tasks directory
        """
        tasks_dir = os.path.dirname(__file__)
        
        # Load physical tasks
        physical_files = [f for f in os.listdir(tasks_dir) if f.startswith('physical_') and f.endswith('.py')]
        for filename in physical_files:
            try:
                module_name = filename[:-3]  # Remove .py
                module_path = f'tasks.{module_name}'
                
                # Import the module
                module = importlib.import_module(module_path)
                
                # Find the task class (should be named like RaiseHandsTask, OneLegBalanceTask, etc.)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        hasattr(attr, 'task_name') and 
                        hasattr(attr, 'process_frame')):
                        
                        # Create instance and store
                        task_instance = attr()
                        task_info = task_instance.get_task_info()
                        age_group = task_info['age_group']
                        
                        self.physical_tasks[age_group] = task_instance
                        self.task_modules[task_info['task_name']] = module
                        print(f"✅ Loaded physical task: {task_info['task_name']} (Age {age_group})")
                        break
                        
            except Exception as e:
                print(f"⚠️  Failed to load physical task {filename}: {e}")
        
        # Load linguistic tasks
        linguistic_files = [f for f in os.listdir(tasks_dir) if f.startswith('linguistic_') and f.endswith('.py')]
        for filename in linguistic_files:
            try:
                module_name = filename[:-3]  # Remove .py
                module_path = f'tasks.{module_name}'
                
                # Import the module
                module = importlib.import_module(module_path)
                
                # Find the task class
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        hasattr(attr, 'task_name') and 
                        hasattr(attr, 'process_audio')):
                        
                        # Create instance and store
                        task_instance = attr()
                        task_info = task_instance.get_task_info()
                        age_group = task_info['age_group']
                        
                        self.linguistic_tasks[age_group] = task_instance
                        self.task_modules[task_info['task_name']] = module
                        print(f"✅ Loaded linguistic task: {task_info['task_name']} (Age {age_group})")
                        break
                        
            except Exception as e:
                print(f"⚠️  Failed to load linguistic task {filename}: {e}")
    
    def get_physical_task(self, age_group):
        """
        Get physical task for specific age group
        """
        if age_group in self.physical_tasks:
            task = self.physical_tasks[age_group]
            return {
                'available': True,
                'task_info': task.get_task_info(),
                'instance': task
            }
        else:
            # Fallback to basic task info
            basic_tasks = {
                "0-1": {"task": "raise_hands", "title": "Can baby raise both hands high?", "icon": "🖐️"},
                "1-2": {"task": "one_leg", "title": "Can you stand on one leg?", "icon": "🦵"},
                "2-3": {"task": "turn_around", "title": "Can you turn around in a circle?", "icon": "🔄"},
                "3-4": {"task": "stand_still", "title": "Can you stand very still?", "icon": "🧘"},
                "4-5": {"task": "frog_jump", "title": "Can you do a frog jump?", "icon": "🐸"},
                "5-6": {"task": "kangaroo_jump", "title": "Can you do kangaroo jumps?", "icon": "🦘"}
            }
            
            if age_group in basic_tasks:
                return {
                    'available': False,
                    'task_info': basic_tasks[age_group],
                    'instance': None
                }
            else:
                return None
    
    def get_linguistic_task(self, age_group):
        """
        Get linguistic task for specific age group
        """
        if age_group in self.linguistic_tasks:
            task = self.linguistic_tasks[age_group]
            return {
                'available': True,
                'task_info': task.get_task_info(),
                'instance': task
            }
        else:
            # Fallback to basic task info
            basic_tasks = {
                "0-1": {"task": "say_mama", "title": "Say 'ma‑ma'", "icon": "👶", "target_words": ["ma", "mama"]},
                "1-2": {"task": "apple", "title": "Say 'apple'", "icon": "🍎", "target_words": ["apple"]},
                "2-3": {"task": "rhyme_cat", "title": "What rhymes with 'cat'?", "icon": "🐱", "target_words": ["bat", "hat", "mat"]},
                "3-4": {"task": "fill_blank", "title": "Fill in the blank: 'The sun is ___'", "icon": "☀️", "target_words": ["bright", "hot", "yellow"]},
                "4-5": {"task": "sentence_sun", "title": "Make a sentence about the sun", "icon": "🌞", "target_words": ["sun", "bright"]},
                "5-6": {"task": "story_kite", "title": "Tell a short story about a kite", "icon": "🪁", "target_words": ["kite", "fly"]}
            }
            
            if age_group in basic_tasks:
                return {
                    'available': False,
                    'task_info': basic_tasks[age_group],
                    'instance': None
                }
            else:
                return None
    
    def process_physical_frame(self, age_group, frame_data):
        """
        Process a frame for physical assessment
        """
        task_info = self.get_physical_task(age_group)
        
        if not task_info or not task_info['available']:
            return {
                'error': 'Enhanced physical assessment not available for this age group',
                'fallback': True,
                'age_group': age_group
            }
        
        try:
            task_instance = task_info['instance']
            
            # Convert frame_data to cv2 format if needed
            import cv2
            import numpy as np
            import base64
            
            if isinstance(frame_data, str):
                # Decode base64 frame
                img_data = base64.b64decode(frame_data.split('base64,')[1])
                np_array = np.frombuffer(img_data, np.uint8)
                frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
            else:
                frame = frame_data
            
            # Process the frame
            result = task_instance.process_frame(frame)
            result['enhanced'] = True
            result['age_group'] = age_group
            result['task_name'] = task_info['task_info']['task_name']
            
            return result
            
        except Exception as e:
            return {
                'error': f'Physical processing error: {str(e)}',
                'fallback': True,
                'age_group': age_group
            }
    
    def process_linguistic_audio(self, age_group, audio_data):
        """
        Process audio for linguistic assessment
        """
        task_info = self.get_linguistic_task(age_group)
        
        if not task_info or not task_info['available']:
            return {
                'error': 'Enhanced linguistic assessment not available for this age group',
                'fallback': True,
                'age_group': age_group,
                'target_words': task_info['task_info'].get('target_words', []) if task_info else []
            }
        
        try:
            task_instance = task_info['instance']
            
            # Process the audio
            result = task_instance.process_audio(audio_data)
            result['enhanced'] = True
            result['age_group'] = age_group
            result['task_name'] = task_info['task_info']['task_name']
            
            return result
            
        except Exception as e:
            return {
                'error': f'Linguistic processing error: {str(e)}',
                'fallback': True,
                'age_group': age_group
            }
    
    def get_all_available_tasks(self):
        """
        Get summary of all available enhanced tasks
        """
        summary = {
            'physical_tasks': {},
            'linguistic_tasks': {},
            'total_physical': len(self.physical_tasks),
            'total_linguistic': len(self.linguistic_tasks)
        }
        
        for age_group, task in self.physical_tasks.items():
            task_info = task.get_task_info()
            summary['physical_tasks'][age_group] = {
                'name': task_info['task_name'],
                'title': task_info['title'],
                'icon': task_info['icon'],
                'available': task_info['available']
            }
        
        for age_group, task in self.linguistic_tasks.items():
            task_info = task.get_task_info()
            summary['linguistic_tasks'][age_group] = {
                'name': task_info['task_name'],
                'title': task_info['title'],
                'icon': task_info['icon'],
                'available': task_info['available']
            }
        
        return summary
    
    def reset_task(self, age_group, task_type):
        """
        Reset a specific task for a new attempt
        """
        if task_type == 'physical' and age_group in self.physical_tasks:
            self.physical_tasks[age_group].reset()
            return True
        elif task_type == 'linguistic' and age_group in self.linguistic_tasks:
            self.linguistic_tasks[age_group].reset()
            return True
        return False
    
    def get_task_progress(self, age_group, task_type):
        """
        Get progress information for a specific task
        """
        if task_type == 'physical' and age_group in self.physical_tasks:
            task = self.physical_tasks[age_group]
            return {
                'success_count': task.success_count,
                'total_attempts': task.total_attempts,
                'task_name': task.task_name,
                'age_group': age_group
            }
        elif task_type == 'linguistic' and age_group in self.linguistic_tasks:
            task = self.linguistic_tasks[age_group]
            progress = {
                'success_count': task.success_count,
                'total_attempts': task.total_attempts,
                'task_name': task.task_name,
                'age_group': age_group
            }
            
            # Add story-specific progress if available
            if hasattr(task, 'get_progress_summary'):
                progress.update(task.get_progress_summary())
            
            return progress
        
        return None

# Global instance
enhanced_task_manager = None

def get_task_manager():
    """
    Get or create the global task manager instance
    """
    global enhanced_task_manager
    if enhanced_task_manager is None:
        enhanced_task_manager = EnhancedTaskManager()
    return enhanced_task_manager
