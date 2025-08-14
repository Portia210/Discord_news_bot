# News Processor

A comprehensive news processing pipeline that loads pre-filtered articles, creates embeddings, deduplicates similar articles, clusters them using HDBSCAN, and generates AI-powered summaries.

## Features

- **Article Parsing**: Automatically parses news text into structured articles
- **Embedding Generation**: Creates numerical "meaning fingerprints" using OpenAI embeddings
- **Deduplication**: Removes similar articles based on semantic similarity
- **Clustering**: Groups related articles using HDBSCAN algorithm
- **AI Summarization**: Generates polished cluster summaries using OpenAI
- **Database Storage**: Saves results to SQLAlchemy database
- **Configurable**: Easy configuration through config.py

## Architecture

```
news_processor/
├── __init__.py              # Package initialization
├── models.py                # Data models (NewsArticle, NewsCluster, NewsDigest)
├── embedding_service.py     # OpenAI embedding generation
├── deduplicator.py          # Article deduplication logic
├── clustering.py            # HDBSCAN clustering service
├── summarizer.py            # OpenAI summarization service
├── processor.py             # Main orchestration class
├── main.py                  # Example usage script
└── README.md               # This file
```

## Components

### 1. EmbeddingService
- Generates embeddings using OpenAI's text-embedding-3-small model
- Fallback to local sentence-transformers model if OpenAI unavailable
- Calculates cosine similarity between embeddings

### 2. Deduplicator
- Removes duplicate articles based on semantic similarity
- Configurable similarity threshold (default: 0.85)
- Keeps the most important article from each duplicate group

### 3. ClusteringService
- Uses HDBSCAN for density-based clustering
- Handles noise points by creating individual clusters
- Merges article content and tags within clusters

### 4. Summarizer
- Generates cluster summaries using OpenAI GPT models
- Extracts relevant tags and importance scores
- Handles parsing errors gracefully

### 5. NewsProcessor
- Main orchestration class
- Coordinates the entire pipeline
- Handles database persistence

## Configuration

Configuration is managed through `config.py`:

```python
class NewsProcessorConfig:
    EMBEDDING_MODEL = "text-embedding-3-small"
    SUMMARIZATION_MODEL = "gpt-4o-mini"
    SIMILARITY_THRESHOLD = 0.85
    MIN_CLUSTER_SIZE = 2
    TOP_N_CLUSTERS = 10
```

## Usage

### Basic Usage

```python
from news_processor import NewsProcessor

# Initialize processor
processor = NewsProcessor()

# Process news text
with open('news.txt', 'r') as f:
    news_text = f.read()

digest = processor.process_news_text(news_text)

# Print results
for cluster in digest.clusters:
    print(f"Summary: {cluster.summary}")
    print(f"Importance: {cluster.importance_score}")
    print(f"Tags: {cluster.tags}")
    print(f"Articles: {len(cluster.articles)}")
```

### With Database Storage

```python
from db.engine import SessionLocal

# Process and save to database
db = SessionLocal()
try:
    processor.save_to_database(digest, db)
finally:
    db.close()
```

## Database Models

### NewsArticle
- `id`: Primary key
- `headline`: Article headline
- `summary`: Article summary
- `content`: Full article content
- `tags`: JSON array of tags
- `importance_score`: Numeric importance (0.0-1.0)
- `source`: News source
- `url`: Article URL
- `timestamp`: Publication timestamp
- `embedding`: JSON array of embedding vector
- `cluster_id`: Foreign key to cluster

### NewsCluster
- `id`: Primary key
- `summary`: AI-generated cluster summary
- `tags`: JSON array of cluster tags
- `importance_score`: Cluster importance score
- `merged_content`: Combined content from all articles
- `cluster_size`: Number of articles in cluster

### NewsTest (Test Model)
- `id`: Primary key
- `test_name`: Name of the test
- `test_data`: Sample data used for testing
- `test_config`: JSON configuration used
- `success`: Whether the test passed
- `error_message`: Error message if failed
- `processing_time`: Time taken for processing
- `articles_processed`: Number of articles processed
- `clusters_created`: Number of clusters created

### NewsProcessingLog (Test Model)
- `id`: Primary key
- `run_id`: Unique identifier for processing run
- `status`: Current status ('started', 'in_progress', 'completed', 'failed')
- `step`: Current processing step
- `articles_count`: Number of articles at this step
- `clusters_count`: Number of clusters at this step
- `processing_time`: Time taken for this step
- `config_used`: JSON configuration used
- `error_message`: Error message if failed

## Dependencies

Add these to your requirements.txt:

```
numpy==1.24.3
scikit-learn==1.3.0
hdbscan==0.8.33
sentence-transformers==2.2.2
openai==1.93.0
```

## Environment Variables

Required:
- `OPENAI_API_KEY`: Your OpenAI API key

## Testing

### Basic Test
Run the basic test script to verify setup:

```bash
python test_news_processor.py
```

### Database Integration Test
Run the database integration test:

```bash
python test_news_db.py
```

### Database Setup
Setup the database tables:

```bash
python setup_news_db.py
```

## Example Output

```
================================================================================
NEWS DIGEST - 2025-01-27 10:30:15
Total Articles: 45
Top Clusters: 10
================================================================================

1. CLUSTER (Importance: 0.92)
   Size: 8 articles
   Tags: ['Trump', 'Russia', 'Ukraine', 'Peace Talks']
   Summary: President Trump and Russian President Putin are planning to meet next week to discuss Ukraine peace negotiations, with reports indicating progress toward a ceasefire agreement.
   Articles:
     - TRUMP TO MEET PUTIN NEXT WEEK FOR UKRAINE TALKS
     - PUTIN OFFERS CEASE-FIRE IN UKRAINE FOR EASTERN TERRITORY
     - TRUMP: WE ARE GETTING VERY CLOSE ON UKRAINE
     - ...
--------------------------------------------------------------------------------
```

## Pipeline Flow

1. **Load & Parse**: Parse news text into structured articles
2. **Embed**: Generate embeddings for each article
3. **Deduplicate**: Remove similar articles
4. **Cluster**: Group related articles using HDBSCAN
5. **Summarize**: Generate AI summaries for each cluster
6. **Rank**: Sort clusters by importance
7. **Select**: Choose top N clusters for digest
8. **Store**: Save results to database (optional)
