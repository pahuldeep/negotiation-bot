from pydantic import BaseModel
from typing import Optional, List, Dict

class NegotiationParameters(BaseModel):
    max_price: float
    min_price: float
    target_price: float
    product_id: str
    flexibility: Optional[float] = 0.1
    negotiation_strategy: Optional[str] = "standard"


class NegotiationSession(BaseModel):
    session_id: str
    parameters: NegotiationParameters
    messages: List[Dict]
    created_at: str
    updated_at: str
    status: str = "active"
