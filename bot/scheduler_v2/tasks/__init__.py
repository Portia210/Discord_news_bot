"""
Individual Task Functions - Easy to test and edit independently
"""

from .news_report import (
    morning_news_report_task,
    evening_news_report_task
)
from .economic_calendar import (
    schedule_economic_calendar_task,
    economic_warning_task,
    economic_update_task
)

__all__ = [
    'morning_news_report_task', 'evening_news_report_task',
    'schedule_economic_calendar_task', 'economic_warning_task', 'economic_update_task',
] 