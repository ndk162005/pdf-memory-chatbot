import sys
from pathlib import Path

# Ensure virtual environment packages are accessible regardless of python executable used
venv_site = Path(__file__).resolve().parent / ".venv" / "Lib" / "site-packages"
if venv_site.exists() and str(venv_site) not in sys.path:
    sys.path.insert(0, str(venv_site))

import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings, Settings
from app.database.database import db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    logger.info('Starting PDF Memory Chatbot...')
    
    # Create necessary directories
    Settings.ensure_dirs()
    
    # Initialize database
    db_manager.create_tables()
    logger.info('Database initialized')
    
    # Check Ollama availability (warning only, don't block startup)
    try:
        from app.llm.ollama_client import OllamaClient
        client = OllamaClient()
        if client.is_available():
            if client.check_model():
                logger.info(f'Ollama is available with model: {settings.OLLAMA_MODEL}')
            else:
                logger.warning(
                    f'Ollama is running but model "{settings.OLLAMA_MODEL}" is not available. '
                    f'Please run: ollama pull {settings.OLLAMA_MODEL}'
                )
        else:
            logger.warning(
                'Ollama is not available. Please start Ollama with: ollama serve'
            )
    except Exception as e:
        logger.warning(f'Could not check Ollama availability: {e}')
    
    logger.info('PDF Memory Chatbot started successfully')
    
    yield
    
    db_manager.close()
    logger.info('PDF Memory Chatbot shut down')

# Create FastAPI app
app = FastAPI(
    title='PDF Memory Chatbot',
    description='A local document-memory conversational AI powered by Ollama',
    version='1.0.0',
    lifespan=lifespan
)

# Include API routers
from app.api import upload, chat, documents

app.include_router(upload.router, tags=['Upload'])
app.include_router(chat.router, tags=['Chat'])
app.include_router(documents.router, tags=['Documents'])

# Serve frontend static files
frontend_dir = Path(__file__).parent / 'frontend'
if frontend_dir.exists():
    app.mount('/static', StaticFiles(directory=str(frontend_dir)), name='static')

# Serve frontend index.html at root
@app.get('/')
async def serve_frontend():
    index_path = frontend_dir / 'index.html'
    if index_path.exists():
        return FileResponse(str(index_path))
    return {'message': 'PDF Memory Chatbot API is running. Frontend not found.'}

# Health check
@app.get('/health')
async def health_check():
    return {
        'status': 'healthy',
        'ollama_url': settings.OLLAMA_BASE_URL,
        'ollama_model': settings.OLLAMA_MODEL,
        'embedding_model': settings.EMBEDDING_MODEL_NAME
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)

