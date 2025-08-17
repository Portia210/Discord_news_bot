#%%
import json
import sqlite3
from openai import OpenAI
from config import Config
from utils.logger import logger
import numpy as np

# Load articles from JSON file
with open('news_processor/articles.json', 'r', encoding='utf-8') as f:
    articles = json.load(f)

logger.info(f"Loaded {len(articles)} articles from JSON")

# Extract headlines
headlines = [article['headline'] for article in articles]
logger.info(f"Extracted {len(headlines)} headlines")

# Generate embeddings
KEY = Config.TOKENS.OPENAI_API_KEY
client = OpenAI(api_key=KEY)

logger.info("Generating embeddings...")
response = client.embeddings.create(
    model=Config.NEWS_PROCESSOR.EMBEDDING_MODEL,
    input=headlines
)

# Create SQLite database
conn = sqlite3.connect('test_embeddings.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        headline TEXT NOT NULL,
        embedding BLOB NOT NULL
    )
''')

# Insert articles with embeddings
for i, (headline, embedding_data) in enumerate(zip(headlines, response.data)):
    embedding_array = np.array(embedding_data.embedding, dtype=np.float32)
    embedding_blob = embedding_array.tobytes()
    
    cursor.execute(
        'INSERT INTO articles (headline, embedding) VALUES (?, ?)',
        (headline, embedding_blob)
    )
    
    if (i + 1) % 10 == 0:
        logger.info(f"Processed {i + 1}/{len(headlines)} articles")

conn.commit()
conn.close()

logger.info(f"✅ Successfully stored {len(headlines)} articles with embeddings in test_embeddings.db")
