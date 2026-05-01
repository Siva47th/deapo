# ETL Project Report: Global Energy Consumption

## Project Title
Batch ETL Pipeline for Global Energy Consumption Analytics

## Problem Statement
Raw energy consumption data is not directly suitable for analytics due to inconsistent formatting, missing-value risk, duplicate records, and absence of business-level aggregates.

## Objective
Design and implement a batch ETL pipeline that ingests raw energy data, applies transformation and quality controls, and loads analytics-ready fact and summary tables into PostgreSQL.

## Data Source Description
- Source type: Flat file (CSV)
- Domain: Energy consumption
- Nature: Raw, uncleaned, historical data
- Update pattern: Batch (static or periodic)
- File: `global_energy_consumption.csv`

## Architecture
```text
Data Source (Global Energy CSV)
  -> Extract Layer (Python + schema validation + metadata capture)
  -> Bronze Layer (raw immutable CSV)
  -> Transformation Layer (cleaning, casting, business rules, derivations)
  -> Silver Layer (cleaned standardized dataset in Parquet/CSV)
  -> Gold Layer (country and yearly aggregations)
  -> Data Warehouse (PostgreSQL)
  -> Analytics Layer (SQL queries / dashboards)
```

## ETL Pipeline Design

### 1. Extract
- Reads `global_energy_consumption.csv`
- Validates expected schema and column presence
- Writes unchanged copy to Bronze:
  - `data/raw/global_energy_consumption_raw.csv`
- Captures extraction metadata (rows, columns, paths)

### 2. Transform
- Renames fields to `snake_case`
- Converts numeric columns to proper datatypes
- Removes duplicate `country-year` records
- Handles missing values with median strategy
- Enforces business rule: no negative total energy values
- Derives metric:
  - `total_energy_consumption_kwh = total_energy_consumption_twh * 1,000,000,000`
- Creates yearly aggregated dataset
- Writes Silver outputs:
  - `data/processed/energy_clean.parquet`
  - `data/processed/yearly_consumption.csv`

### 3. Load
- Incrementally loads curated data into PostgreSQL tables:
  - `energy_fact`
  - `country_energy_summary`
  - `yearly_consumption`
- Uses metadata watermark (`last_processed_year`) to simulate incremental loading
- Persists incremental state:
  - `data/metadata/pipeline_state.json`

## Incremental Loading Logic
- On each run, pipeline reads `last_processed_year`
- Loads only rows where `year > last_processed_year`
- Updates watermark after successful load
- This supports idempotent re-runs and avoids duplicate inserts for already-processed years

## Data Quality Checks Implemented
- Schema consistency validation
- Null percentage by required column
- Negative energy value checks
- Duplicate `country-year` checks
- Row count before vs after transformation

## Output Artifacts

### Bronze
- `data/raw/global_energy_consumption_raw.csv`

### Silver
- `data/processed/energy_clean.parquet`
- `data/processed/yearly_consumption.csv`

### Gold (Files)
- `data/curated/energy_fact.csv`
- `data/curated/country_energy_summary.csv`
- `data/curated/yearly_consumption.csv`

### Gold (Warehouse)
- PostgreSQL database: `energy_warehouse`
- Tables: `energy_fact`, `country_energy_summary`, `yearly_consumption`

### Metadata
- `data/metadata/last_run_metadata.json`
- `data/metadata/pipeline_state.json`

## Tools and Technologies
- Python
- Pandas
- SQLAlchemy
- PostgreSQL
- SQL

## Sample Analytics Use Cases
- Year-over-year global energy trends
- Country-wise total consumption ranking
- Renewable share and emissions trend analysis

## Resume Line
Implemented a batch ETL pipeline using Python and SQL to process global energy consumption data, including raw data ingestion, transformation, incremental loading, and analytics-ready table creation.

## Conclusion
This project is a complete ETL implementation (not just dataset cleaning): it includes layered architecture (Bronze/Silver/Gold), orchestration, incremental load simulation, metadata capture, data quality gates, and warehouse-ready outputs for analytics.
