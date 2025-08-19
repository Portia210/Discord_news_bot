#%%
import os
from openai import OpenAI
from config import Config
from utils import logger, measure_time
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import hdbscan
import spacy
from collections import Counter
from typing import List, Dict, Any, Optional
from bot.news_processor.discord_news_parser import DiscordNewsLoader
from utils import read_json_file
import json
from datetime import datetime

# Load spaCy model for NER
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("✅ spaCy model loaded successfully")
except OSError:
    logger.warning("⚠️ spaCy model not found. Please run: python -m spacy download en_core_web_sm")
    nlp = None

# Initialize OpenAI client
KEY = Config.TOKENS.OPENAI_API_KEY
client = OpenAI(api_key=KEY)

# Load sample data
messages_from_discord = read_json_file("messages_example.json")
articles = DiscordNewsLoader(None)._parse_messages_to_articles(messages_from_discord)

@measure_time
def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using OpenAI's embedding model.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of embedding vectors
    """
    logger.info(f"🔄 Generating embeddings for {len(texts)} texts...")
    
    response = client.embeddings.create(
        model=Config.NEWS_PROCESSOR.EMBEDDING_MODEL,
        input=texts
    )
    
    embeddings = [data.embedding for data in response.data]
    logger.info(f"✅ Generated {len(embeddings)} embeddings with {len(embeddings[0])} dimensions")
    
    return embeddings

@measure_time
def cluster_articles(embeddings: List[List[float]], min_cluster_size: int = None) -> hdbscan.HDBSCAN:
    """
    Cluster articles using HDBSCAN for automatic cluster detection.
    
    Args:
        embeddings: List of embedding vectors
        min_cluster_size: Minimum size for a cluster (defaults to config value)
        
    Returns:
        HDBSCAN clustering model with fitted results
    """
    if min_cluster_size is None:
        min_cluster_size = Config.NEWS_PROCESSOR.MIN_CLUSTER_SIZE
    
    logger.info(f"🔄 Clustering {len(embeddings)} articles with HDBSCAN (min_cluster_size={min_cluster_size})...")
    
    # Initialize HDBSCAN with parameters suitable for news clustering
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=1,  # Minimum points to form a core point
        metric='euclidean',  # Distance metric for embeddings
        cluster_selection_method='eom'  # Excess of Mass for cluster selection
    )
    
    # Fit the model
    cluster_labels = clusterer.fit_predict(embeddings)
    
    # Log clustering results
    n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
    n_noise = list(cluster_labels).count(-1)
    
    logger.info(f"✅ Clustering complete: {n_clusters} clusters, {n_noise} noise points")
    logger.info(f"📊 Cluster distribution: {dict(Counter(cluster_labels))}")
    
    return clusterer

def extract_cluster_entities(articles: List[Dict], cluster_labels: List[int]) -> Dict[int, Dict[str, Any]]:
    """
    Extract and aggregate named entities for each cluster using spaCy NER.
    
    Args:
        articles: List of article dictionaries
        cluster_labels: Cluster labels from HDBSCAN
        
    Returns:
        Dictionary mapping cluster_id to entity information
    """
    if nlp is None:
        logger.warning("⚠️ spaCy not available, skipping NER extraction")
        return {}
    
    logger.info("🔄 Extracting named entities for clusters...")
    
    # Entity types we're interested in
    entity_types = ['PERSON', 'ORG', 'GPE', 'EVENT']
    
    cluster_entities = {}
    
    for cluster_id in set(cluster_labels):
        if cluster_id == -1:  # Skip noise points
            continue
            
        # Get articles in this cluster
        cluster_articles = [
            article for i, article in enumerate(articles) 
            if cluster_labels[i] == cluster_id
        ]
        
        # Extract entities from all headlines in the cluster
        all_entities = []
        for article in cluster_articles:
            doc = nlp(article['headline'])
            entities = [(ent.text, ent.label_) for ent in doc.ents if ent.label_ in entity_types]
            all_entities.extend(entities)
        
        # Count entity frequencies
        entity_counts = Counter(all_entities)
        
        # Get top entities by type
        top_entities = {}
        for entity_type in entity_types:
            type_entities = [(text, label) for (text, label), count in entity_counts.most_common() 
                           if label == entity_type]
            if type_entities:
                top_entities[entity_type] = type_entities[:3]  # Top 3 per type
        
        # Create cluster label from most common entities
        most_common = entity_counts.most_common(5)
        cluster_label = " | ".join([f"{text} ({label})" for (text, label), count in most_common[:3]])
        
        cluster_entities[cluster_id] = {
            'label': cluster_label,
            'top_entities': top_entities,
            'entity_counts': dict(entity_counts),
            'article_count': len(cluster_articles)
        }
        
        logger.info(f"📋 Cluster {cluster_id}: {cluster_label} ({len(cluster_articles)} articles)")
    
    logger.info(f"✅ Entity extraction complete for {len(cluster_entities)} clusters")
    return cluster_entities

def export_clustering_results(articles: List[Dict], cluster_labels: List[int], 
                            cluster_entities: Dict[int, Dict[str, Any]], 
                            cluster_summaries: Dict[int, str] = None,
                            filename: str = None) -> str:
    """
    Export clustering results to a detailed text file.
    
    Args:
        articles: List of article dictionaries
        cluster_labels: Cluster labels from HDBSCAN
        cluster_entities: Entity information for each cluster
        cluster_summaries: Optional summaries for each cluster
        filename: Optional custom filename
        
    Returns:
        Path to the exported file
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"clustering_results_{timestamp}.txt"
    
    logger.info(f"🔄 Exporting clustering results to {filename}...")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("NEWS CLUSTERING RESULTS\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Articles: {len(articles)}\n")
        f.write(f"Total Clusters: {len(cluster_entities)}\n")
        f.write(f"Noise Points: {list(cluster_labels).count(-1)}\n\n")
        
        # Summary statistics
        f.write("CLUSTER SUMMARY\n")
        f.write("-" * 40 + "\n")
        for cluster_id in sorted(cluster_entities.keys()):
            entity_info = cluster_entities[cluster_id]
            f.write(f"Cluster {cluster_id}: {entity_info['article_count']} articles\n")
            f.write(f"  Label: {entity_info['label']}\n")
            if cluster_summaries and cluster_id in cluster_summaries:
                f.write(f"  Summary: {cluster_summaries[cluster_id]}\n")
            f.write("\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("DETAILED CLUSTER ANALYSIS\n")
        f.write("=" * 80 + "\n\n")
        
        # Detailed cluster information
        for cluster_id in sorted(cluster_entities.keys()):
            entity_info = cluster_entities[cluster_id]
            
            f.write(f"CLUSTER {cluster_id}\n")
            f.write("-" * 50 + "\n")
            f.write(f"Articles: {entity_info['article_count']}\n")
            f.write(f"Label: {entity_info['label']}\n")
            
            if cluster_summaries and cluster_id in cluster_summaries:
                f.write(f"Summary: {cluster_summaries[cluster_id]}\n")
            
            f.write("\nENTITIES BY TYPE:\n")
            for entity_type, entities in entity_info['top_entities'].items():
                if entities:
                    f.write(f"  {entity_type}:\n")
                    for text, label in entities:
                        count = entity_info['entity_counts'].get((text, label), 0)
                        f.write(f"    - {text} (count: {count})\n")
            
            f.write("\nARTICLES IN THIS CLUSTER:\n")
            for i, article in enumerate(articles):
                if cluster_labels[i] == cluster_id:
                    f.write(f"  {i+1}. {article['headline']}\n")
                    if 'url' in article:
                        f.write(f"     URL: {article['url']}\n")
                    if 'timestamp' in article:
                        f.write(f"     Time: {article['timestamp']}\n")
                    f.write("\n")
            
            f.write("\n" + "=" * 80 + "\n\n")
        
        # Noise points section
        noise_indices = [i for i, label in enumerate(cluster_labels) if label == -1]
        if noise_indices:
            f.write("NOISE POINTS (Unclustered Articles)\n")
            f.write("-" * 50 + "\n")
            for i, idx in enumerate(noise_indices):
                article = articles[idx]
                f.write(f"{i+1}. {article['headline']}\n")
                if 'url' in article:
                    f.write(f"   URL: {article['url']}\n")
                if 'timestamp' in article:
                    f.write(f"   Time: {article['timestamp']}\n")
                f.write("\n")
        
        # Entity frequency analysis
        f.write("\n" + "=" * 80 + "\n")
        f.write("GLOBAL ENTITY FREQUENCY ANALYSIS\n")
        f.write("=" * 80 + "\n\n")
        
        all_entities = []
        for cluster_id in cluster_entities:
            entity_info = cluster_entities[cluster_id]
            for (text, label), count in entity_info['entity_counts'].items():
                all_entities.extend([(text, label)] * count)
        
        global_entity_counts = Counter(all_entities)
        
        f.write("MOST FREQUENT ENTITIES ACROSS ALL CLUSTERS:\n")
        for (text, label), count in global_entity_counts.most_common(20):
            f.write(f"  {text} ({label}): {count} occurrences\n")
    
    logger.info(f"✅ Clustering results exported to {filename}")
    return filename

def summarize_cluster(articles: List[Dict], cluster_id: int, client: OpenAI, 
                     cluster_label: str = "") -> Optional[str]:
    """
    Generate a summary for a cluster using OpenAI's LLM.
    
    Args:
        articles: List of article dictionaries
        cluster_id: ID of the cluster to summarize
        client: OpenAI client instance
        cluster_label: Optional cluster label for context
        
    Returns:
        Generated summary or None if summarization fails
    """
    try:
        # Get headlines for this cluster
        headlines = [article['headline'] for article in articles]
        
        # Create prompt for summarization
        headlines_text = "\n".join([f"- {headline}" for headline in headlines])
        
        prompt = f"""Summarize the following news headlines in 1-2 sentences. 
Focus on the main theme or event they're reporting on.

Cluster context: {cluster_label}

Headlines:
{headlines_text}

Summary:"""

        response = client.chat.completions.create(
            model=Config.NEWS_PROCESSOR.SUMMARIZATION_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.3
        )
        
        summary = response.choices[0].message.content.strip()
        logger.info(f"📝 Generated summary for cluster {cluster_id}: {summary[:100]}...")
        return summary
        
    except Exception as e:
        logger.error(f"❌ Failed to summarize cluster {cluster_id}: {e}")
        return None

def analyze_cluster_similarities(embeddings: List[List[float]], cluster_labels: List[int]) -> None:
    """
    Analyze similarities within and between clusters.
    
    Args:
        embeddings: List of embedding vectors
        cluster_labels: Cluster labels from HDBSCAN
    """
    logger.info("🔄 Analyzing cluster similarities...")
    
    similarity_matrix = cosine_similarity(embeddings)
    
    # Calculate intra-cluster similarities
    for cluster_id in set(cluster_labels):
        if cluster_id == -1:  # Skip noise
            continue
            
        cluster_indices = [i for i, label in enumerate(cluster_labels) if label == cluster_id]
        
        if len(cluster_indices) < 2:
            continue
            
        # Calculate average similarity within cluster
        intra_similarities = []
        for i in cluster_indices:
            for j in cluster_indices:
                if i != j:
                    intra_similarities.append(similarity_matrix[i][j])
        
        avg_intra_similarity = np.mean(intra_similarities)
        logger.info(f"📊 Cluster {cluster_id} intra-similarity: {avg_intra_similarity:.4f}")

def main(enable_summarization: bool = True, min_cluster_size: int = None, export_results: bool = True):
    """
    Main function to run the complete news clustering pipeline.
    
    Args:
        enable_summarization: Whether to generate cluster summaries
        min_cluster_size: Minimum cluster size for HDBSCAN
        export_results: Whether to export results to file
    """
    logger.info("🚀 Starting news clustering pipeline...")
    
    # Prepare texts for embedding
    texts = [article['headline'] for article in articles]
    
    # Step 1: Generate embeddings
    embeddings = generate_embeddings(texts)
    
    # Assign embeddings back to articles
    for i, embedding in enumerate(embeddings):
        articles[i]['embedding'] = embedding
    
    # Step 2: Cluster articles
    clusterer = cluster_articles(embeddings, min_cluster_size)
    cluster_labels = clusterer.labels_
    
    # Step 3: Extract entities and create cluster labels
    cluster_entities = extract_cluster_entities(articles, cluster_labels)
    
    # Step 4: Optional summarization
    cluster_summaries = {}
    if enable_summarization:
        logger.info("🔄 Generating cluster summaries...")
        for cluster_id in cluster_entities:
            cluster_articles_subset = [
                article for i, article in enumerate(articles) 
                if cluster_labels[i] == cluster_id
            ]
            summary = summarize_cluster(
                cluster_articles_subset, 
                cluster_id, 
                client, 
                cluster_entities[cluster_id]['label']
            )
            if summary:
                cluster_summaries[cluster_id] = summary
    
    # Step 5: Export results to file
    if export_results:
        export_filename = export_clustering_results(
            articles, cluster_labels, cluster_entities, cluster_summaries
        )
        logger.info(f"📄 Results exported to: {export_filename}")
    
    # Step 6: Analyze similarities
    analyze_cluster_similarities(embeddings, cluster_labels)
    
    # Print final results summary
    logger.info("📋 Final clustering results:")
    for cluster_id in sorted(cluster_entities.keys()):
        entity_info = cluster_entities[cluster_id]
        print(f"\n🔸 Cluster {cluster_id} ({entity_info['article_count']} articles):")
        print(f"   Label: {entity_info['label']}")
        
        if cluster_id in cluster_summaries:
            print(f"   Summary: {cluster_summaries[cluster_id]}")
        
        # Show top entities by type
        for entity_type, entities in entity_info['top_entities'].items():
            if entities:
                entities_str = ", ".join([f"{text}" for text, label in entities])
                print(f"   {entity_type}: {entities_str}")
    
    # Show noise points
    noise_count = list(cluster_labels).count(-1)
    if noise_count > 0:
        print(f"\n🔸 Noise points ({noise_count} articles):")
        for i, label in enumerate(cluster_labels):
            if label == -1:
                print(f"   - {articles[i]['headline']}")
    
    logger.info("✅ News clustering pipeline completed successfully!")
    
    return {
        'clusterer': clusterer,
        'cluster_labels': cluster_labels,
        'cluster_entities': cluster_entities,
        'cluster_summaries': cluster_summaries,
        'articles': articles
    }

# Run the pipeline
if __name__ == "__main__":
    results = main(enable_summarization=True, export_results=True)
