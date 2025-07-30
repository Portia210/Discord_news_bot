import requests
from config import Config

def get_symbols_list():
    try:
        res = requests.get(f"https://financialmodelingprep.com/api/v3/stock/list?apikey={Config.TOKENS.FMP_API_KEY}")

        if res.status_code == 200:
            res_json = res.json()
            clean_list = [item for item in res_json if item["symbol"].isalpha()]
            # sort clean_list by symbol alphabetically
            clean_list = sorted(clean_list, key=lambda item: item["symbol"])
            return clean_list
    
        else:
            print(f"Error: {res.status_code}")
            return None
 
    except Exception as e:
        print(f"Error: {e}")
        return None