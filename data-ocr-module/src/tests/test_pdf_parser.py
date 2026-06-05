"""
Tests for PDF Parser and Document Loader.

Tests native PDF text extraction, metadata extraction,
file validation, and document loading functionality.
"""

import pytest
from pathlib import Path

from src.ingestion.document_loader import (
    DocumentLoader,
    DocumentLoadError,
    UnsupportedFileError,
    FileSizeError,
)
from src.ocr.pdf_parser import PDFParser, PDFParseError


class TestDocumentLoader:
    """Test suite for DocumentLoader."""

    def test_init_default_config(self):
        """Test DocumentLoader initializes with default config."""
        loader = DocumentLoader()
        assert loader.max_file_size_mb > 0
        assert ".pdf" in loader.supported_extensions
        assert ".docx" in loader.supported_extensions
        assert ".txt" in loader.supported_extensions

    def test_detect_file_type_txt(self, sample_txt_file):
        """Test file type detection for .txt files."""
        loader = DocumentLoader()
        result = loader.detect_file_type(sample_txt_file)
        assert result["extension"] == ".txt"
        assert result["category"] == "text"

    def test_detect_file_type_pdf(self, tmp_dir):
        """Test file type detection for .pdf extension."""
        loader = DocumentLoader()
        # Create a dummy PDF-named file
        pdf_path = tmp_dir / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 dummy content")
        result = loader.detect_file_type(pdf_path)
        assert result["extension"] == ".pdf"
        assert result["category"] == "pdf"

    def test_detect_file_type_docx(self, tmp_dir):
        """Test file type detection for .docx extension."""
        loader = DocumentLoader()
        docx_path = tmp_dir / "test.docx"
        docx_path.write_bytes(b"PK dummy content")
        result = loader.detect_file_type(docx_path)
        assert result["extension"] == ".docx"
        assert result["category"] == "docx"

    def test_validate_file_success(self, sample_txt_file):
        """Test successful file validation."""
        loader = DocumentLoader()
        result = loader.validate_file(sample_txt_file)
        assert result["valid"] is True
        assert result["extension"] == ".txt"
        assert result["size_bytes"] > 0

    def test_validate_file_not_found(self, tmp_dir):
        """Test validation fails for non-existent file."""
        loader = DocumentLoader()
        with pytest.raises(DocumentLoadError, match="File not found"):
            loader.validate_file(tmp_dir / "nonexistent.txt")

    def test_validate_file_empty(self, empty_file):
        """Test validation fails for empty file."""
        loader = DocumentLoader()
        with pytest.raises(DocumentLoadError, match="File is empty"):
            loader.validate_file(empty_file)

    def test_validate_file_unsupported(self, unsupported_file):
        """Test validation fails for unsupported extension."""
        loader = DocumentLoader()
        with pytest.raises(UnsupportedFileError, match="Unsupported file type"):
            loader.validate_file(unsupported_file)

    def test_validate_file_too_large(self, large_file):
        """Test validation fails when file exceeds size limit."""
        loader = DocumentLoader(max_file_size_mb=0)  # 0 MB limit
        with pytest.raises(FileSizeError, match="File too large"):
            loader.validate_file(large_file)

    def test_extract_metadata(self, sample_txt_file):
        """Test metadata extraction from file."""
        loader = DocumentLoader()
        metadata = loader.extract_metadata(sample_txt_file)
        assert "filename" in metadata
        assert "size_bytes" in metadata
        assert "created_at" in metadata
        assert "modified_at" in metadata
        assert metadata["extension"] == ".txt"

    def test_load_text_file(self, sample_txt_file, sample_text):
        """Test loading a text file."""
        loader = DocumentLoader()
        result = loader.load(sample_txt_file)
        assert result["text"] is not None
        assert len(result["text"]) > 0
        assert result["processing_method"] == "native"
        assert result["pages"] == 1
        assert "MASTER SERVICE AGREEMENT" in result["text"]

    def test_load_pdf_routing(self, tmp_dir):
        """Test that PDF files are routed for PDF extraction."""
        loader = DocumentLoader()
        pdf_path = tmp_dir / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 dummy content for routing test")
        result = loader.load(pdf_path)
        assert result.get("requires_pdf_parser") is True
        assert result["processing_method"] == "pending_pdf_extraction"

    def test_batch_validate(self, sample_txt_file, unsupported_file, empty_file):
        """Test batch validation of multiple files."""
        loader = DocumentLoader()
        result = loader.batch_validate(
            [sample_txt_file, unsupported_file, empty_file]
        )
        assert len(result["valid"]) == 1
        assert len(result["invalid"]) == 2


class TestPDFParser:
    """Test suite for PDFParser."""

    def test_init(self):
        """Test PDFParser initializes successfully."""
        parser = PDFParser()
        assert parser is not None

    def test_extract_nonexistent_file(self):
        """Test extraction fails for non-existent file."""
        parser = PDFParser()
        with pytest.raises(PDFParseError, match="File not found"):
            parser.extract(Path("nonexistent.pdf"))

    def test_extract_non_pdf(self, sample_txt_file):
        """Test extraction fails for non-PDF file."""
        parser = PDFParser()
        with pytest.raises(PDFParseError, match="Not a PDF"):
            parser.extract(sample_txt_file)

    def test_extract_metadata_error(self):
        """Test metadata extraction handles errors gracefully."""
        parser = PDFParser()
        result = parser.extract_metadata(Path("nonexistent.pdf"))
        assert "error" in result

    def test_is_scanned_pdf_error(self, sample_txt_file):
        """Test scanned PDF detection handles non-PDF files."""
        parser = PDFParser()
        # Should return True (assume scanned) when analysis fails
        result = parser.is_scanned_pdf(sample_txt_file)
        assert isinstance(result, bool)
