import requests
import json

url = "http://127.0.0.1:8000/api/news-report"

payload = json.dumps({
  "title": "דוח חדשות פיננסיות - בוקר",
  "report_title": "דוח חדשות בוקר",
  "report_subtitle": "עדכוני שוק ופיננסים אחרונים",
  "report_time": "evening",
  "generation_time": "2025-07-20 09:30:00",
  "news_data": [
    {
      "time": "morning",
      "message": "הבוקר פורסמו נתוני ה-CPI בארצות הברית, והם היו גבוהים מהצפוי. עלייה זו מצביעה על לחצים מתמשכים באינפלציה, מה שמוביל לחששות לגבי יציבות המחירים.",
      "link": "https://www.bloomberg.com/news/articles/cpi-data"
    },
    {
      "time": "noon",
      "message": "הנתונים האחרונים עוררו ציפיות כי ה-Fed יעלה את הריבית ב-0.25% בשבוע הבא. צעד זה מבוצע כדי למתן את הלחצים האינפלציוניים ולהחזיר יציבות לשווקים.",
      "link": "https://www.reuters.com/markets/fed-rate-hike"
    },
    {
      "time": "afternoon",
      "message": "שיעור האבטלה בארצות הברית צפוי להישאר על 3.7%. שיעור זה משקף שוק עבודה יציב וחזק, המצביע על כך שהכלכלה האמריקאית עדיין במצב טוב."
    }
  ],
  "price_symbols": [
    {
      "ticker": "AAPL",
      "company": "Apple Inc.",
      "price": "$150.25",
      "change_amount": "+2.15",
      "change_percent": "1.45%",
      "is_positive": True
    },
    {
      "ticker": "GOOGL",
      "company": "Alphabet Inc.",
      "price": "$2,850.75",
      "change_amount": "-15.30",
      "change_percent": "0.53%",
      "is_positive": False
    },
    {
      "ticker": "MSFT",
      "company": "Microsoft Corp.",
      "price": "$380.50",
      "change_amount": "+5.75",
      "change_percent": "1.54%",
      "is_positive": True
    },
    {
      "ticker": "TSLA",
      "company": "Tesla Inc.",
      "price": "$245.80",
      "change_amount": "-8.20",
      "change_percent": "3.23%",
      "is_positive": False
    },
    {
      "ticker": "SPY",
      "company": "S&P 500",
      "price": "$245.80",
      "change_amount": "-8.20",
      "change_percent": "3.23%",
      "is_positive": False
    },
    {
      "ticker": "QQQ",
      "company": "NASDAQ 100",
      "price": "$245.80",
      "change_amount": "-8.20",
      "change_percent": "3.23%",
      "is_positive": False
    },
    {
      "ticker": "IWM",
      "company": "Russell 2000",
      "price": "$245.80",
      "change_amount": "-8.20",
      "change_percent": "3.23%",
      "is_positive": False
    },
    {
      "ticker": "VIX",
      "company": "VIX",
      "price": "$245.80",
      "change_amount": "-8.20",
      "change_percent": "3.23%",
      "is_positive": False
    }
  ]
})
headers = {
  'Authorization': 'your-secret-token',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)