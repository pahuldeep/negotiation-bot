from backend.emotion_agent import EmotionAnalyzer

# from app.chatbot.backend.emotion_agent import EmotionAnalyzer
# from app.chatbot.backend.finance_agent import FinanceAnalyzer
# from app.chatbot.backend.context_agent import NegotiationContext

# ----------------------------------------
# TOOL 1: Emotion Detection
# ----------------------------------------

def detect_emotion(context: str, threshold: float = 0.6):
    """Detects emotions in negotiation-related messages."""
    analyzer = EmotionAnalyzer(confidence_threshold=threshold)
    analyzer.analyze_text(context)
    return analyzer.summarize_emotions()

# ----------------------------------------
# TOOL 2: Negotiation Context
# ----------------------------------------

# def negotiation_context(text: str):
#     """Extracts structured parameters from a negotiation message."""
#     extractor = NegotiationContext(model="llama3.2")
#     context = extractor.extract(text)
#     summary = extractor.generate_context_summary(context)
#     return summary


# if __name__ == "__main__":

#     negotiation_text = "I can offer $10,000 for the truck load, but only if you include a 6-month warranty."

#     print("\n--- Detecting Emotions ---")
#     emotions = detect_emotion(negotiation_text)
#     print(emotions)

    # print("\n--- Extracting Negotiation Context ---")
    # context_result = negotiation_context(negotiation_text)
    # print(context_result)




















# from typing import List, Dict, Any
# from pydantic import BaseModel
# from langchain.tools import tool

# from context_call import NegotiationContext
# from hf_models import EmotionAnalyzer, EntityAnalyzer

# # --------------------------
# # TOOL 1: Negotiation Context
# # --------------------------
# class ContextInput(BaseModel):
#     text: str

# class ContextOutput(BaseModel):
#     context: Dict[str, Any]
#     parameter_frequencies: Dict[str, int]

# @tool
# def extract_negotiation_context(input: ContextInput) -> ContextOutput:
#     extractor = NegotiationContext(model="mistral")
#     context = extractor.extract(input.text)
#     frequencies = extractor.count_filled_parameters(context)
#     return ContextOutput(context=context, parameter_frequencies=frequencies)

# # --------------------------
# # TOOL 2: Financial Entity Analysis
# # --------------------------
# class FinancialInput(BaseModel):
#     context: str
#     text: str

# class EntityOutput(BaseModel):
#     entities: List[Dict[str, str]]

# @tool
# def analyze_financial_entities(input: FinancialInput) -> EntityOutput:
#     analyzer = EntityAnalyzer("AhmedTaha012/finance-ner-v0.0.9-finetuned-ner")
#     analyzer.analyze_text(input.context, input.text)
#     entities = analyzer.get_entity_summary()
#     return EntityOutput(entities=entities)

# # --------------------------
# # TOOL 3: Emotion Detection
# # --------------------------
# class EmotionInput(BaseModel):
#     context: str
#     message: str
#     threshold: float = 0.6

# class EmotionOutput(BaseModel):
#     emotions: List[Dict[str, Any]]

# @tool
# def detect_emotion(input: EmotionInput) -> EmotionOutput:
#     analyzer = EmotionAnalyzer(confidence_threshold=input.threshold)
#     emotions = analyzer.analyze_text(input.context, input.message)
#     return EmotionOutput(emotions=emotions)
