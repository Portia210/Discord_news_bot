"""
Main pipeline orchestrator for the news processing pipeline.
Uses LangChain to connect all components in a modular workflow.
"""

import time
from typing import List, Dict, Any, Optional
from config import Config
from .data_loader import ArticleLoader
from .embeddings import EmbeddingManager
from .classifier import ImpactClassifier
from .clustering import ArticleClusterer
from .labeler import ClusterLabeler
from .summarizer import ClusterSummarizer
from .database import DatabaseManager

class PipelineResult:
    def __init__(self):
        self.articles = []
        self.clusters = []
        self.total_articles = 0
        self.total_clusters = 0
        self.processing_time = 0.0
        self.step_times = {}

class NewsProcessingPipeline:
    def __init__(self):
        Config.validate()
        self.data_loader = ArticleLoader()
        self.embedding_manager = EmbeddingManager()
        self.classifier = ImpactClassifier()
        self.clusterer = ArticleClusterer()
        self.labeler = ClusterLabeler()
        self.summarizer = ClusterSummarizer()
        self.database = DatabaseManager()

    def _preprocess_text(self, text: str) -> str:
        if not text:
            return ""
        
        text = text.lower()
        import re
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text

    def run_pipeline(self, articles_source: str = "sample") -> PipelineResult:
        start_time = time.time()
        result = PipelineResult()
        
        print("🚀 Starting news processing pipeline...")
        
        try:
            # Step 1: Load Articles
            step_start = time.time()
            print("📰 Loading articles...")
            
            if articles_source == "sample":
                articles = self.data_loader.load_sample_articles()
            elif articles_source == "messages":
                print("⚠️  Use load_from_messages() method directly for message lists")
                articles = self.data_loader.load_sample_articles()
            else:
                articles = self.data_loader.load_from_json(articles_source)
            
            result.step_times['loading'] = time.time() - step_start
            
            if not articles:
                print("⚠️  No articles to process")
                return result
            
            # Step 2: Generate Embeddings
            step_start = time.time()
            print("🔍 Generating embeddings...")
            
            for article in articles:
                processed_headline = self._preprocess_text(article['headline'])
                article['full_text'] = processed_headline
            
            articles_with_embeddings = self.embedding_manager.embed_articles(articles)
            result.step_times['embedding'] = time.time() - step_start
            
            # Step 3: Filter by Impact
            step_start = time.time()
            print("🎯 Filtering by impact...")
            filtered_articles = self.embedding_manager.filter_by_impact(articles_with_embeddings)
            result.step_times['filtering'] = time.time() - step_start
            
            # Step 4: Classify Articles
            step_start = time.time()
            print("📊 Classifying articles...")
            classified_articles = self.classifier.classify_articles(filtered_articles)
            result.step_times['classification'] = time.time() - step_start
            
            # Step 5: Cluster Articles
            step_start = time.time()
            print("🔗 Clustering articles...")
            clustered_articles = self.clusterer.cluster_articles(classified_articles)
            result.step_times['clustering'] = time.time() - step_start
            
            # Step 6: Label Clusters
            step_start = time.time()
            print("🏷️  Labeling clusters...")
            cluster_summary = self.clusterer.get_cluster_summary(clustered_articles)
            cluster_labels = self.labeler.label_clusters(clustered_articles, cluster_summary)
            result.step_times['labeling'] = time.time() - step_start
            
            # Step 7: Summarize Clusters
            step_start = time.time()
            print("📝 Summarizing clusters...")
            cluster_summaries = self.summarizer.summarize_all_clusters(
                clustered_articles, cluster_summary, cluster_labels
            )
            result.step_times['summarization'] = time.time() - step_start
            
            # Step 8: Store Results
            step_start = time.time()
            print("💾 Storing results...")
            stored_articles = self.database.store_articles(clustered_articles)
            stored_clusters = self.database.store_clusters(cluster_summary, cluster_labels, cluster_summaries)
            result.step_times['storage'] = time.time() - step_start
            
            # Update result
            result.articles = clustered_articles
            result.clusters = cluster_summaries
            result.total_articles = len(clustered_articles)
            result.total_clusters = len(cluster_summaries)
            result.processing_time = time.time() - start_time
            
            self._print_summary(result)
            
        except Exception as e:
            print(f"❌ Pipeline error: {e}")
            result.processing_time = time.time() - start_time
        
        return result

    def run_pipeline_with_messages(self, messages_list: List[Dict[str, Any]]) -> PipelineResult:
        start_time = time.time()
        result = PipelineResult()
        
        print("🚀 Starting news processing pipeline with Discord messages...")
        
        try:
            # Step 1: Load Articles from Messages
            step_start = time.time()
            print("📰 Loading articles from messages...")
            articles = self.data_loader.load_from_messages(messages_list)
            result.step_times['loading'] = time.time() - step_start
            
            if not articles:
                print("⚠️  No articles to process")
                return result
            
            # Continue with the rest of the pipeline...
            # Step 2: Generate Embeddings
            step_start = time.time()
            print("🔍 Generating embeddings...")
            
            for article in articles:
                processed_headline = self._preprocess_text(article['headline'])
                article['full_text'] = processed_headline
            
            articles_with_embeddings = self.embedding_manager.embed_articles(articles)
            result.step_times['embedding'] = time.time() - step_start
            
            # Step 3: Filter by Impact
            step_start = time.time()
            print("🎯 Filtering by impact...")
            filtered_articles = self.embedding_manager.filter_by_impact(articles_with_embeddings)
            result.step_times['filtering'] = time.time() - step_start
            
            # Step 4: Classify Articles
            step_start = time.time()
            print("📊 Classifying articles...")
            classified_articles = self.classifier.classify_articles(filtered_articles)
            result.step_times['classification'] = time.time() - step_start
            
            # Step 5: Cluster Articles
            step_start = time.time()
            print("🔗 Clustering articles...")
            clustered_articles = self.clusterer.cluster_articles(classified_articles)
            result.step_times['clustering'] = time.time() - step_start
            
            # Step 6: Label Clusters
            step_start = time.time()
            print("🏷️  Labeling clusters...")
            cluster_summary = self.clusterer.get_cluster_summary(clustered_articles)
            cluster_labels = self.labeler.label_clusters(clustered_articles, cluster_summary)
            result.step_times['labeling'] = time.time() - step_start
            
            # Step 7: Summarize Clusters
            step_start = time.time()
            print("📝 Summarizing clusters...")
            cluster_summaries = self.summarizer.summarize_all_clusters(
                clustered_articles, cluster_summary, cluster_labels
            )
            result.step_times['summarization'] = time.time() - step_start
            
            # Step 8: Store Results
            step_start = time.time()
            print("💾 Storing results...")
            stored_articles = self.database.store_articles(clustered_articles)
            stored_clusters = self.database.store_clusters(cluster_summary, cluster_labels, cluster_summaries)
            result.step_times['storage'] = time.time() - step_start
            
            # Update result
            result.articles = clustered_articles
            result.clusters = cluster_summaries
            result.total_articles = len(clustered_articles)
            result.total_clusters = len(cluster_summaries)
            result.processing_time = time.time() - start_time
            
            self._print_summary(result)
            
        except Exception as e:
            print(f"❌ Pipeline error: {e}")
            result.processing_time = time.time() - start_time
        
        return result

    def _print_summary(self, result: PipelineResult):
        print(f"\n✅ Pipeline completed in {result.processing_time:.2f}s")
        print(f"📊 Processed {result.total_articles} articles into {result.total_clusters} clusters")
        
        for step, time_taken in result.step_times.items():
            print(f"   {step}: {time_taken:.2f}s")

    def get_recent_results(self, limit: int = 50) -> Dict[str, Any]:
        articles = self.database.get_articles(limit)
        clusters = self.database.get_clusters()
        
        return {
            'articles': articles,
            'clusters': clusters,
            'total_articles': len(articles),
            'total_clusters': len(clusters)
        }
