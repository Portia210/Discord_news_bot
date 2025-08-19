#%%
"""
Test Pipeline - Step by Step
Testing the news processing pipeline components
"""

import importlib
import json

# Force reload modules to get latest changes
from . import config, embeddings
importlib.reload(config)
importlib.reload(embeddings)

from .config import Config
from .data_loader import ArticleLoader
from .embeddings import EmbeddingManager
from .classifier import ImpactClassifier


#%%
# Step 1: Test Configuration
print("🔧 Testing Configuration...")
try:
    Config.validate()
    print("✅ Configuration is valid")
except Exception as e:
    print(f"❌ Configuration error: {e}")

#%%
# Step 2: Test Data Loading
print("\n📰 Testing Data Loading...")
loader = ArticleLoader()
messages_list = json.load(open("messages_example.json", "r", encoding="utf-8"))
print(f"Loaded {len(messages_list)} messages")

# Parse all messages
articles = []
for message in messages_list:
    article = loader._parse_discord_message(message)
    if article:
        articles.append(article)

print(f"✅ Successfully parsed {len(articles)} articles")

#%%
# Step 3: Test Embedding Generation
print("\n🔍 Testing Embedding Generation...")
embedding_manager = EmbeddingManager()

try:
    embedded_articles = embedding_manager.embed_articles(articles)
    print(f"✅ Generated embeddings for {len(embedded_articles)} articles")
except Exception as e:
    print(f"❌ Embedding error: {e}")
    embedded_articles = articles

#%%
# Step 4: Test Impact Classification
print("\n📊 Impact Classification (Threshold: 0.25, Chunk Size: 20):")
print("-" * 80)

classifier = ImpactClassifier(impact_threshold=0.25, chunk_size=20)
classified_articles = classifier.classify_articles(embedded_articles)


print("\n📈 Article Classification Results:")
for i, article in enumerate(classified_articles, 1):
    try:
        vector_similarity = article.get('vector_similarity', 0)
        max_similarity = article.get('max_similarity', 0)
        boost_factor = article.get('boost_factor', 0)
        all_similarities = article.get('all_similarities', [])
        llm_rating = article.get('llm_rating', 0)
        headline = article['headline'][:60] + "..." if len(article['headline']) > 60 else article['headline']
        
        print(f"{i:2d}. Vector: {vector_similarity:.4f} (max: {max_similarity:.4f}, boost: {boost_factor:.3f}), LLM: {llm_rating:.3f} | {headline}")
        
        # Show boost details for articles with significant boosts
        if boost_factor > 1.1:
            above_threshold = [sim for sim in all_similarities if sim > 0.25]
            print(f"     🚀 Boost: {boost_factor:.3f} from {len(above_threshold)} similarities above 0.25")
            
    except Exception as e:
        print(f"{i:2d}. Error: {e} | {article['headline'][:60]}...")

#%%
# Step 5: Show High-Impact Articles Only
print("\n🏆 High-Impact Articles (Above 0.25 threshold):")
print("-" * 50)

high_impact = [a for a in classified_articles if a.get('vector_similarity', 0) >= 0.25]
for i, article in enumerate(high_impact, 1):
    vector_sim = article.get('vector_similarity', 0)
    max_sim = article.get('max_similarity', 0)
    boost = article.get('boost_factor', 0)
    llm_rating = article.get('llm_rating', 0)
    headline = article['headline'][:50] + "..." if len(article['headline']) > 50 else article['headline']
    
    boost_info = f" (boost: {boost:.3f})" if boost > 1.0 else ""
    print(f"{i}. Vector: {vector_sim:.4f} (max: {max_sim:.4f}{boost_info}), LLM: {llm_rating:.3f} | {headline}")

#%%
# Step 6: Show Statistics
print("\n📊 Classification Statistics:")
print("-" * 30)
total_articles = len(classified_articles)
high_impact_count = len(high_impact)
avg_vector_sim = sum(a.get('vector_similarity', 0) for a in classified_articles) / total_articles
avg_llm_rating = sum(a.get('llm_rating', 0) for a in classified_articles) / total_articles

print(f"Total Articles: {total_articles}")
print(f"High-Impact Articles: {high_impact_count} ({high_impact_count/total_articles*100:.1f}%)")
print(f"Average Vector Similarity: {avg_vector_sim:.4f}")
print(f"Average LLM Rating: {avg_llm_rating:.3f}")

#%%
print("\n🎉 Testing Complete!")
