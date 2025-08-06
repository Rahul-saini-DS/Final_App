"""
Enhanced Tasks Package for Child Assessment
Provides advanced physical and linguistic assessment capabilities
"""

from .enhanced_task_manager import get_task_manager, EnhancedTaskManager

# Try to import individual tasks (they may fail if dependencies are missing)
try:
    from .physical_0_raise_hands import RaiseHandsTask
except ImportError:
    RaiseHandsTask = None

try:
    from .physical_1_one_leg_balance import OneLegBalanceTask
except ImportError:
    OneLegBalanceTask = None

try:
    from .physical_4_frog_jump import FrogJumpTask
except ImportError:
    FrogJumpTask = None

try:
    from .linguistic_0_say_mama import SayMamaTask
except ImportError:
    SayMamaTask = None

try:
    from .linguistic_5_story_kite import StoryKiteTask
except ImportError:
    StoryKiteTask = None

__all__ = [
    'get_task_manager',
    'EnhancedTaskManager',
    'RaiseHandsTask',
    'OneLegBalanceTask', 
    'FrogJumpTask',
    'SayMamaTask',
    'StoryKiteTask'
]
