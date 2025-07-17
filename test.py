from cnbc_scraper.cnbc_scraper import extract_s_data_dict_from_html
from utils.read_write import *
import requests
from yf_scraper.headers import headers

url = "https://www.cnbc.com/2025/07/17/solar-wind-permit-interior-department-burgum-trump.html"

response = requests.get(url, headers=headers)
html = response.text

script = extract_s_data_dict_from_html(html)
write_json_file("temp.json", script)

print(script)