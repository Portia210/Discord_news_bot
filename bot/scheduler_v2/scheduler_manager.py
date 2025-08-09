"""
Global Scheduler Access - Provides global access to CoreScheduler/TasksScheduler instance
"""

# Global scheduler instance
_scheduler_instance = None

def get_scheduler():
    """Get the global CoreScheduler/TasksScheduler instance"""
    global _scheduler_instance
    return _scheduler_instance

def set_scheduler(scheduler):
    """Set the global CoreScheduler/TasksScheduler instance"""
    global _scheduler_instance
    _scheduler_instance = scheduler 