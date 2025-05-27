from collections import defaultdict
from typing import Dict, List, Optional, Callable

from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification


# ==================================================
# FINANCE IDENTIFICATION (Finance-NER (Name entity recoginition))
# ==================================================

# Quantitative (profit, loss, percentage)
class FinanceAnalyzer:
    def __init__(self,
        model_name: str = "AhmedTaha012/finance-ner-v0.0.9-finetuned-ner",
        entity_types: Optional[List[str]] = None,
        aggregation_strategy: str = "simple",
        confidence_threshold: float = 0.85,
        pipeline_fn: Optional[Callable] = None):
        
        # Load model & tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)

        # Extract labels from model config
        self.raw_labels = self.model.config.id2label
        self.entity_types = entity_types or self._extract_entity_types()

        # Build NER pipeline
        self.ner = pipeline_fn("ner", model=self.model, tokenizer=self.tokenizer, aggregation_strategy=aggregation_strategy) if pipeline_fn else pipeline("ner", model=self.model, tokenizer=self.tokenizer, aggregation_strategy=aggregation_strategy)

        self.confidence_threshold = confidence_threshold
        self.entity_counts = defaultdict(lambda: defaultdict(int))

    def _extract_entity_types(self) -> List[str]:
        """Extract base entity types from model label config"""
        types = set()
        for label in self.raw_labels.values():
            if label != "O":
                base_type = label.split("-")[-1]
                types.add(base_type)
        return sorted(types)

    def analyze_text(self, title: str, content: str) -> Dict[str, List[Dict]]:
        """Analyze entities in combined text"""
        full_text = f"{title}\n{content}"
        entities = self.ner(full_text)
        processed = self._process_entities(entities)
        self._update_counts(processed)
        return processed

    def _process_entities(self, entities: List[Dict]) -> Dict[str, List[Dict]]:
        """Filter and organize entities by simplified type"""
        categorized = defaultdict(list)
        for entity in entities:
            if entity['score'] >= self.confidence_threshold:
                label = entity['entity_group']  
                base_type = label.split("-")[-1]  #"profit", "loss", "business", "location".
                if base_type in self.entity_types:
                    categorized[base_type].append({
                        'text': entity['word'],
                        'confidence': entity['score']
                    })
        return dict(categorized)

    def _update_counts(self, processed_entities: Dict[str, List[Dict]]):
        """Track frequency of each entity by type"""
        for category, entities in processed_entities.items():
            for entity in entities:
                self.entity_counts[category][entity['text']] += 1

    def get_entity_summary(self) -> List[Dict]:
        """Summarize entities by category without frequency counts"""
        summary = []
        for category, entities in self.entity_counts.items():
            for entity in entities.keys():
                summary.append({
                    'Category': category,
                    'Entity': entity
                })
        return summary    
    