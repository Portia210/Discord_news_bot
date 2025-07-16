import urllib.request
import ssl
from config import Config

# Get proxy configuration from config
PROXY_HOST = Config.PROXY.HOST
PROXY_PORT = Config.PROXY.PORT
PROXY_CUSTOMER_ID = Config.PROXY.CUSTOMER_ID
PROXY_ZONE = Config.PROXY.ZONE
PROXY_PASSWORD = Config.PROXY.PASSWORD
# TARGET_URL must be set manually, as config.urls does not exist
TARGET_URL = "https://example.com"  # <-- Set your target URL here

proxy_user = f"brd-customer-{PROXY_CUSTOMER_ID}-zone-{PROXY_ZONE}"
proxy_pass = PROXY_PASSWORD
proxy_url = f"http://{proxy_user}:{proxy_pass}@{PROXY_HOST}:{PROXY_PORT}"

proxy_handler = urllib.request.ProxyHandler({
    "http": proxy_url,
    "https": proxy_url,
})

# Create SSL context to ignore SSL certificate errors
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

opener = urllib.request.build_opener(proxy_handler, urllib.request.HTTPSHandler(context=ssl_context))
urllib.request.install_opener(opener)

req = urllib.request.Request(TARGET_URL)
req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36")

try:
    with urllib.request.urlopen(req, context=ssl_context) as response:
        html = response.read()
        print(html.decode("utf-8"))
except Exception as e:
    print("Error:", e)
