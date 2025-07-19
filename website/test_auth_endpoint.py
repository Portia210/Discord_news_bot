#!/usr/bin/env python3
"""
Test script for the authenticated news data endpoint
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_TOKEN = "your-secret-token"  # Change this to match your environment variable
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def test_create_news_data():
    """Test creating news data for a specific date"""
    
    # Sample data similar to sample_news.json
    news_data = {
        "title": "דוח חדשות פיננסיות - בוקר",
        "report_title": "דוח חדשות בוקר",
        "report_subtitle": "עדכוני שוק ופיננסים אחרונים",
        "report_time": "morning",
        "generation_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "news_data": [
            {
                "time": "morning",
                "message": "הבוקר פורסמו נתוני ה-CPI בארצות הברית, והם היו גבוהים מהצפוי.",
                "link": "https://www.bloomberg.com/news/articles/cpi-data"
            },
            {
                "time": "noon",
                "message": "הנתונים האחרונים עוררו ציפיות כי ה-Fed יעלה את הריבית ב-0.25% בשבוע הבא.",
                "link": "https://www.reuters.com/markets/fed-rate-hike"
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
            }
        ]
    }
    
    # Test date
    test_date = "2025-07-19"
    
    print(f"🚀 Testing authenticated news data creation for date: {test_date}")
    print(f"📡 URL: {BASE_URL}/api/news-data/{test_date}")
    print(f"🔑 Using token: {API_TOKEN}")
    print("-" * 50)
    
    try:
        # Create news data
        response = requests.post(
            f"{BASE_URL}/api/news-report",
            headers=HEADERS,
            json=news_data
        )
        
        print(f"📤 Response Status: {response.status_code}")
        print(f"📤 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Success! News data created:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Test getting the rendered report
            print("\n" + "="*50)
            print("🔄 Testing report rendering...")
            
            report_response = requests.get(f"{BASE_URL}/news-report/{test_date}")
            if report_response.status_code == 200:
                print("✅ Successfully rendered news report")
                print(f"📄 Report length: {len(report_response.text)} characters")
                # Save the report to a file for inspection
                with open(f"test_report_{test_date}.html", "w", encoding="utf-8") as f:
                    f.write(report_response.text)
                print(f"💾 Report saved to: test_report_{test_date}.html")
            else:
                print(f"❌ Failed to render report: {report_response.status_code}")
                print(report_response.text)
                
        else:
            print("❌ Failed to create news data:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the Flask server is running on port 8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_unauthorized_access():
    """Test accessing the endpoint without authentication"""
    
    news_data = {"news_data": [{"time": "test", "message": "test"}]}
    
    print(f"\n🚫 Testing unauthorized access")
    print("-" * 50)
    
    try:
        # Try without auth header
        response = requests.post(
            f"{BASE_URL}/api/news-report",
            json=news_data
        )
        
        print(f"📤 Response Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Correctly rejected unauthorized access")
            print(response.json())
        else:
            print("❌ Should have rejected unauthorized access")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing Authenticated News Data Endpoint")
    print("=" * 60)
    
    # Test with authentication
    test_create_news_data()
    
    # Test without authentication
    test_unauthorized_access()
    
    print("\n" + "=" * 60)
    print("🏁 Testing completed!") 