from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentModel(BaseModel):
    id: Optional[int] = None
    filename: str
    total_pages: int
    uploaded_at: Optional[str] = None

class ParagraphModel(BaseModel):
    id: Optional[int] = None
    document_id: int
    page_number: int
    paragraph_number: int
    text: str

class DocumentResponse(BaseModel):
    id: int
    filename: str
    total_pages: int
    uploaded_at: str

class UploadResponse(BaseModel):
    status: str
    document_id: int
    filename: str
    pages: int
    paragraphs: int

class ChatRequest(BaseModel):
    session_id: str
    message: str

class SourceInfo(BaseModel):
    filename: str
    page_number: int
    paragraph_number: int
    text: str

class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceInfo]
