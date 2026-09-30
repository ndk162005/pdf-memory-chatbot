import logging
from fastapi import APIRouter, HTTPException
from app.database.models import ChatRequest, ChatResponse
from app.llm.answer_generator import AnswerGenerator

logger = logging.getLogger(__name__)
router = APIRouter()

answer_generator = AnswerGenerator()

@router.post('/chat', response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message and receive a grounded answer."""
    
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail='Message cannot be empty')
    
    if not request.session_id or not request.session_id.strip():
        raise HTTPException(status_code=400, detail='Session ID is required')
    
    result = await answer_generator.generate_answer(
        session_id=request.session_id,
        user_message=request.message.strip()
    )
    
    return result

@router.post('/chat/clear')
async def clear_chat(session_id: str):
    """Clear conversation history for a session."""
    answer_generator.clear_conversation(session_id)
    return {'status': 'success', 'message': 'Conversation cleared'}
