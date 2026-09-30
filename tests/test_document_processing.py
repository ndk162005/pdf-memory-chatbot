import pytest
from app.processing.document_processor import DocumentProcessor

def test_process_simple_pages():
    processor = DocumentProcessor()
    pages = [
        {"page_number": 1, "text": "This is a simple paragraph that is long enough to not be filtered."}
    ]
    chunks = processor.process_pages(pages, "doc_1")
    assert len(chunks) == 1
    assert chunks[0]["document_id"] == "doc_1"
    assert chunks[0]["page_number"] == 1
    assert chunks[0]["text"] == "This is a simple paragraph that is long enough to not be filtered."

def test_preserves_page_numbers():
    processor = DocumentProcessor()
    pages = [
        {"page_number": 1, "text": "Page one text that is sufficiently long."},
        {"page_number": 2, "text": "Page two text that is sufficiently long."}
    ]
    chunks = processor.process_pages(pages, "doc_1")
    assert len(chunks) == 2
    assert chunks[0]["page_number"] == 1
    assert chunks[1]["page_number"] == 2

def test_removes_short_chunks():
    processor = DocumentProcessor()
    pages = [
        {"page_number": 1, "text": "Too short\n\nThis is a longer paragraph that should definitely be kept."}
    ]
    chunks = processor.process_pages(pages, "doc_1")
    assert len(chunks) == 1
    assert "longer paragraph" in chunks[0]["text"]

def test_splits_large_paragraphs():
    processor = DocumentProcessor()
    long_text = "Word " * 500
    pages = [
        {"page_number": 1, "text": long_text}
    ]
    chunks = processor.process_pages(pages, "doc_1")
    assert len(chunks) > 1

def test_paragraph_numbering_is_sequential():
    processor = DocumentProcessor()
    pages = [
        {"page_number": 1, "text": "Paragraph one is long enough.\n\nParagraph two is long enough too."},
        {"page_number": 2, "text": "Paragraph three is on the next page."}
    ]
    chunks = processor.process_pages(pages, "doc_1")
    assert len(chunks) == 3
    assert chunks[0]["paragraph_number"] == 1
    assert chunks[1]["paragraph_number"] == 2
    assert chunks[2]["paragraph_number"] == 3

def test_empty_pages_handled():
    processor = DocumentProcessor()
    pages = [
        {"page_number": 1, "text": "    "},
        {"page_number": 2, "text": "Valid text on page two."}
    ]
    chunks = processor.process_pages(pages, "doc_1")
    assert len(chunks) == 1
    assert chunks[0]["page_number"] == 2
