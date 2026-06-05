"""
Tests for CUAD Dataset Pipeline, Text Cleaner, and JSON Formatter.

Tests the full CUAD loading → parsing → export workflow,
text cleaning pipeline, and structured output formatting.
"""

import json
import pytest
from pathlib import Path

from src.dataset.cuad_loader import CUADLoader, CUAD_CLAUSE_TYPES
from src.dataset.cuad_parser import CUADParser
from src.dataset.cuad_exporter import CUADExporter
from src.preprocessing.clean_text import TextCleaner
from src.preprocessing.json_formatter import JSONFormatter


# =============================================================================
# CUAD Loader Tests
# =============================================================================


class TestCUADLoader:
    """Test suite for CUAD dataset loader."""

    def test_clause_types_defined(self):
        """Test that all 41 CUAD clause types are defined."""
        assert len(CUAD_CLAUSE_TYPES) == 41
        assert "Governing Law" in CUAD_CLAUSE_TYPES
        assert "Non-Compete" in CUAD_CLAUSE_TYPES
        assert "Parties" in CUAD_CLAUSE_TYPES

    def test_init(self, tmp_dir):
        """Test CUADLoader initialization."""
        loader = CUADLoader(
            dataset_path=tmp_dir, output_path=tmp_dir / "output"
        )
        assert loader.dataset_path == tmp_dir
        assert (tmp_dir / "output").exists()

    def test_find_dataset_file(self, sample_cuad_json):
        """Test finding CUAD dataset file."""
        loader = CUADLoader(dataset_path=sample_cuad_json.parent)
        result = loader.find_dataset_file()
        assert result is not None
        assert result.name == "CUADv1.json"

    def test_find_dataset_file_missing(self, tmp_dir):
        """Test finding dataset file when not present."""
        loader = CUADLoader(dataset_path=tmp_dir / "empty")
        (tmp_dir / "empty").mkdir(exist_ok=True)
        result = loader.find_dataset_file()
        assert result is None

    def test_load_success(self, sample_cuad_json):
        """Test successful dataset loading."""
        loader = CUADLoader(dataset_path=sample_cuad_json.parent)
        result = loader.load()
        assert result is not None
        assert "data" in result
        assert len(loader.articles) > 0

    def test_load_not_found(self, tmp_dir):
        """Test loading when dataset is not found."""
        empty_dir = tmp_dir / "empty"
        empty_dir.mkdir(exist_ok=True)
        loader = CUADLoader(dataset_path=empty_dir)
        result = loader.load()
        assert result is None

    def test_num_contracts(self, sample_cuad_json):
        """Test contract count after loading."""
        loader = CUADLoader(dataset_path=sample_cuad_json.parent)
        loader.load()
        assert loader.num_contracts == 1

    def test_get_contract(self, sample_cuad_json):
        """Test getting a specific contract by index."""
        loader = CUADLoader(dataset_path=sample_cuad_json.parent)
        loader.load()
        contract = loader.get_contract(0)
        assert contract is not None
        assert "title" in contract

    def test_get_contract_out_of_range(self, sample_cuad_json):
        """Test getting contract with invalid index."""
        loader = CUADLoader(dataset_path=sample_cuad_json.parent)
        loader.load()
        contract = loader.get_contract(999)
        assert contract is None

    def test_get_contract_texts(self, sample_cuad_json):
        """Test extracting contract texts."""
        loader = CUADLoader(dataset_path=sample_cuad_json.parent)
        loader.load()
        texts = loader.get_contract_texts()
        assert len(texts) == 1
        assert "title" in texts[0]
        assert "text" in texts[0]
        assert len(texts[0]["text"]) > 0

    def test_summary(self, sample_cuad_json):
        """Test dataset summary generation."""
        loader = CUADLoader(dataset_path=sample_cuad_json.parent)
        loader.load()
        summary = loader.summary()
        assert summary["num_contracts"] == 1
        assert summary["clause_types"] == 41

    def test_summary_not_loaded(self, tmp_dir):
        """Test summary when data not loaded."""
        loader = CUADLoader(dataset_path=tmp_dir)
        summary = loader.summary()
        assert summary["status"] == "not_loaded"


# =============================================================================
# CUAD Parser Tests
# =============================================================================


