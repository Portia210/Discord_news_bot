"""
Test Pipeline - Step by Step
Testing the news processing pipeline components
"""

import json
from .config import Config
from .data_loader import ArticleLoader
from .embeddings import EmbeddingManager
from .classifier import ImpactClassifier
from .clustering import ArticleClusterer


def test_configuration():
    """Test configuration validation"""
    print("🔧 Testing Configuration...")
    try:
        Config.validate()
        print("✅ Configuration is valid")
    except Exception as e:
        print(f"❌ Configuration error: {e}")


def test_data_loading():
    """Test data loading and parsing"""
    print("\n📰 Testing Data Loading...")
    loader = ArticleLoader()
    messages_list = json.load(open("messages_example.json", "r", encoding="utf-8"))
    print(f"Loaded {len(messages_list)} messages")

    articles = []
    for message in messages_list:
        article = loader._parse_discord_message(message)
        if article:
            articles.append(article)

    print(f"✅ Successfully parsed {len(articles)} articles")
    return articles


def test_embedding_generation(articles):
    """Test embedding generation"""
    print("\n🔍 Testing Embedding Generation...")
    embedding_manager = EmbeddingManager()

    try:
        embedded_articles = embedding_manager.embed_articles(articles)
        print(f"✅ Generated embeddings for {len(embedded_articles)} articles")
        return embedded_articles
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return articles


def test_impact_classification(embedded_articles):
    """Test impact classification"""
    print("\n📊 Impact Classification (Threshold: 0.15, Chunk Size: 20):")
    print("-" * 80)

    classifier = ImpactClassifier(impact_threshold=0.15, chunk_size=20)
    classified_articles = classifier.classify_articles(embedded_articles)

    print("\n📈 Article Classification Results:")
    print("=" * 100)
    
    for i, article in enumerate(classified_articles, 1):
        try:
            vector_similarity = article.get('vector_similarity', 0)
            economic_sim = article.get('economic_similarity', 0)
            positive_sim = article.get('positive_similarity', 0)
            negative_sim = article.get('negative_similarity', 0)
            neutral_sim = article.get('neutral_similarity', 0)
            llm_rating = article.get('llm_rating', 0)
            headline = article['headline'][:80] + "..." if len(article['headline']) > 80 else article['headline']
            
            if positive_sim > negative_sim and positive_sim > neutral_sim:
                sentiment = "POS"
            elif negative_sim > positive_sim and negative_sim > neutral_sim:
                sentiment = "NEG"
            elif neutral_sim > positive_sim and neutral_sim > negative_sim:
                sentiment = "NEU"
            else:
                sentiment = "MIX"
            
            print(f"\n{i:2d}. {headline}")
            print(f"    Final Score: {llm_rating:.4f} | Sentiment: {sentiment} | Vector Similarity: {vector_similarity:.4f}")
            print(f"    Centroids: Econ={economic_sim:.4f} | Pos={positive_sim:.4f} | Neg={negative_sim:.4f} | Neu={neutral_sim:.4f}")
            
            centroids = [
                ("Economic", economic_sim),
                ("Positive", positive_sim),
                ("Negative", negative_sim),
                ("Neutral", neutral_sim)
            ]
            strongest = max(centroids, key=lambda x: x[1])
            print(f"    Strongest: {strongest[0]} ({strongest[1]:.4f})")
            
            if economic_sim >= 0.15:
                print(f"    ✅ Economic threshold PASSED ({economic_sim:.4f} >= 0.15)")
            else:
                print(f"    ❌ Economic threshold FAILED ({economic_sim:.4f} < 0.15)")
                
            if sentiment == "NEU":
                print(f"    ⚠️  SKIPPED: Closest to neutral sentiment")
                
        except Exception as e:
            print(f"{i:2d}. Error: {e} | {article['headline'][:60]}...")
    
    return classified_articles


