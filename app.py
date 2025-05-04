from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from models import QuestionRequest, AnswerResponse, ConversationRequest
from rag_system import RAGSystem

# Initialize RAG system
rag_system = RAGSystem()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/answer", response_model=AnswerResponse)
async def get_answer(request: QuestionRequest):
    if not request.question or len(request.question.strip()) == 0:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    result = rag_system.answer_question(request.question, request.conversation_id)
    return result

@app.post("/api/clear-conversation")
async def clear_conversation(request: ConversationRequest):
    success = rag_system.clear_conversation(request.conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "success", "message": "Conversation cleared"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)