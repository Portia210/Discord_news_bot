import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

APP_IS_REMOTE = True if os.getenv("APP_IS_REMOTE") == "true" else False


class Timezones():
    EASTERN_US = "America/New_York"
    ISRAEL = "Asia/Jerusalem"
    APP_TIMEZONE = ISRAEL

class Server():
    LOCAL_SERVER_IP = "127.0.0.1"
    PUBLIC_SERVER_IP = "54.165.14.238"
    CURRENT_SERVER_IP = PUBLIC_SERVER_IP if APP_IS_REMOTE else LOCAL_SERVER_IP
    PORT = 8000
    API_TOKEN = os.getenv("SERVER_API_TOKEN")


class Config:
    TIMEZONES = Timezones
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    SERVER = Server
