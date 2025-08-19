# News Processing Pipeline v1.0

A comprehensive news processing pipeline that filters, clusters, and summarizes market-impacting news articles using LangChain, OpenAI, and HDBSCAN.

## 🎯 Overview

This pipeline implements the hybrid approach outlined in `plan.md`:

1. **Load Articles** - From various sources (JSON, sample data)
2. **Hybrid Impact Filter** - Embedding similarity + optional OpenAI classification
3. **Generate Embeddings** - Using OpenAI's text-embedding-3-small
4. **Dynamic Clustering** - HDBSCAN for topic-based clustering
5. **Lightweight Labeling** - spaCy NER for cluster labels
6. **Cluster Summarization** - OpenAI LLM for concise summaries
7. **Database Storage** - SQLite with SQLAlchemy
8. **LangChain Orchestration** - Modular, testable workflow

## 📁 Project Structure

```
pipe_line_v1/
├── config.py              # Configuration and environment variables
├── data_loader.py         # Article loading and preprocessing
├── embeddings.py          # OpenAI embeddings and similarity
├── classifier.py          # Impact classification with OpenAI
├── clustering.py          # HDBSCAN clustering
├── labeler.py            # spaCy NER labeling
├── summarizer.py         # OpenAI LLM summarization
├── database.py           # SQLAlchemy database operations
├── pipeline.py           # Main orchestrator using LangChain
├── main.py               # Entry point and examples
├── requirements.txt      # Dependencies
├── env_example.txt       # Environment variables template
└── README.md            # This file
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Copy environment template and add your API key
cp env_example.txt .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Run the Pipeline

```bash
# Run with sample articles
python main.py

# Run with specific source
python main.py sample
python main.py json
python main.py path/to/articles.json
```

## 🔧 Configuration

Create a `.env` file with:

```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///news_pipeline.db
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o-mini
SIMILARITY_THRESHOLD=0.7
IMPACT_SCORE_THRESHOLD=6.0
MIN_CLUSTER_SIZE=2
```

## 📊 Pipeline Flow

### Step 1: Data Loading
- Supports JSON files, sample data, and custom formats
- Preprocesses articles for consistent structure
- Handles different article formats automatically

### Step 2: Hybrid Impact Filtering
1. **Embedding Pre-filter**: Cosine similarity vs high-impact reference
2. **OpenAI Classification**: Optional scoring for borderline cases
3. **Threshold Filtering**: Keep articles above impact thresholds

### Step 3: Embedding Generation
- Uses OpenAI's `text-embedding-3-small` model
- Generates embeddings for all article text
- Stores embeddings for clustering

### Step 4: Dynamic Clustering
- HDBSCAN algorithm for topic-based clustering
- Configurable minimum cluster size
- Handles noise points (unclustered articles)

### Step 5: Cluster Labeling
- spaCy NER for named entity extraction
- Creates lightweight labels from most common entities
- Fallback to headline keywords if needed

### Step 6: Summarization
- OpenAI LLM for cluster summaries
- Chunks large clusters to prevent token overflow
- Creates overall market summary

### Step 7: Database Storage
- SQLite database with SQLAlchemy ORM
- Stores articles, clusters, embeddings, and metadata
- Supports updates and retrieval

## 🎯 Usage Examples

### Basic Pipeline Execution

```python
from pipeline import NewsProcessingPipeline

# Initialize pipeline
pipeline = NewsProcessingPipeline()

# Run with sample articles
result = pipeline.run_pipeline("sample")

# Access results
print(f"Processed {result.stats['total_articles']} articles")
print(f"Created {result.stats['clusters_created']} clusters")
print(f"Market summary: {result.market_summary}")
```

### Custom Article Processing

```python
from data_loader import ArticleLoader
from embeddings import EmbeddingManager

# Load custom articles
loader = ArticleLoader()
articles = loader.load_from_json("my_articles.json")

# Generate embeddings
embedding_manager = EmbeddingManager()
articles_with_embeddings = embedding_manager.embed_articles(articles)

# Filter by impact
filtered_articles = embedding_manager.filter_by_impact(articles_with_embeddings)
```

### Database Operations

```python
from database import DatabaseManager

# Initialize database
db = DatabaseManager()

# Store articles
stored_count = db.store_articles(articles)

# Retrieve recent results
recent_articles = db.get_articles(limit=50)
recent_clusters = db.get_clusters()
```

## 🔍 Key Features

### Hybrid Filtering
- **Fast pre-filtering** with embeddings (cosine similarity)
- **Accurate classification** with OpenAI for borderline cases
- **Configurable thresholds** for different use cases

### Dynamic Clustering
- **HDBSCAN algorithm** for robust topic clustering
- **Noise handling** for outlier articles
- **Cluster confidence** scoring

### Intelligent Labeling
- **spaCy NER** for named entity extraction
- **Entity frequency** analysis for meaningful labels
- **Fallback mechanisms** for edge cases

### LangChain Integration
- **Modular design** with clear separation of concerns
- **Easy testing** and debugging
- **Extensible architecture** for future enhancements

## 📈 Performance

- **Processing speed**: ~2-5 seconds per article (including API calls)
- **Memory usage**: Efficient embedding storage and retrieval
- **Scalability**: Modular design supports horizontal scaling
- **Cost optimization**: Hybrid filtering reduces unnecessary API calls

## 🛠️ Customization

### Adding New Data Sources

```python
# Extend ArticleLoader class
class CustomArticleLoader(ArticleLoader):
    def load_from_custom_source(self, source_path):
        # Implement custom loading logic
        pass
```

### Custom Impact Scoring

```python
# Extend ImpactClassifier class
class CustomImpactClassifier(ImpactClassifier):
    def custom_scoring_method(self, article):
        # Implement custom scoring logic
        pass
```

### Database Extensions

```python
# Add new models to database.py
class CustomModel(Base):
    __tablename__ = 'custom_table'
    # Define your schema
```

## 🐛 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure `.env` file exists with correct API key
   - Check API key permissions and billing

2. **spaCy Model Not Found**
   - Run: `python -m spacy download en_core_web_sm`
   - Verify model installation: `python -c "import spacy; spacy.load('en_core_web_sm')"`

3. **Database Errors**
   - Check SQLite file permissions
   - Ensure database directory is writable

4. **Memory Issues**
   - Reduce batch sizes in embedding generation
   - Process articles in smaller chunks

### Debug Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run pipeline with debug info
pipeline = NewsProcessingPipeline()
result = pipeline.run_pipeline("sample")
```

## 📝 License

This project is part of the Discord Bot project and follows the same licensing terms.

## 🤝 Contributing

1. Follow the modular design principles
2. Add comprehensive docstrings
3. Include error handling
4. Test with different article formats
5. Update documentation for new features
