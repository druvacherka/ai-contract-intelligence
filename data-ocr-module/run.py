"""
Master Orchestration Runner — Data + OCR Pipeline.

CLI entry point that orchestrates the full document processing pipeline:

    upload file → detect type → extract text → OCR if needed
    → clean text → format JSON → save output

Usage:
    python run.py --file uploads/sample.pdf
    python run.py --file uploads/contract.docx
    python run.py --dir uploads/
    python run.py --cuad
"""

import argparse
import json
import sys
import time
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.utils.config import Config
from src.utils.logger import logger
from src.ingestion.document_loader import DocumentLoader, DocumentLoadError
from src.ingestion.docx_parser import DOCXParser, DOCXParseError
from src.ocr.pdf_parser import PDFParser, PDFParseError
from src.ocr.ocr_engine import OCREngine, OCRError
from src.ocr.scan_detector import ScanDetector
from src.preprocessing.clean_text import TextCleaner
from src.preprocessing.json_formatter import JSONFormatter


class PipelineOrchestrator:
    """
    Master orchestrator for the document processing pipeline.

    Connects all modules together:
    DocumentLoader → PDFParser/DOCXParser → ScanDetector
    → OCREngine → TextCleaner → JSONFormatter
    """

    def __init__(self) -> None:
        # Ensure all directories exist
        Config.ensure_directories()

        # Initialize all pipeline components
        self.document_loader = DocumentLoader()
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        self.scan_detector = ScanDetector()
        self.ocr_engine = OCREngine()
        self.text_cleaner = TextCleaner()
        self.json_formatter = JSONFormatter()

        logger.info("PipelineOrchestrator initialized — all modules loaded")

    def process_file(self, filepath: str | Path) -> dict:
        """
        Process a single document through the full pipeline.

        Flow:
        1. Validate and detect file type
        2. Extract text (native or OCR)
        3. Clean text
        4. Format to JSON
        5. Save output

        Args:
            filepath: Path to the document file.

        Returns:
            Processing result dict.
        """
        filepath = Path(filepath).resolve()
        overall_start = time.time()

        logger.info("=" * 60)
        logger.info("PIPELINE START: {}", filepath.name)
        logger.info("=" * 60)

        try:
            # ─── Step 1: Validate & Load ───
            logger.info("Step 1/5: Validating document...")
            doc_info = self.document_loader.load(filepath)
            file_metadata = doc_info.get("metadata", {})
            category = file_metadata.get("category", "unknown")

            logger.info(
                "Document validated | type={} | size={:.2f}MB",
                category,
                file_metadata.get("size_mb", 0),
            )

            # ─── Step 2: Extract Text ───
            logger.info("Step 2/5: Extracting text...")
            extracted_text = ""
            pages = 0
            processing_method = "native"
            ocr_confidence = None

            if category == "pdf":
                extracted_text, pages, processing_method, ocr_confidence = (
                    self._process_pdf(filepath)
                )
            elif category == "docx":
                extracted_text, pages = self._process_docx(filepath)
            elif category == "text":
                extracted_text = doc_info.get("text", "")
                pages = 1
            else:
                raise DocumentLoadError(f"Unsupported category: {category}")

            if not extracted_text.strip():
                logger.warning("No text extracted from document")
                extracted_text = "[NO TEXT EXTRACTED]"

            logger.info(
                "Text extracted | method={} | chars={} | pages={}",
                processing_method,
                len(extracted_text),
                pages,
            )

            # ─── Step 3: Clean Text ───
            logger.info("Step 3/5: Cleaning text...")
            is_ocr = processing_method == "ocr"
            clean_result = self.text_cleaner.clean(
                extracted_text, is_ocr=is_ocr
            )
            clean_text = clean_result["clean_text"]
            sentences = clean_result.get("sentences", [])

            logger.info(
                "Text cleaned | original={} | clean={} | reduction={:.1f}%",
                clean_result["original_length"],
                clean_result["clean_length"],
                clean_result["reduction_percent"],
            )

            # ─── Step 4: Format JSON ───
            logger.info("Step 4/5: Formatting output...")
            overall_elapsed = time.time() - overall_start

            document, output_path = self.json_formatter.format_and_save(
                filename=filepath.name,
                clean_text=clean_text,
                pages=pages,
                processing_method=processing_method,
                metadata=file_metadata,
                sentences=sentences,
                confidence=ocr_confidence,
                processing_time=overall_elapsed,
            )

            # ─── Step 5: Report ───
            logger.info("Step 5/5: Processing complete!")
            logger.info("=" * 60)
            logger.info("PIPELINE COMPLETE: {}", filepath.name)
            logger.info("  Document ID:  {}", document["document_id"])
            logger.info("  Document Type: {}", document["document_type"])
            logger.info("  Method:       {}", processing_method)
            logger.info("  Pages:        {}", pages)
            logger.info("  Clean Text:   {} chars", len(clean_text))
            logger.info("  Sentences:    {}", len(sentences))
            logger.info("  Output:       {}", output_path)
            logger.info("  Time:         {:.2f}s", overall_elapsed)
            logger.info("=" * 60)

            return {
                "status": "success",
                "document": document,
                "output_path": str(output_path),
                "processing_time_seconds": round(overall_elapsed, 3),
            }

        except (DocumentLoadError, PDFParseError, DOCXParseError, OCRError) as e:
            elapsed = time.time() - overall_start
            logger.error("Pipeline failed for {}: {}", filepath.name, e)
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
                "filepath": str(filepath),
                "processing_time_seconds": round(elapsed, 3),
            }

        except Exception as e:
            elapsed = time.time() - overall_start
            logger.exception("Unexpected pipeline error for {}: {}", filepath.name, e)
            return {
                "status": "error",
                "error": str(e),
                "error_type": "UnexpectedError",
                "filepath": str(filepath),
                "processing_time_seconds": round(elapsed, 3),
            }

    def _process_pdf(
        self, filepath: Path
    ) -> tuple[str, int, str, float | None]:
        """
        Process a PDF file — native extraction with OCR fallback.

        Returns:
            Tuple of (text, page_count, method, ocr_confidence).
        """
        # Try native extraction first
        result = self.pdf_parser.extract(filepath)
        pages = len(result.get("pages", []))

        if not result.get("needs_ocr", False):
            return result["full_text"], pages, "native", None

        # Run scan detection for detailed analysis
        logger.info("Native extraction empty — running scan detection...")
        scan_result = self.scan_detector.detect(filepath)

        if scan_result.get("is_scanned", True):
            logger.info("Confirmed scanned PDF — starting OCR...")
            ocr_result = self.ocr_engine.ocr_pdf(filepath)
            return (
                ocr_result["full_text"],
                ocr_result["metadata"]["num_pages"],
                "ocr",
                ocr_result["metadata"].get("avg_confidence"),
            )
        else:
            # Not scanned but still empty — use whatever we got
            logger.warning(
                "PDF not detected as scanned but text is empty"
            )
            return result["full_text"], pages, "native", None

    def _process_docx(self, filepath: Path) -> tuple[str, int]:
        """
        Process a DOCX file.

        Returns:
            Tuple of (text, page_count_estimate).
        """
        result = self.docx_parser.extract(filepath)
        text = result["full_text"]
        # Estimate pages from text length (avg ~3000 chars per page)
        estimated_pages = max(1, len(text) // 3000)
        return text, estimated_pages

    def process_directory(self, directory: str | Path) -> list[dict]:
        """
        Process all supported documents in a directory.

        Args:
            directory: Path to directory containing documents.

        Returns:
            List of processing results.
        """
        directory = Path(directory)
        if not directory.is_dir():
            logger.error("Not a directory: {}", directory)
            return []

        # Find all supported files
        supported_files: list[Path] = []
        for ext in Config.SUPPORTED_EXTENSIONS:
            supported_files.extend(directory.glob(f"*{ext}"))

        if not supported_files:
            logger.warning("No supported files found in {}", directory)
            return []

        logger.info(
            "Processing {} files from {}",
            len(supported_files),
            directory,
        )

        results: list[dict] = []
        for filepath in supported_files:
            result = self.process_file(filepath)
            results.append(result)

        # Summary
        successful = sum(1 for r in results if r["status"] == "success")
        failed = sum(1 for r in results if r["status"] == "error")
        logger.info(
            "Directory processing complete | total={} | success={} | failed={}",
            len(results),
            successful,
            failed,
        )

        return results

    def run_cuad_pipeline(self) -> dict:
        """
        Run the full CUAD dataset processing pipeline.

        Returns:
            Pipeline result summary.
        """
        from src.dataset.cuad_loader import CUADLoader
        from src.dataset.cuad_parser import CUADParser
        from src.dataset.cuad_exporter import CUADExporter

        logger.info("=" * 60)
        logger.info("CUAD DATASET PIPELINE START")
        logger.info("=" * 60)

        start_time = time.time()

        # Step 1: Load
        loader = CUADLoader()
        raw_data = loader.load()
        if raw_data is None:
            logger.error("Failed to load CUAD dataset")
            return {"status": "error", "error": "Dataset not found"}

        summary = loader.summary()
        logger.info("Dataset loaded: {}", summary)

        # Step 2: Inspect labels
        labels_df = loader.inspect_labels()
        logger.info("Label inspection:\n{}", labels_df.to_string())

        # Step 3: Parse
        parser = CUADParser()
        contracts = parser.parse_all(loader.articles)
        statistics = parser.get_clause_statistics()
        logger.info("Parse statistics: {}", statistics)

        # Step 4: Export
        exporter = CUADExporter()
        export_results = exporter.export_all(contracts, statistics)

        elapsed = time.time() - start_time

        logger.info("=" * 60)
        logger.info("CUAD PIPELINE COMPLETE")
        logger.info("  Contracts: {}", len(contracts))
        logger.info("  Exports:   {}", list(export_results.keys()))
        logger.info("  Time:      {:.2f}s", elapsed)
        logger.info("=" * 60)

        return {
            "status": "success",
            "contracts_parsed": len(contracts),
            "statistics": statistics,
            "exports": {k: str(v) for k, v in export_results.items()},
            "processing_time_seconds": round(elapsed, 3),
        }


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Data + OCR Pipeline — Contract Intelligence Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run.py --file uploads/sample.pdf
    python run.py --file uploads/contract.docx
    python run.py --dir uploads/
    python run.py --cuad
    python run.py --file uploads/scan.pdf --verbose
        """,
    )

    parser.add_argument(
        "--file",
        type=str,
        help="Path to a single document file to process",
    )
    parser.add_argument(
        "--dir",
        type=str,
        help="Path to a directory of documents to process",
    )
    parser.add_argument(
        "--cuad",
        action="store_true",
        help="Run the CUAD dataset processing pipeline",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Custom output directory for processed files",
    )

    args = parser.parse_args()

    # Validate arguments
    if not any([args.file, args.dir, args.cuad]):
        parser.print_help()
        sys.exit(1)

    # Initialize orchestrator
    orchestrator = PipelineOrchestrator()

    # Process based on mode
    if args.cuad:
        result = orchestrator.run_cuad_pipeline()
        print(json.dumps(result, indent=2, default=str))

    elif args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            logger.error("File not found: {}", filepath)
            sys.exit(1)

        result = orchestrator.process_file(filepath)
        print(json.dumps(result, indent=2, default=str))

        if result["status"] == "error":
            sys.exit(1)

    elif args.dir:
        dirpath = Path(args.dir)
        if not dirpath.is_dir():
            logger.error("Directory not found: {}", dirpath)
            sys.exit(1)

        results = orchestrator.process_directory(dirpath)
        summary = {
            "total": len(results),
            "success": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "error"),
            "results": results,
        }
        print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
