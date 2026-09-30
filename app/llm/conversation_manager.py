import logging
from datetime import datetime
from collections import defaultdict
from app.core.config import settings

logger = logging.getLogger(__name__)

class ConversationManager:
    """In-memory conversation store. Interface designed for future SQLite migration."""
    
    def __init__(self, max_messages: int = None):
        self.max_messages = max_messages or settings.MAX_CONVERSATION_MESSAGES
        # session_id -> list of messages
        self._conversations: dict[str, list[dict]] = defaultdict(list)
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to the conversation."""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        self._conversations[session_id].append(message)
        
        # Trim if exceeding max
        if len(self._conversations[session_id]) > self.max_messages:
            self._conversations[session_id] = self._conversations[session_id][-self.max_messages:]
    
    def get_history(self, session_id: str) -> list[dict]:
        """Get conversation history for a session."""
        return list(self._conversations.get(session_id, []))
    
    def get_recent_history(self, session_id: str, n: int = None) -> list[dict]:
        """Get the most recent n messages."""
        n = n or self.max_messages
        history = self._conversations.get(session_id, [])
        return list(history[-n:])
    
    def clear_session(self, session_id: str):
        """Clear conversation for a session."""
        if session_id in self._conversations:
            del self._conversations[session_id]
            logger.info(f'Cleared conversation for session {session_id}')
    
    def resolve_followup(self, session_id: str, current_question: str) -> str:
        """Resolve follow-up references using conversation context.
        
        If the current question contains references like 'that', 'it', 'this',
        'those', etc., try to build a more complete query for retrieval.
        """
        history = self.get_recent_history(session_id, 6)  # Last 6 messages
        
        if not history:
            return current_question
        
        # Check if question seems like a follow-up
        followup_indicators = [
            'that', 'this', 'it', 'those', 'these', 'they', 'them',
            'the same', 'above', 'previous', 'mentioned',
            'what about', 'how about', 'and the', 'also',
            'more about', 'explain', 'elaborate', 'why',
            'is it', 'is that', 'are they', 'are those',
            'second', 'third', 'first', 'last', 'next'
        ]
        
        question_lower = current_question.lower().strip()
        is_followup = any(indicator in question_lower for indicator in followup_indicators)
        
        # Also check if question is very short (likely follow-up)
        if len(question_lower.split()) <= 5:
            is_followup = True
        
        if not is_followup:
            return current_question
        
        # Build enhanced query with recent context
        context_parts = []
        for msg in history[-4:]:  # Last 4 messages
            if msg['role'] == 'user':
                context_parts.append(msg['content'])
            elif msg['role'] == 'assistant':
                # Take just the first sentence of assistant response
                first_sentence = msg['content'].split('.')[0]
                if len(first_sentence) < 200:
                    context_parts.append(first_sentence)
        
        # Combine for retrieval (not for display)
        enhanced = ' '.join(context_parts[-2:]) + ' ' + current_question
        logger.info(f'Resolved follow-up: "{current_question}" -> "{enhanced[:100]}..."')
        return enhanced
    
    def list_sessions(self) -> list[str]:
        """List all active session IDs."""
        return list(self._conversations.keys())
