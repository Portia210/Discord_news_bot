"""
Individual Task Functions - Easy to test and edit independently
"""

from .news_report import (
    morning_news_report_task,
    evening_news_report_task
)

from .economic_calendar_tasks import (
    get_economic_calendar_task,
    economic_warning_task,
    economic_update_task
)

from .weekly_tasks import (
    weekly_backup_task
)

__all__ = [
    # Daily tasks
    'morning_news_report_task',
    'evening_news_report_task',
    
    # Economic calendar tasks
    'get_economic_calendar_task',
    'economic_warning_task',
    'economic_update_task',
    
    # Weekly tasks
    'weekly_backup_task',
] 