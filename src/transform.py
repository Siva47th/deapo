from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd


@dataclass
class TransformResult:
    cleaned_df: pd.DataFrame
    yearly_df: pd.DataFrame
    quality_summary: Dict[str, object]


def _to_snake_case_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "Country": "country",
        "Year": "year",
        "Total Energy Consumption (TWh)": "total_energy_consumption_twh",
        "Per Capita Energy Use (kWh)": "per_capita_energy_use_kwh",
        "Renewable Energy Share (%)": "renewable_energy_share_pct",
        "Fossil Fuel Dependency (%)": "fossil_fuel_dependency_pct",
        "Industrial Energy Use (%)": "industrial_energy_use_pct",
        "Household Energy Use (%)": "household_energy_use_pct",
        "Carbon Emissions (Million Tons)": "carbon_emissions_million_tons",
        "Energy Price Index (USD/kWh)": "energy_price_index_usd_per_kwh",
    }
    return df.rename(columns=rename_map)


def _run_transformations(df: pd.DataFrame) -> pd.DataFrame:
    df = _to_snake_case_columns(df)

    numeric_cols = [
        "total_energy_consumption_twh",
        "per_capita_energy_use_kwh",
        "renewable_energy_share_pct",
        "fossil_fuel_dependency_pct",
        "industrial_energy_use_pct",
        "household_energy_use_pct",
        "carbon_emissions_million_tons",
        "energy_price_index_usd_per_kwh",
    ]

    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["country"] = df["country"].astype(str).str.strip()

    df = df.drop_duplicates(subset=["country", "year"])

    # Fill missing numeric values with median per column for batch analytics use.
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

    df = df.dropna(subset=["country", "year"])
    df = df[df["total_energy_consumption_twh"] >= 0]

    # Derived metric: convert total TWh to annual kWh for compatibility with per-capita KPI.
    df["total_energy_consumption_kwh"] = df["total_energy_consumption_twh"] * 1_000_000_000

    return df


def transform_data(raw_input_path: Path) -> TransformResult:
    raw_df = pd.read_csv(raw_input_path)
    row_count_before = len(raw_df)

    cleaned_df = _run_transformations(raw_df)
    row_count_after = len(cleaned_df)

    yearly_df = (
        cleaned_df.groupby("year", as_index=False)
        .agg(
            total_energy_consumption_twh=("total_energy_consumption_twh", "sum"),
            avg_per_capita_energy_use_kwh=("per_capita_energy_use_kwh", "mean"),
            total_carbon_emissions_million_tons=("carbon_emissions_million_tons", "sum"),
            avg_renewable_energy_share_pct=("renewable_energy_share_pct", "mean"),
        )
        .sort_values("year")
    )

    quality_summary = {
        "row_count_before_transform": row_count_before,
        "row_count_after_transform": row_count_after,
    }

    return TransformResult(
        cleaned_df=cleaned_df,
        yearly_df=yearly_df,
        quality_summary=quality_summary,
    )


def save_processed_outputs(
    cleaned_df: pd.DataFrame,
    yearly_df: pd.DataFrame,
    processed_dir: Path,
) -> Tuple[Path, Path]:
    processed_dir.mkdir(parents=True, exist_ok=True)

    cleaned_parquet = processed_dir / "energy_clean.parquet"
    cleaned_csv_fallback = processed_dir / "energy_clean.csv"
    yearly_output = processed_dir / "yearly_consumption.csv"

    try:
        cleaned_df.to_parquet(cleaned_parquet, index=False)
        cleaned_output = cleaned_parquet
    except Exception:
        cleaned_df.to_csv(cleaned_csv_fallback, index=False)
        cleaned_output = cleaned_csv_fallback

    yearly_df.to_csv(yearly_output, index=False)
    return cleaned_output, yearly_output
