from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
from sqlalchemy import create_engine


def _read_pipeline_state(metadata_path: Path) -> Dict[str, int]:
    if metadata_path.exists():
        return json.loads(metadata_path.read_text(encoding="utf-8"))
    return {"last_processed_year": 0}


def _write_pipeline_state(metadata_path: Path, last_processed_year: int) -> None:
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        json.dumps({"last_processed_year": int(last_processed_year)}, indent=2),
        encoding="utf-8",
    )


def load_curated_tables(
    cleaned_df: pd.DataFrame,
    yearly_df: pd.DataFrame,
    database_url: str,
    curated_dir: Path,
    metadata_path: Path,
) -> Tuple[str, Dict[str, int]]:
    curated_dir.mkdir(parents=True, exist_ok=True)

    state = _read_pipeline_state(metadata_path)
    last_processed_year = int(state.get("last_processed_year", 0))

    incremental_df = cleaned_df[cleaned_df["year"] > last_processed_year].copy()
    incremental_yearly_df = yearly_df[yearly_df["year"] > last_processed_year].copy()

    country_summary_df = (
        incremental_df.groupby("country", as_index=False)
        .agg(
            latest_year=("year", "max"),
            total_energy_consumption_twh=("total_energy_consumption_twh", "sum"),
            avg_per_capita_energy_use_kwh=("per_capita_energy_use_kwh", "mean"),
            avg_renewable_energy_share_pct=("renewable_energy_share_pct", "mean"),
            total_carbon_emissions_million_tons=("carbon_emissions_million_tons", "sum"),
        )
        .sort_values(["latest_year", "country"])
    )

    engine = create_engine(database_url)
    with engine.begin() as conn:
        incremental_df.to_sql("energy_fact", conn, if_exists="append", index=False)
        country_summary_df.to_sql("country_energy_summary", conn, if_exists="append", index=False)
        incremental_yearly_df.to_sql("yearly_consumption", conn, if_exists="append", index=False)

    if not incremental_df.empty:
        new_last_processed_year = int(incremental_df["year"].max())
    else:
        new_last_processed_year = last_processed_year

    _write_pipeline_state(metadata_path, new_last_processed_year)

    # Curated file outputs are full snapshots for easy local inspection,
    # while warehouse loading remains incremental.
    full_country_summary_df = (
        cleaned_df.groupby("country", as_index=False)
        .agg(
            latest_year=("year", "max"),
            total_energy_consumption_twh=("total_energy_consumption_twh", "sum"),
            avg_per_capita_energy_use_kwh=("per_capita_energy_use_kwh", "mean"),
            avg_renewable_energy_share_pct=("renewable_energy_share_pct", "mean"),
            total_carbon_emissions_million_tons=("carbon_emissions_million_tons", "sum"),
        )
        .sort_values(["latest_year", "country"])
    )

    cleaned_df.to_csv(curated_dir / "energy_fact.csv", index=False)
    full_country_summary_df.to_csv(curated_dir / "country_energy_summary.csv", index=False)
    yearly_df.to_csv(curated_dir / "yearly_consumption.csv", index=False)

    load_stats = {
        "rows_loaded_energy_fact": len(incremental_df),
        "rows_loaded_country_energy_summary": len(country_summary_df),
        "rows_loaded_yearly_consumption": len(incremental_yearly_df),
        "last_processed_year_previous": last_processed_year,
        "last_processed_year_current": new_last_processed_year,
    }

    return database_url, load_stats
