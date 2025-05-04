from pydantic import BaseModel
from typing import Optional

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class QuestionRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None

class AnswerResponse(BaseModel):
    answer: str
    conversation_id: str

class ConversationRequest(BaseModel):
    conversation_id: str