class TestCUADParser:
    """Test suite for CUAD dataset parser."""

    def test_init(self):
        """Test CUADParser initialization."""
        parser = CUADParser()
        assert parser.parsed_contracts == []
        assert parser.parse_errors == []

    def test_generate_contract_id(self):
        """Test deterministic contract ID generation."""
        id1 = CUADParser.generate_contract_id("title1", "text1")
        id2 = CUADParser.generate_contract_id("title1", "text1")
        id3 = CUADParser.generate_contract_id("title2", "text2")
        assert id1 == id2  # Same input = same ID
        assert id1 != id3  # Different input = different ID
        assert len(id1) == 16

    def test_parse_article(self, sample_cuad_article):
        """Test parsing a single CUAD article."""
        parser = CUADParser()
        result = parser.parse_article(sample_cuad_article)
        assert result is not None
        assert "contract_id" in result
        assert "text" in result
        assert "clauses" in result
        assert len(result["clauses"]) > 0

    def test_parse_article_clause_types(self, sample_cuad_article):
        """Test that parsed clauses have correct types."""
        parser = CUADParser()
        result = parser.parse_article(sample_cuad_article)
        clause_types = {c["type"] for c in result["clauses"]}
        assert "Governing Law" in clause_types or "Agreement Date" in clause_types

    def test_parse_article_empty_paragraphs(self):
        """Test parsing article with empty paragraphs."""
        parser = CUADParser()
        article = {"title": "Empty", "paragraphs": []}
        result = parser.parse_article(article)
        assert result is None

    def test_parse_all(self, sample_cuad_article):
        """Test parsing all articles."""
        parser = CUADParser()
        results = parser.parse_all(
            [sample_cuad_article], show_progress=False
        )
        assert len(results) == 1
        assert results[0]["contract_id"] is not None

    def test_clause_deduplication(self, sample_cuad_article):
        """Test that duplicate clauses are removed."""
        parser = CUADParser()
        result = parser.parse_article(sample_cuad_article)
        # Check for unique spans
        spans = [
            (c["type"], c["start"], c["end"]) for c in result["clauses"]
        ]
        assert len(spans) == len(set(spans))

    def test_clause_sorting(self, sample_cuad_article):
        """Test that clauses are sorted by start position."""
        parser = CUADParser()
        result = parser.parse_article(sample_cuad_article)
        starts = [c["start"] for c in result["clauses"]]
        assert starts == sorted(starts)

    def test_get_clause_statistics(self, sample_cuad_article):
        """Test clause statistics computation."""
        parser = CUADParser()
        parser.parse_all([sample_cuad_article], show_progress=False)
        stats = parser.get_clause_statistics()
        assert stats["total_contracts"] == 1
        assert stats["total_clauses"] > 0
        assert "clause_type_distribution" in stats

    def test_get_clause_statistics_empty(self):
        """Test statistics when no data parsed."""
        parser = CUADParser()
        stats = parser.get_clause_statistics()
        assert stats["status"] == "no_data"


# =============================================================================
# CUAD Exporter Tests
# =============================================================================


class TestCUADExporter:
    """Test suite for CUAD dataset exporter."""

    def test_init(self, tmp_dir):
        """Test exporter initialization."""
        exporter = CUADExporter(output_dir=tmp_dir)
        assert exporter.output_dir == tmp_dir

    def test_export_training_json(self, tmp_dir, sample_cuad_article):
        """Test training JSON export."""
        parser = CUADParser()
        contracts = parser.parse_all(
            [sample_cuad_article], show_progress=False
        )
        exporter = CUADExporter(output_dir=tmp_dir)
        output_path = exporter.export_training_json(contracts)

        assert output_path.exists()
        with open(output_path) as f:
            data = json.load(f)
        assert "metadata" in data
        assert "contracts" in data
        assert len(data["contracts"]) == 1

        # Verify schema
        contract = data["contracts"][0]
        assert "contract_id" in contract
        assert "text" in contract
        assert "clauses" in contract

    def test_export_individual_contracts(self, tmp_dir, sample_cuad_article):
        """Test individual contract export."""
        parser = CUADParser()
        contracts = parser.parse_all(
            [sample_cuad_article], show_progress=False
        )
        exporter = CUADExporter(output_dir=tmp_dir)
        output_dir = exporter.export_individual_contracts(contracts)

        assert output_dir.exists()
        json_files = list(output_dir.glob("*.json"))
        assert len(json_files) == 1

    def test_export_clause_csv(self, tmp_dir, sample_cuad_article):
        """Test clause CSV export."""
        parser = CUADParser()
        contracts = parser.parse_all(
            [sample_cuad_article], show_progress=False
        )
        exporter = CUADExporter(output_dir=tmp_dir)
        output_path = exporter.export_clause_csv(contracts)

        assert output_path.exists()
        assert output_path.suffix == ".csv"

    def test_export_summary_report(self, tmp_dir, sample_cuad_article):
        """Test summary report export."""
        parser = CUADParser()
        contracts = parser.parse_all(
            [sample_cuad_article], show_progress=False
        )
        exporter = CUADExporter(output_dir=tmp_dir)
        output_path = exporter.export_summary_report(contracts)

        assert output_path.exists()
        with open(output_path) as f:
            data = json.load(f)
        assert "statistics" in data

    def test_export_all(self, tmp_dir, sample_cuad_article):
        """Test full export pipeline."""
        parser = CUADParser()
        contracts = parser.parse_all(
            [sample_cuad_article], show_progress=False
        )
        exporter = CUADExporter(output_dir=tmp_dir)
        results = exporter.export_all(contracts)

        assert "training_json" in results
        assert "individual_contracts" in results
        assert "clause_csv" in results
        assert "summary_report" in results


