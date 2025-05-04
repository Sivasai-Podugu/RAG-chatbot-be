from pydantic import BaseModel
from typing import List, Optional

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
    conversation_ids: List[str] = []
    conversation_id: Optional[str] = None  # For backward compatibility
    
    def get_all_ids(self):
        """Get all conversation IDs from both fields"""
        ids = self.conversation_ids.copy()
        if self.conversation_id and self.conversation_id not in ids:
            ids.append(self.conversation_id)
        return ids