def test_clustering(classified_articles):
    """Test article clustering"""
    print("\n🔗 Testing Article Clustering...")
    print("-" * 80)

    clusterer = ArticleClusterer(min_cluster_size=2)
    clustered_articles = clusterer.cluster_articles(classified_articles)

    print(f"✅ Clustered {len(clustered_articles)} articles using HDBSCAN")
    
    # Show clustering results
    print("\n📊 Clustering Results:")
    print("=" * 60)
    
    cluster_summary = clusterer.get_cluster_summary(clustered_articles)
    noise_articles = clusterer.get_noise_articles(clustered_articles)
    
    print(f"Total Clusters: {len([k for k in cluster_summary.keys() if k != -1])}")
    print(f"Noise Articles: {len(noise_articles)}")
    
    # Group articles by cluster
    cluster_groups = {}
    for article in clustered_articles:
        cluster_id = article.get('cluster_id', -1)
        if cluster_id not in cluster_groups:
            cluster_groups[cluster_id] = []
        cluster_groups[cluster_id].append(article)
    
    # Show each cluster with all articles
    for cluster_id in sorted(cluster_groups.keys()):
        if cluster_id == -1:
            continue
            
        articles_in_cluster = cluster_groups[cluster_id]
        summary = cluster_summary[cluster_id]
        
        print(f"\n🔸 Cluster {cluster_id} ({len(articles_in_cluster)} articles):")
        print(f"   Avg Impact Score: {summary['avg_impact_score']:.4f}")
        print(f"   Sources: {', '.join(summary['sources'][:3])}{'...' if len(summary['sources']) > 3 else ''}")
        print(f"   Articles in this cluster:")
        
        # Sort articles by impact score (highest first)
        sorted_articles = sorted(articles_in_cluster, key=lambda x: x.get('llm_rating', 0), reverse=True)
        
        for i, article in enumerate(sorted_articles, 1):
            headline = article['headline'][:70] + "..." if len(article['headline']) > 70 else article['headline']
            score = article.get('llm_rating', 0)
            economic_sim = article.get('economic_similarity', 0)
            positive_sim = article.get('positive_similarity', 0)
            negative_sim = article.get('negative_similarity', 0)
            
            # Determine sentiment
            if positive_sim > negative_sim:
                sentiment = "POS"
            else:
                sentiment = "NEG"
            
            print(f"   {i:2d}. [{score:.3f}] {sentiment} | Econ:{economic_sim:.3f} | {headline}")
    
    # Show noise articles
    if noise_articles:
        print(f"\n🔸 Noise Articles ({len(noise_articles)}):")
        for i, article in enumerate(noise_articles, 1):
            headline = article['headline'][:70] + "..." if len(article['headline']) > 70 else article['headline']
            score = article.get('llm_rating', 0)
            economic_sim = article.get('economic_similarity', 0)
            print(f"   {i:2d}. [{score:.3f}] Econ:{economic_sim:.3f} | {headline}")
    
    return clustered_articles


def show_high_impact_articles(classified_articles):
    """Show high-impact articles summary"""
    print("\n🏆 High-Impact Articles (Above 0.15 threshold):")
    print("=" * 80)

    high_impact = [a for a in classified_articles if a.get('llm_rating', 0) >= 0.15]
    for i, article in enumerate(high_impact, 1):
        vector_sim = article.get('vector_similarity', 0)
        economic_sim = article.get('economic_similarity', 0)
        positive_sim = article.get('positive_similarity', 0)
        negative_sim = article.get('negative_similarity', 0)
        neutral_sim = article.get('neutral_similarity', 0)
        sentiment_score = article.get('sentiment_score', 0)
        llm_rating = article.get('llm_rating', 0)
        headline = article['headline'][:70] + "..." if len(article['headline']) > 70 else article['headline']
        
        if positive_sim > negative_sim and positive_sim > neutral_sim:
            sentiment = "POS"
        elif negative_sim > positive_sim and negative_sim > neutral_sim:
            sentiment = "NEG"
        elif neutral_sim > positive_sim and neutral_sim > negative_sim:
            sentiment = "NEU"
        else:
            sentiment = "MIX"
        
        print(f"\n{i}. {headline}")
        print(f"   Score: {llm_rating:.4f} | Sentiment: {sentiment} | Econ: {economic_sim:.4f}")
        print(f"   Centroids: Pos={positive_sim:.4f} | Neg={negative_sim:.4f} | Neu={neutral_sim:.4f} | Sent={sentiment_score:.4f}")
    return high_impact


