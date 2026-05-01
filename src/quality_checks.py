from __future__ import annotations

from typing import Dict, List

import pandas as pd


REQUIRED_COLUMNS = [
    "country",
    "year",
    "total_energy_consumption_twh",
    "per_capita_energy_use_kwh",
    "renewable_energy_share_pct",
    "fossil_fuel_dependency_pct",
    "industrial_energy_use_pct",
    "household_energy_use_pct",
    "carbon_emissions_million_tons",
    "energy_price_index_usd_per_kwh",
]


def run_quality_checks(df: pd.DataFrame) -> Dict[str, object]:
    checks: Dict[str, object] = {}

    checks["schema_consistent"] = all(col in df.columns for col in REQUIRED_COLUMNS)

    null_pct = (
        (df[REQUIRED_COLUMNS].isnull().sum() / len(df)).fillna(0).round(4).to_dict()
        if len(df) > 0
        else {col: 0 for col in REQUIRED_COLUMNS}
    )
    checks["null_percentage_by_column"] = null_pct

    checks["negative_energy_values"] = int((df["total_energy_consumption_twh"] < 0).sum())

    duplicate_country_year = int(df.duplicated(subset=["country", "year"]).sum())
    checks["duplicate_country_year_rows"] = duplicate_country_year

    if not checks["schema_consistent"]:
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        checks["missing_columns"] = missing

    return checks


def assert_quality_gate(checks: Dict[str, object]) -> None:
    if not checks.get("schema_consistent", False):
        raise ValueError("Quality check failed: schema is inconsistent.")
    if checks.get("negative_energy_values", 0) > 0:
        raise ValueError("Quality check failed: negative energy values found.")
    if checks.get("duplicate_country_year_rows", 0) > 0:
        raise ValueError("Quality check failed: duplicate country-year rows found.")
