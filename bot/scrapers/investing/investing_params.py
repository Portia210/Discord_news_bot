
class Calendars():
    EARNINGS_CALENDAR = "earnings_calendar"
    HOLIDAY_CALENDAR = "holiday_calendar"
    ECONOMIC_CALENDAR = "economic_calendar"

class TimeRanges():
    TODAY = "today"
    THIS_WEEK = "thisWeek"
    CUSTOM = "custom"

class Countries():
    UNITED_STATES = "5"

class TimeZones():
    ISRAEL = "17"
    EASTERN_US = "8"

class Importance():
    LOW = "1"
    MEDIUM = "2"
    HIGH = "3"
    APP_IMPORTANCES = [MEDIUM, HIGH]

class InvestingParams():
    CALENDARS = Calendars
    TIME_RANGES = TimeRanges
    COUNTRIES = Countries
    TIME_ZONES = TimeZones
    IMPORTANCE = Importance




if __name__ == "__main__":
    print(InvestingParams.IMPORTANCE.LOW)
    print(InvestingParams.CALENDARS.EARNINGS_CALENDAR)