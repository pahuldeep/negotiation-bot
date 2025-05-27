from collections import defaultdict
from typing import Optional, Callable

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# ==================================================
# EMOTION IDENTIFICATION
# ==================================================

class EmotionAnalyzer:
    def __init__(
        self,
        model_name: str = "ayoubkirouane/BERT-Emotions-Classifier",
        confidence_threshold: float = 0.5,
        pipeline_fn: Optional[Callable] = None
    ):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

        self.emotion_pipeline = (
            pipeline_fn("text-classification", model=self.model, tokenizer=self.tokenizer, return_all_scores=True)
            if pipeline_fn else
            pipeline("text-classification", model=self.model, tokenizer=self.tokenizer, return_all_scores=True)
        )

        self.confidence_threshold = confidence_threshold
        self.emotion_counts = defaultdict(int)
        self.emotion_confidences = defaultdict(float)   # To track total confidence per emotion
        self.labels = self.model.config.id2label.values()

    def analyze_text(self, text: str):
        """Analyze emotion of the given text"""
        scores = self.emotion_pipeline(text)[0]

        detected_emotions = []
        for emotion in scores:
            if emotion['score'] >= self.confidence_threshold:
                detected_emotions.append({
                    'emotion': emotion['label'],
                    'confidence': emotion['score']
                })
                self.emotion_counts[emotion['label']] += 1
                self.emotion_confidences[emotion['label']] += emotion['score']

        return detected_emotions


    def reset(self):
        """Reset emotion counts and confidences."""
        self.emotion_counts.clear()
        self.emotion_confidences.clear()

    def summarize_emotions(self) -> str:
        """Generate a one-line summary of detected emotions with average confidence."""
        if not self.emotion_counts:
            return "No emotions detected yet."

        parts = []
        for emotion, count in sorted(self.emotion_counts.items(), key=lambda x: x[1], reverse=True):
            avg_conf = self.emotion_confidences[emotion] / count 
            # {count} occurrence{'s' if count > 1 else ''} with avg
            parts.append(f"{emotion} confidence: {avg_conf:.0%}")

        return " | ".join(parts)


# ================================================
# EXTRA 
# ================================================

# KPI refinements: (user satisfaction, user retentions, user churn rate)
