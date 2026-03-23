from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, conint, confloat


class ChatMessage(BaseModel):
    role: str = Field(..., description="Role in the conversation (system, user, assistant)")
    content: str = Field(..., description="Text content of the message")


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., description="User message to send to the assistant")
    temperature: Optional[confloat(ge=0.0, le=1.0)] = Field(
        None, description="Sampling temperature"
    )
    max_tokens: Optional[conint(ge=16, le=4096)] = Field(
        None, description="Maximum number of tokens to generate"
    )


class ChatChunk(BaseModel):
    session_id: str
    delta: str
    is_end: bool = False


class ErrorResponse(BaseModel):
    detail: str
    meta: Optional[Dict[str, Any]] = None

