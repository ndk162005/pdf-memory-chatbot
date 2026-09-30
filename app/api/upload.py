import os
import uuid
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.config import settings
from app.processing.document_service import DocumentService
from app.database.models import UploadResponse

logger = logging.getLogger(__name__)
router = APIRouter()

document_service = DocumentService()

@router.post('/upload', response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF document."""
    
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail='No filename provided')
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail='Only PDF files are accepted')
    
    if file.content_type and file.content_type != 'application/pdf':
        # Some browsers may not set content_type correctly, so just warn
        logger.warning(f'Unexpected content type: {file.content_type}')
    
    # Save file temporarily
    settings.ensure_dirs()
    temp_filename = f'{uuid.uuid4().hex}_{file.filename}'
    file_path = settings.UPLOAD_DIR / temp_filename
    
    try:
        # Write file
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail='Empty file uploaded')
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Process the document
        result = await document_service.process_upload(
            file_path=str(file_path),
            filename=file.filename
        )
        
        return result
        
    except ValueError as e:
        logger.error(f'PDF processing error: {e}')
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f'Upload error: {e}')
        raise HTTPException(status_code=500, detail=f'Error processing document: {str(e)}')
    finally:
        # Clean up temp file
        if file_path.exists():
            try:
                os.remove(file_path)
            except Exception:
                pass
