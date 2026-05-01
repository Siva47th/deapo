from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from src.extract import extract_raw_data
from src.load import load_curated_tables
from src.quality_checks import assert_quality_gate, run_quality_checks
from src.transform import save_processed_outputs, transform_data


EXPECTED_COLUMNS = [
    "Country",
    "Year",
    "Total Energy Consumption (TWh)",
    "Per Capita Energy Use (kWh)",
    "Renewable Energy Share (%)",
    "Fossil Fuel Dependency (%)",
    "Industrial Energy Use (%)",
    "Household Energy Use (%)",
    "Carbon Emissions (Million Tons)",
    "Energy Price Index (USD/kWh)",
]

DEFAULT_DATABASE_URL = "postgresql+psycopg2://postgres:ezhumalai@1234@localhost:5432/energy_warehouse"


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    load_dotenv(base_dir / ".env")

    source_path = base_dir / "global_energy_consumption.csv"
    raw_output_path = base_dir / "data" / "raw" / "global_energy_consumption_raw.csv"
    processed_dir = base_dir / "data" / "processed"
    curated_dir = base_dir / "data" / "curated"
    metadata_dir = base_dir / "data" / "metadata"
    database_url = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

    extract_stats = extract_raw_data(source_path, raw_output_path, EXPECTED_COLUMNS)

    transform_result = transform_data(raw_output_path)
    quality_checks = run_quality_checks(transform_result.cleaned_df)
    quality_checks.update(transform_result.quality_summary)
    assert_quality_gate(quality_checks)

    cleaned_output_path, yearly_output_path = save_processed_outputs(
        transform_result.cleaned_df,
        transform_result.yearly_df,
        processed_dir,
    )

    warehouse_target, load_stats = load_curated_tables(
        cleaned_df=transform_result.cleaned_df,
        yearly_df=transform_result.yearly_df,
        database_url=database_url,
        curated_dir=curated_dir,
        metadata_path=metadata_dir / "pipeline_state.json",
    )

    ingest_metadata = {
        "pipeline_name": "energy_batch_etl",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source_path": str(source_path),
        "raw_output_path": str(raw_output_path),
        "raw_row_count": extract_stats["row_count"],
        "raw_column_count": extract_stats["column_count"],
        "processed_clean_output": str(cleaned_output_path),
        "processed_yearly_output": str(yearly_output_path),
        "warehouse_target": warehouse_target,
        "quality_checks": quality_checks,
        "load_stats": load_stats,
    }

    metadata_dir.mkdir(parents=True, exist_ok=True)
    run_meta_path = metadata_dir / "last_run_metadata.json"
    run_meta_path.write_text(json.dumps(ingest_metadata, indent=2), encoding="utf-8")

    print("Pipeline completed successfully.")
    print(f"Warehouse target: {warehouse_target}")
    print(f"Run metadata: {run_meta_path}")


if __name__ == "__main__":
    main()
