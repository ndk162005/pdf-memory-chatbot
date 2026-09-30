import pytest
import os
import fitz
from app.processing.pdf_extractor import PDFExtractor

@pytest.fixture
def temp_pdf(tmp_path):
    path = str(tmp_path / "test.pdf")
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50,50), 'Test content page 1')
    doc.save(path)
    doc.close()
    return path

@pytest.fixture
def empty_pdf(tmp_path):
    path = str(tmp_path / "empty.pdf")
    doc = fitz.open()
    doc.new_page()
    doc.save(path)
    doc.close()
    return path

def test_extract_nonexistent_file():
    extractor = PDFExtractor()
    with pytest.raises(FileNotFoundError):
        extractor.extract("nonexistent.pdf")

def test_extract_non_pdf(tmp_path):
    extractor = PDFExtractor()
    path = tmp_path / "not_pdf.txt"
    path.write_text("not a pdf")
    with pytest.raises(ValueError):
        extractor.extract(str(path))

def test_extract_valid_pdf(temp_pdf):
    extractor = PDFExtractor()
    pages = extractor.extract(temp_pdf)
    assert len(pages) == 1
    assert "Test content page 1" in pages[0]["text"]
    assert pages[0]["page_number"] == 1

def test_extract_empty_pdf(empty_pdf):
    extractor = PDFExtractor()
    with pytest.raises(ValueError):
        extractor.extract(empty_pdf)

def test_page_numbers_are_one_indexed(tmp_path):
    path = str(tmp_path / "test_multi.pdf")
    doc = fitz.open()
    for i in range(3):
        page = doc.new_page()
        page.insert_text((50,50), f'Page {i}')
    doc.save(path)
    doc.close()
    
    extractor = PDFExtractor()
    pages = extractor.extract(path)
    assert len(pages) == 3
    assert pages[0]["page_number"] == 1
    assert pages[1]["page_number"] == 2
    assert pages[2]["page_number"] == 3
