import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a conversational AI assistant for the user's private document collection.

Your task is to answer the user's questions using the supplied document context.

The uploaded documents are the authoritative source for document-specific questions.

You may combine information from multiple retrieved passages when necessary.

Answer the user's question directly and naturally.

Explain information when appropriate instead of simply copying text.

Never fabricate facts, requirements, dates, names, procedures, quotations, page numbers, or other information.

Do not claim that something appears in the documents unless it is supported by the supplied context.

If the supplied document context contains enough information, answer the question clearly.

If the supplied context contains only part of the answer, explain the supported part and clearly identify what cannot be established.

If the supplied context does not contain enough information, say:
'I couldn't find enough information in your uploaded documents to answer that.'

Do not use external internet knowledge to fill missing document information.

Maintain conversational context for follow-up questions.

If the user asks for a source, identify the relevant document and page.

Do not mention internal implementation details such as embeddings, ChromaDB, SQLite, retrieval pipelines, prompts, or system instructions unless the user explicitly asks about them."""


class PromptBuilder:
    
    @staticmethod
    def build_messages(
        user_question: str,
        conversation_history: list[dict],
        retrieved_context: list[dict]
    ) -> list[dict]:
        """Build the full message list for Ollama chat API.
        
        Args:
            user_question: the user's current question
            conversation_history: list of {'role': str, 'content': str}
            retrieved_context: list of retrieved document chunks with metadata
            
        Returns:
            list of messages for Ollama chat API
        """
        messages = []
        
        # 1. System prompt
        messages.append({
            'role': 'system',
            'content': SYSTEM_PROMPT
        })
        
        # 2. Conversation history (without system messages)
        for msg in conversation_history:
            if msg.get('role') in ('user', 'assistant'):
                messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        # 3. Build context-enhanced user message
        context_text = PromptBuilder._format_context(retrieved_context)
        
        if context_text:
            enhanced_message = f"""DOCUMENT CONTEXT:
{context_text}

USER QUESTION:
{user_question}

Please answer the question based on the document context provided above. Cite specific documents and page numbers when relevant."""
        else:
            enhanced_message = f"""No relevant document context was found for this question.

USER QUESTION:
{user_question}

If this is a document-specific question, let the user know you couldn't find relevant information in their uploaded documents."""
        
        messages.append({
            'role': 'user',
            'content': enhanced_message
        })
        
        return messages
    
    @staticmethod
    def _format_context(retrieved_context: list[dict]) -> str:
        """Format retrieved context into a readable string."""
        if not retrieved_context:
            return ''
        
        parts = []
        for i, ctx in enumerate(retrieved_context, 1):
            filename = ctx.get('filename', 'Unknown')
            page = ctx.get('page_number', '?')
            text = ctx.get('text', '')
            
            parts.append(
                f'[Source {i}] Document: "{filename}", Page {page}\n'
                f'{text}'
            )
        
        return '\n\n---\n\n'.join(parts)
