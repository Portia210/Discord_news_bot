import yfinance as yf

stock = yf.Ticker("ABEV3.SA")
price = stock.info['regularMarketPrice']
print(price)
 