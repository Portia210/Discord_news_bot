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

def is_scheduler_running():
    """Check if the global scheduler is running"""
    global _scheduler_instance
    return _scheduler_instance is not None and _scheduler_instance.is_running()

def clear_scheduler():
    """Clear the global scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is not None:
        _scheduler_instance.stop()
        _scheduler_instance = None 