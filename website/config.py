import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()



class Timezones():
    EASTERN_US = "America/New_York"
    ISRAEL = "Asia/Jerusalem"
    APP_TIMEZONE = ISRAEL



class Config:
    TIMEZONES = Timezones
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
