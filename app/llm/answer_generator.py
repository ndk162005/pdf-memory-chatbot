import logging
from app.llm.ollama_client import OllamaClient
from app.llm.prompt_builder import PromptBuilder
from app.llm.conversation_manager import ConversationManager
from app.retrieval.document_retrieval import DocumentRetrieval
from app.database.models import ChatResponse, SourceInfo

logger = logging.getLogger(__name__)

# Global instances
_conversation_manager = ConversationManager()
_ollama_client = OllamaClient()
_document_retrieval = DocumentRetrieval()


class AnswerGenerator:
    
    def __init__(self):
        self.conversation_manager = _conversation_manager
        self.ollama_client = _ollama_client
        self.retrieval = _document_retrieval
        self.prompt_builder = PromptBuilder()
    
    async def generate_answer(self, session_id: str, user_message: str) -> ChatResponse:
        """Generate a grounded answer for the user's question.
        
        Pipeline:
        1. Resolve follow-up references
        2. Retrieve relevant document context
        3. Build prompt with context + history
        4. Send to Ollama
        5. Store messages in conversation
        6. Return answer + sources
        """
        try:
            # 1. Resolve follow-up context
            retrieval_query = self.conversation_manager.resolve_followup(
                session_id, user_message
            )
            
            # 2. Retrieve relevant documents
            retrieved_context = self.retrieval.retrieve(query=retrieval_query)
            
            # 3. Get conversation history
            history = self.conversation_manager.get_recent_history(session_id)
            
            # 4. Build messages for Ollama
            messages = self.prompt_builder.build_messages(
                user_question=user_message,
                conversation_history=history,
                retrieved_context=retrieved_context
            )
            
            # 5. Call Ollama
            logger.info(f'Sending query to Ollama with {len(retrieved_context)} context chunks')
            answer = self.ollama_client.chat(messages=messages)
            
            # Clean up thinking tags from model output if present (qwen3 uses <think> tags)
            answer = self._clean_thinking_tags(answer)
            
            # 6. Store in conversation history
            self.conversation_manager.add_message(session_id, 'user', user_message)
            self.conversation_manager.add_message(session_id, 'assistant', answer)
            
            # 7. Build sources from retrieval (NOT from LLM)
            sources = [
                SourceInfo(
                    filename=ctx.get('filename', 'Unknown'),
                    page_number=ctx.get('page_number', 0),
                    paragraph_number=ctx.get('paragraph_number', 0),
                    text=ctx.get('text', '')
                )
                for ctx in retrieved_context
            ]
            
            return ChatResponse(
                answer=answer,
                sources=sources
            )
            
        except ConnectionError as e:
            logger.error(f'Ollama connection error: {e}')
            return ChatResponse(
                answer=f'⚠️ Cannot connect to Ollama. Please ensure Ollama is running with: ollama serve',
                sources=[]
            )
        except TimeoutError as e:
            logger.error(f'Ollama timeout: {e}')
            return ChatResponse(
                answer='⚠️ The AI model took too long to respond. Please try again with a simpler question.',
                sources=[]
            )
        except ValueError as e:
            logger.error(f'Ollama model error: {e}')
            return ChatResponse(
                answer=f'⚠️ {str(e)}',
                sources=[]
            )
        except Exception as e:
            logger.error(f'Error generating answer: {e}')
            return ChatResponse(
                answer='⚠️ An unexpected error occurred while generating the answer. Please try again.',
                sources=[]
            )
    
    def _clean_thinking_tags(self, text: str) -> str:
        """Remove <think>...</think> blocks from model output."""
        import re
        # Remove think blocks (qwen3 model uses these)
        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        return cleaned.strip()
    
    def clear_conversation(self, session_id: str):
        """Clear conversation history for a session."""
        self.conversation_manager.clear_session(session_id)
