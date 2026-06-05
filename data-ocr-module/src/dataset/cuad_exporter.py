"""
CUAD Dataset Exporter.

Exports parsed CUAD contracts to training-ready JSON, CSV, and
individual contract files for downstream NLP consumption.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from tqdm import tqdm

from src.utils.config import Config
from src.utils.logger import logger


class CUADExporter:
    """
    Exports parsed CUAD contract data into multiple output formats
    suitable for NLP model training and analysis.
    """

    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or Config.EXPORT_PATH
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("CUADExporter initialized | output_dir={}", self.output_dir)

    def _generate_export_metadata(
        self, num_contracts: int, export_format: str
    ) -> dict[str, Any]:
        """Generate metadata header for export files."""
        return {
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "pipeline_version": "1.0.0",
            "dataset": "CUAD_v1",
            "num_contracts": num_contracts,
            "export_format": export_format,
        }

    def export_training_json(
        self,
        contracts: list[dict[str, Any]],
        filename: str = "cuad_training_data.json",
    ) -> Path:
        """
        Export all contracts as a single training-ready JSON file.

        Schema per contract:
        {
            "contract_id": "",
            "text": "",
            "clauses": [
                {"type": "", "start": 0, "end": 0, "text": ""}
            ]
        }

        Args:
            contracts: List of parsed contract dicts.
            filename: Output filename.

        Returns:
            Path to the exported file.
        """
        logger.info("Exporting {} contracts to training JSON", len(contracts))

        # Build training-ready records (strip extra metadata)
        training_records: list[dict[str, Any]] = []
        for contract in tqdm(contracts, desc="Formatting for export"):
            record = {
                "contract_id": contract["contract_id"],
                "text": contract["text"],
                "clauses": [
                    {
                        "type": clause["type"],
                        "start": clause["start"],
                        "end": clause["end"],
                        "text": clause["text"],
                    }
                    for clause in contract.get("clauses", [])
                ],
            }
            training_records.append(record)

        output_data = {
            "metadata": self._generate_export_metadata(
                len(training_records), "training_json"
            ),
            "contracts": training_records,
        }

        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        size_mb = output_path.stat().st_size / (1024 * 1024)
        logger.info(
            "Training JSON exported | file={} | size={:.2f}MB | contracts={}",
            output_path,
            size_mb,
            len(training_records),
        )
        return output_path

    def export_individual_contracts(
        self,
        contracts: list[dict[str, Any]],
        subdir: str = "individual",
    ) -> Path:
        """
        Export each contract as a separate JSON file.

        Args:
            contracts: List of parsed contract dicts.
            subdir: Subdirectory name within the output directory.

        Returns:
            Path to the output subdirectory.
        """
        individual_dir = self.output_dir / subdir
        individual_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "Exporting {} individual contracts to {}",
            len(contracts),
            individual_dir,
        )

        for contract in tqdm(contracts, desc="Exporting contracts"):
            cid = contract["contract_id"]
            safe_title = (
                contract.get("title", cid)
                .replace("/", "_")
                .replace("\\", "_")
                .replace(" ", "_")[:80]
            )
            filename = f"{safe_title}_{cid[:8]}.json"

            record = {
                "contract_id": contract["contract_id"],
                "title": contract.get("title", ""),
                "text": contract["text"],
                "clauses": contract.get("clauses", []),
                "metadata": contract.get("metadata", {}),
            }

            filepath = individual_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False, indent=2)

        logger.info(
            "Individual contracts exported | dir={} | count={}",
            individual_dir,
            len(contracts),
        )
        return individual_dir

    def export_clause_csv(
        self,
        contracts: list[dict[str, Any]],
        filename: str = "cuad_clauses.csv",
    ) -> Path:
        """
        Export all clauses as a flat CSV for analysis.

        Args:
            contracts: List of parsed contract dicts.
            filename: Output CSV filename.

        Returns:
            Path to the exported CSV.
        """
        logger.info("Exporting clause CSV for {} contracts", len(contracts))

        rows: list[dict[str, Any]] = []
        for contract in contracts:
            for clause in contract.get("clauses", []):
                rows.append(
                    {
                        "contract_id": contract["contract_id"],
                        "contract_title": contract.get("title", ""),
                        "clause_type": clause["type"],
                        "clause_start": clause["start"],
                        "clause_end": clause["end"],
                        "clause_text": clause["text"],
                        "clause_length": len(clause["text"]),
                    }
                )

        df = pd.DataFrame(rows)
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False, encoding="utf-8")

        logger.info(
            "Clause CSV exported | file={} | rows={} | columns={}",
            output_path,
            len(df),
            list(df.columns),
        )
        return output_path

    def export_summary_report(
        self,
        contracts: list[dict[str, Any]],
        statistics: dict[str, Any] | None = None,
        filename: str = "cuad_summary_report.json",
    ) -> Path:
        """
        Export a summary report of the parsed dataset.

        Args:
            contracts: List of parsed contract dicts.
            statistics: Optional pre-computed statistics.
            filename: Output filename.

        Returns:
            Path to the summary report.
        """
        # Compute basic stats if not provided
        if statistics is None:
            total_clauses = sum(len(c.get("clauses", [])) for c in contracts)
            clause_type_counts: dict[str, int] = {}
            for contract in contracts:
                for clause in contract.get("clauses", []):
                    ctype = clause["type"]
                    clause_type_counts[ctype] = clause_type_counts.get(ctype, 0) + 1

            statistics = {
                "total_contracts": len(contracts),
                "total_clauses": total_clauses,
                "avg_clauses_per_contract": round(
                    total_clauses / max(len(contracts), 1), 2
                ),
                "clause_type_distribution": clause_type_counts,
            }

        report = {
            "metadata": self._generate_export_metadata(len(contracts), "summary_report"),
            "statistics": statistics,
            "contract_summaries": [
                {
                    "contract_id": c["contract_id"],
                    "title": c.get("title", ""),
                    "text_length": len(c["text"]),
                    "num_clauses": len(c.get("clauses", [])),
                    "clause_types": list(
                        set(cl["type"] for cl in c.get("clauses", []))
                    ),
                }
                for c in contracts
            ],
        }

        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info("Summary report exported to {}", output_path)
        return output_path

    def export_all(
        self,
        contracts: list[dict[str, Any]],
        statistics: dict[str, Any] | None = None,
    ) -> dict[str, Path]:
        """
        Run all export operations.

        Args:
            contracts: List of parsed contract dicts.
            statistics: Optional pre-computed statistics.

        Returns:
            Dict mapping export type to output path.
        """
        logger.info("Running full export pipeline for {} contracts", len(contracts))

        results = {
            "training_json": self.export_training_json(contracts),
            "individual_contracts": self.export_individual_contracts(contracts),
            "clause_csv": self.export_clause_csv(contracts),
            "summary_report": self.export_summary_report(contracts, statistics),
        }

        logger.info("Full export complete | outputs={}", list(results.keys()))
        return results
