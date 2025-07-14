from enum import StrEnum


class Calendars(StrEnum):
    EARNINGS_CALENDAR = "earnings_calendar"
    HOLIDAY_CALENDAR = "holiday_calendar"
    ECONOMIC_CALENDAR = "economic_calendar"

class TimeRanges(StrEnum):
    TODAY = "today"
    THIS_WEEK = "thisWeek"
    CUSTOM = "custom"

class Countries(StrEnum):
    UNITED_STATES = "5"

class TimeZones(StrEnum):
    ISRAEL = "17"
    EASTERN_US = "8"

class Importance(StrEnum):
    LOW = "1"
    MEDIUM = "2"
    HIGH = "3"

class InvestingVariables():
    CALENDARS = Calendars
    TIME_RANGES = TimeRanges
    COUNTRIES = Countries
    TIME_ZONES = TimeZones
    IMPORTANCE = Importance




if __name__ == "__main__":
    print(InvestingVariables.IMPORTANCE.LOW)
    print(InvestingVariables.CALENDARS.EARNINGS_CALENDAR)