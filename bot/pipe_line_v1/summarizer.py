"""
Summarizer module for the news processing pipeline.
Handles cluster summarization using OpenAI LLM.
"""

from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from .config import Config

class ClusterSummarizer:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=Config.LLM_MODEL, 
            openai_api_key=Config.OPENAI_API_KEY, 
            temperature=0.3
        )
        self.summary_template = ChatPromptTemplate.from_template(
            """Summarize these related news articles into a concise, human-readable market summary:
            Articles: {articles_text}
            Provide a clear, factual summary in 2-3 sentences:"""
        )

    def summarize_cluster(self, articles: List[Dict[str, Any]], cluster_label: str = "") -> str:
        articles_text = self._prepare_articles_text(articles)
        
        try:
            response = self.llm.invoke(
                self.summary_template.format(articles_text=articles_text)
            )
            return response.content.strip()
        except Exception:
            return "Summary generation failed."

    def _prepare_articles_text(self, articles: List[Dict[str, Any]], max_articles: int = 10) -> str:
        articles_text = []
        
        for i, article in enumerate(articles[:max_articles]):
            headline = article.get('headline', '')
            articles_text.append(f"{i+1}. {headline}")
        
        return "\n".join(articles_text)

    def summarize_all_clusters(self, articles: List[Dict[str, Any]], cluster_summary: Dict[int, Dict[str, Any]], cluster_labels: Dict[int, str]) -> Dict[int, str]:
        cluster_summaries = {}
        
        for cluster_id in cluster_summary:
            if cluster_id == -1:
                cluster_summaries[cluster_id] = "Individual articles with no clear clustering."
                continue
            
            cluster_articles = [article for article in articles if article.get('cluster_id') == cluster_id]
            if cluster_articles:
                label = cluster_labels.get(cluster_id, "")
                summary = self.summarize_cluster(cluster_articles, label)
                cluster_summaries[cluster_id] = summary
        
        return cluster_summaries

    def create_market_summary(self, cluster_summaries: Dict[int, str]) -> str:
        if not cluster_summaries:
            return "No significant market developments to report."
        
        summary_parts = []
        for cluster_id, summary in cluster_summaries.items():
            if cluster_id != -1:
                summary_parts.append(summary)
        
        if summary_parts:
            return " ".join(summary_parts)
        else:
            return "Market activity shows individual news items without clear thematic clustering."