# =============================================================================
# Text Cleaner Tests
# =============================================================================


class TestTextCleaner:
    """Test suite for text cleaning pipeline."""

    def test_init(self):
        """Test TextCleaner initialization."""
        cleaner = TextCleaner()
        assert cleaner is not None

    def test_normalize_unicode(self):
        """Test unicode normalization."""
        cleaner = TextCleaner()
        text = "This is \u201csmart\u201d text with \u2019s"
        result = cleaner.normalize_unicode(text)
        assert "\u201c" not in result
        assert "\u201d" not in result
        assert '"smart"' in result

    def test_remove_excessive_whitespace(self):
        """Test whitespace normalization."""
        cleaner = TextCleaner()
        text = "Hello    World\n\n\n\nNew  Paragraph"
        result = cleaner.remove_excessive_whitespace(text)
        assert "    " not in result
        assert "\n\n\n" not in result

    def test_remove_headers_footers(self):
        """Test header/footer removal."""
        cleaner = TextCleaner()
        text = "Page 1 of 10\nActual content here\nCONFIDENTIAL\n2\nMore content"
        result = cleaner.remove_headers_footers(text)
        assert "Page 1 of 10" not in result
        assert "CONFIDENTIAL" not in result
        assert "Actual content here" in result

    def test_remove_page_numbers(self):
        """Test page number removal."""
        cleaner = TextCleaner()
        text = "Content\nPage 5 of 20\n- 3 -\nMore content"
        result = cleaner.remove_page_numbers(text)
        assert "Page 5 of 20" not in result
        assert "- 3 -" not in result

    def test_clean_legal_text(self):
        """Test legal text cleanup."""
        cleaner = TextCleaner()
        text = "Section  3.1  Terms\n_________________________\n========="
        result = cleaner.clean_legal_text(text)
        assert "Section 3.1" in result
        assert "____" not in result
        assert "====" not in result

    def test_split_sentences(self):
        """Test sentence splitting."""
        cleaner = TextCleaner()
        text = (
            "This is section 3.1 of the Agreement. "
            "The Provider Inc. shall perform services. "
            "This is the final sentence."
        )
        sentences = cleaner.split_sentences(text)
        assert len(sentences) >= 2
        # Should NOT split on "Inc." or "3.1"

    def test_preserve_clause_formatting(self):
        """Test clause formatting preservation."""
        cleaner = TextCleaner()
        text = "ARTICLE 1. Definitions\n1.1 Terms\n(a) First item\n(b) Second item"
        result = cleaner.preserve_clause_formatting(text)
        assert "ARTICLE 1." in result
        assert "(a)" in result

    def test_full_clean_pipeline(self, sample_text):
        """Test the full cleaning pipeline."""
        cleaner = TextCleaner()
        result = cleaner.clean(sample_text)
        assert result["clean_text"] is not None
        assert len(result["clean_text"]) > 0
        assert result["num_sentences"] > 0
        assert result["clean_length"] > 0
        assert "MASTER SERVICE AGREEMENT" in result["clean_text"]

    def test_clean_dirty_text(self, sample_dirty_text):
        """Test cleaning dirty/messy text."""
        cleaner = TextCleaner()
        result = cleaner.clean(sample_dirty_text, is_ocr=False)
        clean = result["clean_text"]
        assert "Page 1 of 10" not in clean
        assert "Page 2 of 10" not in clean
        assert "CONFIDENTIAL" not in clean
        assert "DRAFT" not in clean
        assert "AGREEMENT" in clean
        assert result["reduction_percent"] > 0

    def test_clean_empty_text(self):
        """Test cleaning empty text."""
        cleaner = TextCleaner()
        result = cleaner.clean("")
        assert result["clean_text"] == ""
        assert result["num_sentences"] == 0


