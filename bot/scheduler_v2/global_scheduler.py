"""
Global Scheduler Access - Provides global access to CoreScheduler/TasksScheduler instance
"""

# Global scheduler instance
_discord_scheduler_instance = None

def get_discord_scheduler():
    """Get the global CoreScheduler/TasksScheduler instance"""
    global _discord_scheduler_instance
    return _discord_scheduler_instance

def set_discord_scheduler(scheduler):
    """Set the global CoreScheduler/TasksScheduler instance"""
    global _discord_scheduler_instance
    _discord_scheduler_instance = scheduler 