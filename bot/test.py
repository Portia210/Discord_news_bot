dict = {"AAPL": "Apple Inc.", "MSFT": "Microsoft Corp.", "GOOGL": "Alphabet Inc.", "PLTR": "Palantir Technologies Inc.", "IREN": "Iren SpA"}
dict2 = {"IREN": "Iren SpA", "TSLA": "Tesla Inc.", "NVDA": "NVIDIA Corp.", "META": "Meta Platforms Inc.", "AMZN": "Amazon.com Inc."}

dict3= {}

print(dict3)
dict3.update(dict2)
print(dict3)
dict3.update(dict)
print(dict3)