import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

REMOTE_SERVER = True if os.getenv("REMOTE_SERVER") == "true" else False
print(f"REMOTE_SERVER: {REMOTE_SERVER}")


class Timezones():
    EASTERN_US = "America/New_York"
    ISRAEL = "Asia/Jerusalem"
    APP_TIMEZONE = ISRAEL

class Server():
    LOCAL_SERVER_IP = "127.0.0.1"
    REMOTE_SERVER_IP = "54.165.14.238"
    APP_SERVER_IP = REMOTE_SERVER_IP if REMOTE_SERVER else LOCAL_SERVER_IP
    PORT = 8000
    API_TOKEN = os.getenv("SERVER_API_TOKEN")


class Config:
    TIMEZONES = Timezones
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    SERVER = Server
