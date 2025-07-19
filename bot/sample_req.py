import requests
import json

url = "https://query1.finance.yahoo.com/v7/finance/quote?fields=fiftyTwoWeekHigh%2CfiftyTwoWeekLow%2CfromCurrency%2CfromExchange%2CheadSymbolAsString%2ClogoUrl%2ClongName%2CmarketCap%2CmessageBoardId%2CoptionsType%2CovernightMarketTime%2CovernightMarketPrice%2CovernightMarketChange%2CovernightMarketChangePercent%2CregularMarketTime%2CregularMarketChange%2CregularMarketChangePercent%2CregularMarketOpen%2CregularMarketPrice%2CregularMarketSource%2CregularMarketVolume%2CpostMarketTime%2CpostMarketPrice%2CpostMarketChange%2CpostMarketChangePercent%2CpreMarketTime%2CpreMarketPrice%2CpreMarketChange%2CpreMarketChangePercent%2CshortName%2CtoCurrency%2CtoExchange%2CunderlyingExchangeSymbol%2CunderlyingSymbol%2CstockStory&formatted=true&imgHeights=50&imgLabels=logoUrl&imgWidths=50&symbols=AAPL,AI&enablePrivateCompany=true&overnightPrice=true&topPickThisMonth=true&lang=en-US&region=US&crumb=X7OMi%2FFe4nm"

payload = {}
headers = {
  'accept': '*/*',
  'accept-language': 'en,en-US;q=0.9',
  'origin': 'https://finance.yahoo.com',
  'priority': 'u=1, i',
  'referer': 'https://finance.yahoo.com/quote/PLTR/news/',
  'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-site',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
  'Cookie': 'GUCS=AQXCfRV1; A3=d=AQABBKGKc2cCEHT7atMqsTimn1z_h2DE9DgFEgABCAG-ZmiWaF5EyyMA9qMCAAcIdFG_ZgcRnMQ&S=AQAAAhI85Rn162FjBhJVZVHLEzg; GUC=AQABCAFoZr5olkIc-wSJ&s=AQAAAIdHtF0U&g=aGVycQ; A1S=d=AQABBKGKc2cCEHT7atMqsTimn1z_h2DE9DgFEgABCAG-ZmiWaF5EyyMA9qMCAAcIdFG_ZgcRnMQ&S=AQAAAhI85Rn162FjBhJVZVHLEzg; EuConsent=CQT7KEAQT7KEAAOACBHEBxFoAP_gAEPgACiQKptB9G7WTXFneTp2YPskOYwX0VBJ4MAwBgCBAUABzBIUIBwCVmAzJEyIICACGAIAIGBBIABtGAhAQEAAYIAFAABIAEgAIBAAIGAAACAAAABACAAAAAAAAAAQgEAXMBQgmCYEBFoIQUhAggAgAQAAAAAEAIgBCAQAEAAAQAAACAAIACgAAgAAAAAAAAAEAFAIEAAAIAECAgvkdAAAAAAAAAAIAAYACAABAAAAAIKpgAkGhUQRFgQAhEIGEECAAQUBABQIAgAACBAAAATBAUIAwAVGAiAEAIAAAAAAAAAAABAAABAAhAAEAAQIAAAAAIAAgAIAAAACAAAAAAAAAAAAAAAAAAAAAAAAAGIBAggCAABBAAQUAAAAAgAAAAAAAAAIgACAAAAAAAAAAAAAAIgAAAAAAAAAAAAAAAAAAIEAAAIAAAAoDEFgAAAAAAAAAAAAAACAABAAAAAIAAA; A1=d=AQABBKGKc2cCEHT7atMqsTimn1z_h2DE9DgFEgABCAG-ZmiWaF5EyyMA9qMCAAcIdFG_ZgcRnMQ&S=AQAAAhI85Rn162FjBhJVZVHLEzg; cmp=t=1751478890&j=1&u=1---&v=87; axids=gam=y-ZXW.GtdE2uIcKMnJTlVCAkYz_ZrV42oj~A&dv360=eS00QXB3bmd4RTJ1Rzg5alBpbmxETG83MnRHa3JOZEdWVX5B&ydsp=y-YdyE4LNE2uKrZBVA1MkZ_6SQXDAUX2eM~A&tbla=y-YA.WjD9E2uJ5v8dqu4d6y_zxH8rziNJW~A; tbla_id=e7fe438e-84c7-4cc2-917f-3b82510bda39-tuctf2f6fdb; PRF=t%3DPLTR%26dock-collapsed%3Dtrue'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

with open("response.json", "w", encoding="utf-8") as f:
    json.dump(response.json(), f, indent=4)