"""
Database module for the news processing pipeline.
Handles SQLite storage using SQLAlchemy.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from .config import Config

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    id = Column(String, primary_key=True)
    headline = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    full_text = Column(Text, nullable=False)
    source = Column(String, nullable=False)
    timestamp = Column(String)
    url = Column(String)
    embedding = Column(JSON)
    cluster_id = Column(Integer, default=-1)
    impact_similarity = Column(Float)
    impact_score = Column(Float)
    cluster_size = Column(Integer, default=1)
    cluster_confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    raw_data = Column(JSON)

class Cluster(Base):
    __tablename__ = 'clusters'
    id = Column(Integer, primary_key=True)
    label = Column(String)
    summary = Column(Text)
    size = Column(Integer, default=0)
    avg_impact_score = Column(Float, default=0.0)
    avg_similarity = Column(Float, default=0.0)
    sources = Column(JSON)
    earliest_timestamp = Column(String)
    latest_timestamp = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DatabaseManager:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or Config.DATABASE_URL
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()

    def store_articles(self, articles: List[Dict[str, Any]]) -> int:
        session = self.get_session()
        stored_count = 0
        
        try:
            for article_data in articles:
                article_id = str(hash(article_data.get('headline', '')))
                
                existing = session.query(Article).filter(Article.id == article_id).first()
                if existing:
                    continue
                
                article = Article(
                    id=article_id,
                    headline=article_data.get('headline', ''),
                    content=article_data.get('raw_message', ''),
                    full_text=article_data.get('full_text', ''),
                    source=article_data.get('author', 'Unknown'),
                    timestamp=article_data.get('discord_timestamp'),
                    url=article_data.get('link'),
                    embedding=json.dumps(article_data.get('embedding', [])),
                    cluster_id=article_data.get('cluster_id', -1),
                    impact_similarity=article_data.get('impact_similarity'),
                    impact_score=article_data.get('impact_score'),
                    cluster_size=article_data.get('cluster_size', 1),
                    cluster_confidence=article_data.get('cluster_confidence', 0.0),
                    raw_data=json.dumps(article_data)
                )
                
                session.add(article)
                stored_count += 1
            
            session.commit()
            return stored_count
            
        except Exception:
            session.rollback()
            return 0
        finally:
            session.close()

    def store_clusters(self, cluster_summary: Dict[int, Dict[str, Any]], cluster_labels: Dict[int, str], cluster_summaries: Dict[int, str]) -> int:
        session = self.get_session()
        stored_count = 0
        
        try:
            for cluster_id, summary in cluster_summary.items():
                if cluster_id == -1:
                    continue
                
                existing = session.query(Cluster).filter(Cluster.id == cluster_id).first()
                if existing:
                    continue
                
                cluster = Cluster(
                    id=cluster_id,
                    label=cluster_labels.get(cluster_id, ''),
                    summary=cluster_summaries.get(cluster_id, ''),
                    size=summary.get('size', 0),
                    avg_impact_score=summary.get('avg_impact_score', 0.0),
                    sources=json.dumps(summary.get('sources', [])),
                    earliest_timestamp=summary.get('earliest_timestamp'),
                    latest_timestamp=summary.get('latest_timestamp')
                )
                
                session.add(cluster)
                stored_count += 1
            
            session.commit()
            return stored_count
            
        except Exception:
            session.rollback()
            return 0
        finally:
            session.close()

    def get_articles(self, limit: int = 100) -> List[Dict[str, Any]]:
        session = self.get_session()
        try:
            articles = session.query(Article).limit(limit).all()
            return [
                {
                    'id': article.id,
                    'headline': article.headline,
                    'content': article.content,
                    'full_text': article.full_text,
                    'source': article.source,
                    'timestamp': article.timestamp,
                    'url': article.url,
                    'embedding': json.loads(article.embedding) if article.embedding else None,
                    'cluster_id': article.cluster_id,
                    'impact_similarity': article.impact_similarity,
                    'impact_score': article.impact_score,
                    'cluster_size': article.cluster_size,
                    'cluster_confidence': article.cluster_confidence,
                    'created_at': article.created_at.isoformat() if article.created_at else None,
                    'raw_data': json.loads(article.raw_data) if article.raw_data else None
                }
                for article in articles
            ]
        finally:
            session.close()

    def get_clusters(self) -> List[Dict[str, Any]]:
        session = self.get_session()
        try:
            clusters = session.query(Cluster).all()
            return [
                {
                    'id': cluster.id,
                    'label': cluster.label,
                    'summary': cluster.summary,
                    'size': cluster.size,
                    'avg_impact_score': cluster.avg_impact_score,
                    'avg_similarity': cluster.avg_similarity,
                    'sources': json.loads(cluster.sources) if cluster.sources else [],
                    'earliest_timestamp': cluster.earliest_timestamp,
                    'latest_timestamp': cluster.latest_timestamp,
                    'created_at': cluster.created_at.isoformat() if cluster.created_at else None,
                    'updated_at': cluster.updated_at.isoformat() if cluster.updated_at else None
                }
                for cluster in clusters
            ]
        finally:
            session.close()
