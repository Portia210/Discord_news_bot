from utils import read_json_file

request_json = read_json_file(f'scrapers/investing/requests_json/economic_calendar.json')
print(request_json)