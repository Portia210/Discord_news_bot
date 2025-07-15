"""
Individual Task Functions - Easy to test and edit independently
"""

from .daily_tasks import (
    daily_schedule_task,
    market_open_check_task,
    daily_report_task,
    morning_greeting_task,
    evening_summary_task,
    system_health_check_task,
    news_check_task,
    schedule_future_events_task
)

from .weekly_tasks import (
    weekly_backup_task
)

# from .custom_tasks import (
#     # Add your custom tasks here
# )

__all__ = [
    # Daily tasks
    'daily_schedule_task',
    'market_open_check_task', 
    'daily_report_task',
    'morning_greeting_task',
    'evening_summary_task',
    'system_health_check_task',
    'news_check_task',
    'schedule_future_events_task',
    
    # Weekly tasks
    'weekly_backup_task',
] 