def show_statistics(classified_articles):
    """Show classification statistics"""
    print("\n📊 Classification Statistics:")
    print("-" * 30)
    total_articles = len(classified_articles)
    high_impact_count = len([a for a in classified_articles if a.get('llm_rating', 0) >= 0.15])
    avg_vector_sim = sum(a.get('vector_similarity', 0) for a in classified_articles) / total_articles
    avg_llm_rating = sum(a.get('llm_rating', 0) for a in classified_articles) / total_articles

    print(f"Total Articles: {total_articles}")
    print(f"High-Impact Articles: {high_impact_count} ({high_impact_count/total_articles*100:.1f}%)")
    print(f"Average Vector Similarity: {avg_vector_sim:.4f}")
    print(f"Average LLM Rating: {avg_llm_rating:.3f}")

    print("\n🎯 Centroid Analysis:")
    print("-" * 20)
    economic_scores = [a.get('economic_similarity', 0) for a in classified_articles]
    positive_scores = [a.get('positive_similarity', 0) for a in classified_articles]
    negative_scores = [a.get('negative_similarity', 0) for a in classified_articles]
    neutral_scores = [a.get('neutral_similarity', 0) for a in classified_articles]

    print(f"Avg Economic Similarity: {sum(economic_scores)/len(economic_scores):.4f}")
    print(f"Avg Positive Similarity: {sum(positive_scores)/len(positive_scores):.4f}")
    print(f"Avg Negative Similarity: {sum(negative_scores)/len(negative_scores):.4f}")
    print(f"Avg Neutral Similarity: {sum(neutral_scores)/len(neutral_scores):.4f}")

    sentiment_counts = {"POS": 0, "NEG": 0, "NEU": 0, "MIX": 0}
    for article in classified_articles:
        economic_sim = article.get('economic_similarity', 0)
        positive_sim = article.get('positive_similarity', 0)
        negative_sim = article.get('negative_similarity', 0)
        neutral_sim = article.get('neutral_similarity', 0)
        
        if positive_sim > negative_sim and positive_sim > neutral_sim:
            sentiment_counts["POS"] += 1
        elif negative_sim > positive_sim and negative_sim > neutral_sim:
            sentiment_counts["NEG"] += 1
        elif neutral_sim > positive_sim and neutral_sim > negative_sim:
            sentiment_counts["NEU"] += 1
        else:
            sentiment_counts["MIX"] += 1

    print(f"\nSentiment Distribution:")
    print(f"Positive: {sentiment_counts['POS']} ({sentiment_counts['POS']/total_articles*100:.1f}%)")
    print(f"Negative: {sentiment_counts['NEG']} ({sentiment_counts['NEG']/total_articles*100:.1f}%)")
    print(f"Neutral: {sentiment_counts['NEU']} ({sentiment_counts['NEU']/total_articles*100:.1f}%)")
    print(f"Mixed: {sentiment_counts['MIX']} ({sentiment_counts['MIX']/total_articles*100:.1f}%)")


def main():
    """Main test pipeline execution"""
    test_configuration()
    articles = test_data_loading()
    embedded_articles = test_embedding_generation(articles)
    classified_articles = test_impact_classification(embedded_articles)
    high_impact_articles = show_high_impact_articles(classified_articles)
    clustered_articles = test_clustering(high_impact_articles)
    # show_statistics(classified_articles)
    print("\n🎉 Testing Complete!")


if __name__ == "__main__":
    main()
