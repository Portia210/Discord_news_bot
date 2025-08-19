"""
Labeler module for the news processing pipeline.
Handles lightweight labeling using spaCy NER.
"""

import spacy
from typing import List, Dict, Any, Set
from collections import Counter

class ClusterLabeler:
    def __init__(self, model_name: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", model_name])
            self.nlp = spacy.load(model_name)

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        doc = self.nlp(text)
        entities = {}
        
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)
        
        return entities

    def create_cluster_label(self, articles: List[Dict[str, Any]], max_entities: int = 5) -> str:
        all_text = " ".join([article.get('headline', '') for article in articles])
        entities = self.extract_entities(all_text)
        
        if not entities:
            return "General News"
        
        entity_counts = Counter()
        for entity_list in entities.values():
            entity_counts.update(entity_list)
        
        top_entities = [entity for entity, _ in entity_counts.most_common(max_entities)]
        return " | ".join(top_entities)

    def label_clusters(self, articles: List[Dict[str, Any]], cluster_summary: Dict[int, Dict[str, Any]]) -> Dict[int, str]:
        cluster_labels = {}
        
        for cluster_id in cluster_summary:
            if cluster_id == -1:
                cluster_labels[cluster_id] = "Noise"
                continue
            
            cluster_articles = [article for article in articles if article.get('cluster_id') == cluster_id]
            if cluster_articles:
                label = self.create_cluster_label(cluster_articles)
                cluster_labels[cluster_id] = label
        
        return cluster_labels
    
    def extract_key_entities(self, articles: List[Dict[str, Any]], entity_types: List[str] = None) -> Dict[str, List[str]]:
        """
        Extract key entities of specific types from articles.
        
        Args:
            articles: List of articles
            entity_types: List of entity types to extract (e.g., ['PERSON', 'ORG', 'GPE'])
            
        Returns:
            Dictionary mapping entity types to lists of entities
        """
        if entity_types is None:
            entity_types = ['PERSON', 'ORG', 'GPE', 'MONEY', 'DATE']
        
        key_entities = {entity_type: [] for entity_type in entity_types}
        
        for article in articles:
            text = article.get('full_text', '')
            entities = self.extract_entities(text)
            
            for entity_type in entity_types:
                if entity_type in entities:
                    for entity in entities[entity_type]:
                        if entity not in key_entities[entity_type]:
                            key_entities[entity_type].append(entity)
        
        return key_entities
