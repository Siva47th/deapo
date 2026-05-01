import shutil
from pathlib import Path
from typing import Dict, List

import pandas as pd


def validate_schema(df: pd.DataFrame, expected_columns: List[str]) -> None:
    missing = [col for col in expected_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Schema validation failed. Missing columns: {missing}")


def extract_raw_data(
    source_path: Path,
    raw_output_path: Path,
    expected_columns: List[str],
) -> Dict[str, int]:
    """
    Extracts dataset and stores it in bronze/raw layer unchanged.
    """
    if not source_path.exists():
        raise FileNotFoundError(f"Source dataset not found: {source_path}")

    raw_output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(source_path)
    validate_schema(df, expected_columns)

    # Preserve source exactly in raw layer for lineage and reprocessing.
    shutil.copy2(source_path, raw_output_path)

    return {
        "row_count": len(df),
        "column_count": len(df.columns),
    }
