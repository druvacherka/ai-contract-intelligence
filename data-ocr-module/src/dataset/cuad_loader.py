"""
CUAD Dataset Loader.

Downloads (or loads from disk) the Contract Understanding Atticus Dataset,
inspects labels, and provides access to raw training/test data.
"""

import json
import zipfile
from pathlib import Path
from typing import Any

import pandas as pd
from tqdm import tqdm

from src.utils.config import Config
from src.utils.logger import logger


# The 41 CUAD clause types
CUAD_CLAUSE_TYPES: list[str] = [
    "Document Name",
    "Parties",
    "Agreement Date",
    "Effective Date",
    "Expiration Date",
    "Renewal Term",
    "Notice Period To Terminate Renewal",
    "Governing Law",
    "Most Favored Nation",
    "Non-Compete",
    "Exclusivity",
    "No-Solicit Of Customers",
    "Competitive Restriction Exception",
    "No-Solicit Of Employees",
    "Non-Disparagement",
    "Termination For Convenience",
    "Rofr/Rofo/Rofn",
    "Change Of Control",
    "Anti-Assignment",
    "Revenue/Profit Sharing",
    "Price Restrictions",
    "Minimum Commitment",
    "Volume Restriction",
    "Ip Ownership Assignment",
    "Joint Ip Ownership",
    "License Grant",
    "Non-Transferable License",
    "Affiliate License-Licensor",
    "Affiliate License-Licensee",
    "Unlimited/All-You-Can-Eat-License",
    "Irrevocable Or Perpetual License",
    "Source Code Escrow",
    "Post-Termination Services",
    "Audit Rights",
    "Uncapped Liability",
    "Cap On Liability",
    "Liquidated Damages",
    "Warranty Duration",
    "Insurance",
    "Covenant Not To Sue",
    "Third Party Beneficiary",
]


