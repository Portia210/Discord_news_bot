#%%

import requests


res = requests.get("https://financialmodelingprep.com/api/v3/stock/list?apikey=g6z1o9xxPfKvz9whloFgBvlzafxCLktW")

if res.status_code == 200:
    res_json = res.json()
else:
    print(f"Error: {res.status_code}")


#%%