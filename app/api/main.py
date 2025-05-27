from fastapi import FastAPI, HTTPException, Depends
from datetime import datetime
from typing import Dict
import uuid
import json
import redis

from app.core.config import settings
from app.db.redis_connection import get_redis
from app.models.models import NegotiationParameters, NegotiationSession

app = FastAPI(title=settings.app_name)


@app.post("/", response_model=NegotiationSession)
def create_negotiation(parameters: NegotiationParameters, redis_client: redis.Redis = Depends(get_redis)):
    session_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    session = NegotiationSession(
        session_id=session_id,
        parameters=parameters,
        messages=[],
        created_at=timestamp,
        updated_at=timestamp
    )

    redis_client.setex(f"negotiation:{session_id}", settings.session_ttl, json.dumps(session.dict()))
    return session


@app.get("/{session_id}", response_model=NegotiationSession)
def get_negotiation(session_id: str, redis_client: redis.Redis = Depends(get_redis)):
    session_data = redis_client.get(f"negotiation:{session_id}")

    if not session_data: raise HTTPException(status_code=404, detail="Negotiation session not found")

    return NegotiationSession(**json.loads(session_data))


@app.post("/{session_id}/messages")
def add_message(session_id: str, message: Dict, redis_client: redis.Redis = Depends(get_redis)):
    session_data = redis_client.get(f"negotiation:{session_id}")
    if not session_data:
        raise HTTPException(status_code=404, detail="Negotiation session not found")

    session = NegotiationSession(**json.loads(session_data))
    session.messages.append(message)
    session.updated_at = datetime.now().isoformat()

    redis_client.setex(f"negotiation:{session_id}", settings.session_ttl, json.dumps(session.dict()))
    return {"message": "Message added successfully"}


@app.put("/{session_id}/parameters")
def update_parameters(session_id: str, parameters: NegotiationParameters, redis_client: redis.Redis = Depends(get_redis)):
    session_data = redis_client.get(f"negotiation:{session_id}")
    if not session_data:
        raise HTTPException(status_code=404, detail="Negotiation session not found")

    session = NegotiationSession(**json.loads(session_data))
    session.parameters = parameters
    session.updated_at = datetime.now().isoformat()

    redis_client.setex(f"negotiation:{session_id}", settings.session_ttl, json.dumps(session.dict()))
    return {"message": "Parameters updated successfully"}

@app.delete("/{session_id}")
def delete_negotiation(session_id: str, redis_client: redis.Redis = Depends(get_redis)):
    if not redis_client.exists(f"negotiation:{session_id}"):
        raise HTTPException(status_code=404, detail="Negotiation session not found")

    redis_client.delete(f"negotiation:{session_id}")
    return {"message": "Negotiation session deleted successfully"}

