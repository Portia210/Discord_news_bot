"""
Task and TaskCondition classes
"""

import pytz
from datetime import datetime, time, timedelta
from typing import Callable, List, Optional
from utils.logger import logger
from config import Config


class TaskCondition:
    """Represents a condition that can cancel or modify scheduling"""
    
    def __init__(self, name: str, check_func: Callable, cancel_on_true: bool = True):
        self.name = name
        self.check_func = check_func
        self.cancel_on_true = cancel_on_true
    
    async def check(self) -> bool:
        """Check the condition and return True if it should cancel scheduling"""
        try:
            result = await self.check_func()
            if result and self.cancel_on_true:
                logger.info(f"🛑 Condition '{self.name}' triggered - cancelling tasks")
            return result and self.cancel_on_true
        except Exception as e:
            logger.error(f"❌ Error checking condition '{self.name}': {e}")
            return False


class Task:
    """Represents a single scheduled task"""
    
    def __init__(self, 
                 name: str,
                 func: Callable,
                 time_str: str,  # "14:30" or "09:00"
                 days: Optional[List[str]] = None,  # ["mon", "tue", "wed", "thu", "fri"]
                 conditions: Optional[List[TaskCondition]] = None,
                 timezone: pytz.timezone = None):
        
        self.name = name
        self.func = func
        self.time_str = time_str
        self.days = days or ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        self.conditions = conditions or []
        self.timezone = timezone or pytz.timezone(Config.TIMEZONES.APP_TIMEZONE)
        self.is_running = False
        
        # Parse time
        try:
            hour, minute = map(int, time_str.split(':'))
            self.schedule_time = time(hour, minute)
        except ValueError:
            raise ValueError(f"Invalid time format: {time_str}. Use HH:MM")
    
    def should_run_today(self) -> bool:
        """Check if task should run today"""
        today = datetime.now(self.timezone).strftime('%a').lower()[:3]
        return today in self.days
    
    def get_next_run(self) -> datetime:
        """Calculate next run time"""
        now = datetime.now(self.timezone)
        today = now.date()
        
        # Create datetime for today at scheduled time
        next_run = datetime.combine(today, self.schedule_time, tzinfo=self.timezone)
        
        # If time has passed today, schedule for tomorrow
        if next_run <= now:
            next_run += timedelta(days=1)
        
        # If task doesn't run today, find next valid day
        while not self.should_run_today():
            next_run += timedelta(days=1)
        
        return next_run
    
    async def check_conditions(self) -> bool:
        """Check all conditions, return True if should cancel"""
        for condition in self.conditions:
            if await condition.check():
                return True
        return False
    
    async def execute(self):
        """Execute the task"""
        if self.is_running:
            logger.warning(f"⚠️ Task '{self.name}' is already running")
            return
        
        self.is_running = True
        try:
            logger.info(f"🚀 Executing task: {self.name}")
            await self.func()
            logger.info(f"✅ Task completed: {self.name}")
        except Exception as e:
            logger.error(f"❌ Task failed: {self.name} - {e}")
        finally:
            self.is_running = False


def create_condition(name: str, check_func: Callable, cancel_on_true: bool = True) -> TaskCondition:
    """Helper function to create conditions"""
    return TaskCondition(name, check_func, cancel_on_true)


def parse_days(days_str: str) -> List[str]:
    """Parse days string like 'mon-fri' or 'mon,wed,fri'"""
    if '-' in days_str:
        # Range like 'mon-fri'
        start, end = days_str.split('-')
        all_days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        start_idx = all_days.index(start.lower())
        end_idx = all_days.index(end.lower())
        
        if start_idx <= end_idx:
            return all_days[start_idx:end_idx + 1]
        else:
            # Handle weekend wrap-around
            return all_days[start_idx:] + all_days[:end_idx + 1]
    else:
        # Comma-separated like 'mon,wed,fri'
        return [day.strip().lower() for day in days_str.split(',')] 