#%%
import os
from openai import OpenAI
from config import Config
from utils import logger, measure_time
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Test articles
articles = [
    {
        'headline': 'FED\'S GOOLSBEE: TARIFFS ARE A STAGFLATIONARY SHOCK',
        'content': 'Tweeter news account: DeItaone  FED\'S GOOLSBEE: TARIFFS ARE A STAGFLATIONARY SHOCK    — *Walter Bloomberg (@DeItaone)   Aug 13, 2025  Link to tweet: https://twitter.com/DeItaone/status/1955682776700813539  Tweeted at: August 13, 2025 at 08:28PM',
        'embedding': None
    },
    {
        'headline': "Federal Reserve's Goolsbee: Tariffs Pose a Stagflation Risk",
        'content': 'Tweeter news account: DeItaone  $AAPL - APPLE TO BOOST US INVESTMENT COMMITMENT BY $100B: WHITE HOUSE    — *Walter Bloomberg (@DeItaone)   Aug 6, 2025  Link to tweet: https://twitter.com/DeItaone/status/1953075233365152188  Tweeted at: August 06, 2025 at 03:46PM',
        'embedding': None
    },
    {
        'headline': 'TRUMP SIGNS EXECUTIVE ORDER IMPOSING ADDITIONAL 25% TARIFF ON INDIA',
        'content': 'Tweeter news account: DeItaone  🚨🚨 TRUMP SIGNS EXECUTIVE ORDER IMPOSING ADDITIONAL 25% TARIFF ON INDIA    — *Walter Bloomberg (@DeItaone)   Aug 6, 2025  Link to tweet: https://twitter.com/DeItaone/status/1953092800632795353  Tweeted at: August 06, 2025 at 04:56PM',
        'embedding': None
    }
]

KEY = Config.TOKENS.OPENAI_API_KEY
client = OpenAI(api_key=KEY)

# Prepare texts for batch processing
texts = [f"{article['headline']}" for article in articles]

@measure_time
def generate_batch_embeddings(texts):
    response = client.embeddings.create(
        model=Config.NEWS_PROCESSOR.EMBEDDING_MODEL,
        input=texts
    )
    return response.data

embeddings_data = generate_batch_embeddings(texts)

# Assign embeddings back to articles
for i, embedding_data in enumerate(embeddings_data):
    articles[i]['embedding'] = embedding_data.embedding

logger.info(f"✅ Batch embeddings generated: {len(articles)} articles")
for i, article in enumerate(articles):
    print(f"Article {i+1}: {len(article['embedding'])} dimensions, first 2 values: {article['embedding'][:2]}")

# %%

#%%

# Calculate similarities between all articles
embeddings = [article['embedding'] for article in articles]
similarity_matrix = cosine_similarity(embeddings)

print("Similarity Matrix:")
for i in range(len(articles)):
    for j in range(len(articles)):
        if i != j:
            similarity = similarity_matrix[i][j]
            print(f"Article {i+1} vs Article {j+1}: {similarity:.4f}")

#%%
# Search for similar articles to a query
query = "FED TARIFFS ECONOMIC POLICY"
query_embedding = client.embeddings.create(
    model=Config.NEWS_PROCESSOR.EMBEDDING_MODEL,
    input=[query]
).data[0].embedding

# Calculate similarities to query
query_similarities = cosine_similarity([query_embedding], embeddings)[0]

print(f"\nSearch Results for: '{query}'")
for i, similarity in enumerate(query_similarities):
    print(f"Article {i+1}: {similarity:.4f} - {articles[i]['headline']}")

#%%
# Find most similar pair
max_similarity = 0
most_similar_pair = None

for i in range(len(articles)):
    for j in range(i+1, len(articles)):
        similarity = similarity_matrix[i][j]
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_pair = (i, j)

print(f"\nMost Similar Pair:")
print(f"Article {most_similar_pair[0]+1} vs Article {most_similar_pair[1]+1}: {max_similarity:.4f}")
print(f"Article {most_similar_pair[0]+1}: {articles[most_similar_pair[0]]['headline']}")
print(f"Article {most_similar_pair[1]+1}: {articles[most_similar_pair[1]]['headline']}")
