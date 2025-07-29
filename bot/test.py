#%%

import requests


res = requests.get("https://financialmodelingprep.com/api/v3/stock/list?apikey=g6z1o9xxPfKvz9whloFgBvlzafxCLktW")

if res.status_code == 200:
    res_json = res.json()
else:
    print(f"Error: {res.status_code}")


#%%

len_of_res_json = len(res_json)
print(len_of_res_json)

#%%

print(res_json[0])
# %%
clean_dict = {}
for item in res_json:
    # if only letters in symbol
    if item["symbol"].isalpha():
        clean_dict[item["symbol"]] = item
print(len(clean_dict))
# sort clean_dict by symbol alphabetically
clean_dict = dict(sorted(clean_dict.items(), key=lambda item: item[0]))

# %%
def search_for_symbol(symbol: str, clean_dict: dict):
    if symbol in clean_dict.keys():
        return True
    else:
        return False
    
def search_for_symbols(symbols: list, clean_dict: dict):
    output_dict = {}
    for symbol in symbols:
        output_dict[symbol] = search_for_symbol(symbol, clean_dict)
    return output_dict

# %%

symbols_to_search = ["SPMO", "SPY", "TQQQ"]
seach_result = search_for_symbols(symbols_to_search, clean_dict)
for symbol in symbols_to_search:
    if seach_result[symbol]:
        print(clean_dict[symbol])
    else:
        print(f"{symbol} not found")
# %%

# %%
# print 10 symbols from clean_dict
for i in range(100):
    print(list(clean_dict.keys())[i])

# %%


# %%