# =============================================================================
# JSON Formatter Tests
# =============================================================================


class TestJSONFormatter:
    """Test suite for JSON output formatter."""

    def test_init(self, tmp_dir):
        """Test JSONFormatter initialization."""
        formatter = JSONFormatter(output_dir=tmp_dir)
        assert formatter.output_dir == tmp_dir

    def test_generate_document_id(self):
        """Test deterministic document ID generation."""
        id1 = JSONFormatter.generate_document_id("file.pdf", "text content")
        id2 = JSONFormatter.generate_document_id("file.pdf", "text content")
        id3 = JSONFormatter.generate_document_id("other.pdf", "other text")
        assert id1 == id2
        assert id1 != id3
        assert len(id1) == 20

    def test_determine_document_type_contract(self):
        """Test document type detection for contracts."""
        assert (
            JSONFormatter.determine_document_type(
                "agreement.pdf", "This is a service agreement"
            )
            == "service_agreement"
        )

    def test_determine_document_type_nda(self):
        """Test document type detection for NDAs."""
        assert (
            JSONFormatter.determine_document_type(
                "nda.pdf", "Non-disclosure agreement"
            )
            == "nda"
        )

    def test_determine_document_type_unknown(self):
        """Test document type detection for unknown types."""
        assert (
            JSONFormatter.determine_document_type(
                "doc.pdf", "Random text with no keywords"
            )
            == "unknown"
        )

    def test_format_document(self, tmp_dir):
        """Test document formatting."""
        formatter = JSONFormatter(output_dir=tmp_dir)
        result = formatter.format_document(
            filename="test_contract.pdf",
            clean_text="This is a test agreement between parties.",
            pages=5,
            processing_method="native",
        )
        assert result["document_id"] is not None
        assert result["filename"] == "test_contract.pdf"
        assert result["pages"] == 5
        assert result["processing_method"] == "native"
        assert result["document_type"] == "contract"  # "agreement" keyword
        assert "text_preview" in result
        assert "metadata" in result

    def test_format_and_save(self, tmp_dir):
        """Test formatting and saving a document."""
        formatter = JSONFormatter(output_dir=tmp_dir)
        document, output_path = formatter.format_and_save(
            filename="test.pdf",
            clean_text="Test contract agreement content.",
            pages=1,
            processing_method="native",
        )
        assert output_path.exists()
        with open(output_path) as f:
            data = json.load(f)
        assert data["document_id"] == document["document_id"]

    def test_validate_output_valid(self, tmp_dir):
        """Test output validation for valid document."""
        formatter = JSONFormatter(output_dir=tmp_dir)
        document = formatter.format_document(
            filename="test.pdf",
            clean_text="Valid content",
            pages=1,
            processing_method="native",
        )
        result = JSONFormatter.validate_output(document)
        assert result["valid"] is True
        assert result["errors"] == []

    def test_validate_output_invalid(self):
        """Test output validation for invalid document."""
        result = JSONFormatter.validate_output({"filename": "test.pdf"})
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_export_batch(self, tmp_dir):
        """Test batch export."""
        formatter = JSONFormatter(output_dir=tmp_dir)
        documents = [
            formatter.format_document(
                filename=f"doc{i}.pdf",
                clean_text=f"Content {i}",
                pages=1,
                processing_method="native",
            )
            for i in range(3)
        ]
        output_path = formatter.export_batch(documents)
        assert output_path.exists()
        with open(output_path) as f:
            data = json.load(f)
        assert data["metadata"]["num_documents"] == 3
        assert len(data["documents"]) == 3
