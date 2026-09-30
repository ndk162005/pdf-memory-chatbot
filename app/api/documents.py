import logging
from fastapi import APIRouter, HTTPException
from app.database.database import db_manager
from app.database.models import DocumentResponse
from app.processing.document_service import DocumentService

logger = logging.getLogger(__name__)
router = APIRouter()

document_service = DocumentService()

@router.get('/documents', response_model=list[DocumentResponse])
async def list_documents():
    """List all uploaded documents."""
    docs = db_manager.list_documents()
    return [
        DocumentResponse(
            id=doc['id'],
            filename=doc['filename'],
            total_pages=doc['total_pages'],
            uploaded_at=doc['uploaded_at']
        )
        for doc in docs
    ]

@router.delete('/documents/{document_id}')
async def delete_document(document_id: int):
    """Delete a document and all associated data."""
    doc = db_manager.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail='Document not found')
    
    deleted = await document_service.delete_document(document_id)
    
    if deleted:
        return {'status': 'success', 'message': f'Document {document_id} deleted'}
    else:
        raise HTTPException(status_code=500, detail='Failed to delete document')
