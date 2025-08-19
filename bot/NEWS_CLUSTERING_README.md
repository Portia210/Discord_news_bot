# News Clustering Pipeline

A modular, clean pipeline for clustering news articles using embeddings, HDBSCAN clustering, NER labeling, and optional summarization.

## Features

- **Embedding Generation**: Uses OpenAI's text-embedding-3-small model
- **Automatic Clustering**: HDBSCAN for automatic cluster detection (no need to specify number of clusters)
- **NER Labeling**: spaCy-based named entity recognition to create meaningful cluster labels
- **Optional Summarization**: LLM-powered summaries for each cluster
- **Modular Design**: Clean, extensible functions for each pipeline step

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Download spaCy Model**:
   ```bash
   python setup_spacy.py
   # Or manually:
   python -m spacy download en_core_web_sm
   ```

3. **Configure Environment**:
   Ensure your `.env` file has the required OpenAI API key.

## Usage

### Basic Usage
```python
from test_embedding import main

# Run the complete pipeline
results = main(enable_summarization=True)
```

### Advanced Usage
```python
from test_embedding import main, generate_embeddings, cluster_articles, extract_cluster_entities

# Run individual steps
embeddings = generate_embeddings(texts)
clusterer = cluster_articles(embeddings, min_cluster_size=3)
cluster_entities = extract_cluster_entities(articles, clusterer.labels_)
```

## Pipeline Functions

### `generate_embeddings(texts: List[str]) -> List[List[float]]`
Generates embeddings for a list of texts using OpenAI's embedding model.

### `cluster_articles(embeddings: List[List[float]], min_cluster_size: int = None) -> hdbscan.HDBSCAN`
Clusters articles using HDBSCAN for automatic cluster detection.

### `extract_cluster_entities(articles: List[Dict], cluster_labels: List[int]) -> Dict[int, Dict[str, Any]]`
Extracts and aggregates named entities (PERSON, ORG, GPE, EVENT) for each cluster.

### `summarize_cluster(articles: List[Dict], cluster_id: int, client: OpenAI, cluster_label: str = "") -> Optional[str]`
Generates a summary for a cluster using OpenAI's LLM.

### `main(enable_summarization: bool = True, min_cluster_size: int = None) -> Dict`
Runs the complete pipeline and returns all results.

## Configuration

Key configuration options in `config.py`:

```python
class NewsProcessorConfig:
    EMBEDDING_MODEL = "text-embedding-3-small"
    SUMMARIZATION_MODEL = "gpt-4o-mini"
    MIN_CLUSTER_SIZE = 2
```

## Output

The pipeline returns a dictionary with:
- `clusterer`: HDBSCAN model with fitted results
- `cluster_labels`: Cluster assignments for each article
- `cluster_entities`: Entity information for each cluster
- `cluster_summaries`: Generated summaries (if enabled)
- `articles`: Original articles with embeddings added

## Example Output

```
🔸 Cluster 0 (3 articles):
   Label: Apple (ORG) | iPhone (EVENT) | Tim Cook (PERSON)
   Summary: Apple's latest iPhone launch and Tim Cook's announcements
   PERSON: Tim Cook, Steve Jobs
   ORG: Apple, Apple Inc
   EVENT: iPhone launch, WWDC

🔸 Cluster 1 (2 articles):
   Label: Tesla (ORG) | Elon Musk (PERSON) | Stock (EVENT)
   Summary: Tesla stock movements and Elon Musk's latest statements
   PERSON: Elon Musk
   ORG: Tesla, SpaceX
```

## Extending the Pipeline

The modular design makes it easy to add new features:

1. **New Entity Types**: Modify `entity_types` in `extract_cluster_entities()`
2. **Different Clustering**: Replace HDBSCAN with other algorithms
3. **Custom Summarization**: Modify the prompt in `summarize_cluster()`
4. **Additional Analysis**: Add new functions and call them in `main()`

## Troubleshooting

- **spaCy Model Not Found**: Run `python setup_spacy.py`
- **OpenAI API Errors**: Check your API key and rate limits
- **Memory Issues**: Reduce batch size or use smaller embedding model