class CUADLoader:
    """
    Loads and inspects the CUAD dataset from local disk.

    Expects the CUAD dataset to be placed in the configured raw directory
    as a JSON file (CUADv1.json) in SQuAD format.
    """

    def __init__(
        self,
        dataset_path: Path | None = None,
        output_path: Path | None = None,
    ) -> None:
        self.dataset_path = dataset_path or Config.CUAD_DATASET_PATH
        self.output_path = output_path or Config.CUAD_OUTPUT_PATH
        self.raw_data: dict[str, Any] | None = None
        self._articles: list[dict[str, Any]] = []

        # Ensure output directory exists
        self.output_path.mkdir(parents=True, exist_ok=True)

        logger.info(
            "CUADLoader initialized | dataset_path={} | output_path={}",
            self.dataset_path,
            self.output_path,
        )

    def find_dataset_file(self) -> Path | None:
        """Locate the CUAD JSON file in the dataset directory."""
        search_dir = Path(self.dataset_path)

        # Check for common CUAD filenames
        candidates = [
            "CUADv1.json",
            "CUAD_v1.json",
            "cuad_v1.json",
            "cuadv1.json",
            "train.json",
        ]

        for name in candidates:
            filepath = search_dir / name
            if filepath.exists():
                logger.info("Found CUAD dataset file: {}", filepath)
                return filepath

        # Fallback: search for any .json file in the directory
        json_files = list(search_dir.glob("*.json"))
        if json_files:
            logger.info("Found JSON file in dataset dir: {}", json_files[0])
            return json_files[0]

        logger.warning("No CUAD dataset file found in {}", search_dir)
        return None

    def extract_zip(self, zip_path: Path) -> Path | None:
        """Extract a CUAD zip archive to the raw directory."""
        logger.info("Extracting ZIP archive: {}", zip_path)
        try:
            with zipfile.ZipFile(str(zip_path), "r") as zf:
                zf.extractall(str(self.dataset_path))
                logger.info(
                    "Extracted {} files from archive", len(zf.namelist())
                )
            return self.find_dataset_file()
        except zipfile.BadZipFile:
            logger.error("Corrupted ZIP file: {}", zip_path)
            return None

    def load(self) -> dict[str, Any] | None:
        """
        Load the CUAD dataset from disk.

        Returns:
            The raw dataset dictionary in SQuAD format, or None if not found.
        """
        dataset_file = self.find_dataset_file()

        # Try ZIP extraction as fallback
        if dataset_file is None:
            zip_files = list(Path(self.dataset_path).glob("*.zip"))
            if zip_files:
                logger.info("Attempting to extract from ZIP: {}", zip_files[0])
                dataset_file = self.extract_zip(zip_files[0])

        if dataset_file is None:
            logger.error(
                "CUAD dataset not found. Please place CUADv1.json in: {}",
                self.dataset_path,
            )
            return None

        logger.info("Loading CUAD dataset from: {}", dataset_file)
        try:
            with open(dataset_file, "r", encoding="utf-8") as f:
                self.raw_data = json.load(f)

            self._articles = self.raw_data.get("data", [])
            logger.info(
                "CUAD dataset loaded | version={} | articles={}",
                self.raw_data.get("version", "unknown"),
                len(self._articles),
            )
            return self.raw_data

        except json.JSONDecodeError as e:
            logger.error("Failed to parse CUAD JSON: {}", e)
            return None
        except Exception as e:
            logger.error("Unexpected error loading CUAD dataset: {}", e)
            return None

    @property
    def articles(self) -> list[dict[str, Any]]:
        """Return the list of contract articles."""
        return self._articles

    @property
    def num_contracts(self) -> int:
        """Return the number of contracts in the dataset."""
        return len(self._articles)

    def get_contract(self, index: int) -> dict[str, Any] | None:
        """Get a specific contract by index."""
        if 0 <= index < len(self._articles):
            return self._articles[index]
        logger.warning("Contract index {} out of range (0-{})", index, len(self._articles) - 1)
        return None

    def inspect_labels(self) -> pd.DataFrame:
        """
        Inspect and summarize all clause types in the dataset.

        Returns:
            DataFrame with clause type statistics.
        """
        if not self._articles:
            logger.warning("No data loaded. Call load() first.")
            return pd.DataFrame()

        label_counts: dict[str, int] = {clause: 0 for clause in CUAD_CLAUSE_TYPES}
        total_annotations = 0

        for article in tqdm(self._articles, desc="Inspecting labels"):
            paragraphs = article.get("paragraphs", [])
            for para in paragraphs:
                qas = para.get("qas", [])
                for qa in qas:
                    question = qa.get("question", "")
                    answers = qa.get("answers", [])

                    # Match question to clause type
                    for clause_type in CUAD_CLAUSE_TYPES:
                        if clause_type.lower() in question.lower():
                            label_counts[clause_type] += len(answers)
                            total_annotations += len(answers)
                            break

        # Build summary DataFrame
        df = pd.DataFrame(
            [
                {
                    "clause_type": k,
                    "annotation_count": v,
                    "has_annotations": v > 0,
                }
                for k, v in label_counts.items()
            ]
        )
        df = df.sort_values("annotation_count", ascending=False).reset_index(drop=True)

        logger.info(
            "Label inspection complete | total_annotations={} | clause_types_with_data={}",
            total_annotations,
            df["has_annotations"].sum(),
        )
        return df

    def get_contract_texts(self) -> list[dict[str, str]]:
        """
        Extract all contract texts with their titles.

        Returns:
            List of dicts with 'title' and 'text' keys.
        """
        contracts: list[dict[str, str]] = []
        for article in self._articles:
            title = article.get("title", "untitled")
            paragraphs = article.get("paragraphs", [])
            full_text = "\n\n".join(
                p.get("context", "") for p in paragraphs
            )
            contracts.append({"title": title, "text": full_text})

        logger.info("Extracted {} contract texts", len(contracts))
        return contracts

    def summary(self) -> dict[str, Any]:
        """Return a summary of the loaded dataset."""
        if not self.raw_data:
            return {"status": "not_loaded"}

        return {
            "version": self.raw_data.get("version", "unknown"),
            "num_contracts": len(self._articles),
            "clause_types": len(CUAD_CLAUSE_TYPES),
            "total_paragraphs": sum(
                len(a.get("paragraphs", [])) for a in self._articles
            ),
        }
