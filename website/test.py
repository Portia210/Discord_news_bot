from utils.read_write import write_json_file
from datetime import datetime

news = {
        'title': 'דוח חדשות פיננסיות',
        'report_title': 'דוח חדשות',
        'report_subtitle': 'עדכוני שוק ופיננסים אחרונים',
        'report_time': 'morning',  # or 'evening'
        'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'news_data': [
            {
                'time': 'morning',
                'message': 'הבוקר פורסמו נתוני ה-CPI בארצות הברית, והם היו גבוהים מהצפוי.',
                'link': 'https://example.com/news1'
            },
            {
                'time': 'noon',
                'message': 'הנתונים האחרונים עוררו ציפיות כי ה-Fed יעלה את הריבית ב-0.25% בשבוע הבא.',
                'link': 'https://example.com/news2'
            }
        ],
        'price_symbols': [
            {
                'ticker': 'AAPL',
                'company': 'Apple Inc.',
                'price': '$150.25',
                'change_amount': '+2.15',
                'change_percent': '1.45%',
                'is_positive': True
            },
            {
                'ticker': 'GOOGL',
                'company': 'Alphabet Inc.',
                'price': '$2,850.75',
                'change_amount': '-15.30',
                'change_percent': '0.53%',
                'is_positive': False
            }
        ]
    }

write_json_file('sample_news.json', news)