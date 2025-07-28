from datetime import time

class ScheduleItem():
    """Represents a schedule with all its properties"""
    def __init__(self, name: str, hour: int, minute: int, second: int = 0):
        self.name = name
        self.hour = hour
        self.minute = minute
        self.second = second
    
    @property
    def time(self) -> time:
        """Returns formatted time string in HH:MM format"""
        return time(self.hour, self.minute, self.second)

class Schedule():
    """Represents a schedule with all its properties"""
    DAILY_SETUP = ScheduleItem("daily_setup", 7, 58)
    DAILY_ECONOMIC_CALENDAR = ScheduleItem("daily_economic_calendar", 8, 0)