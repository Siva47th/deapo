# ETL Energy Project

Designed and implemented a batch ETL pipeline to process raw energy consumption data into analytics-ready tables.

## Data Source Description
- Source type: Flat file (CSV)
- Domain: Energy consumption
- Nature: Raw, uncleaned, historical data
- Update pattern: Batch (static or periodic)

## Problem Statement
Raw energy consumption data is not directly suitable for analysis due to inconsistencies and lack of aggregation.

## Objective
To design an ETL pipeline that ingests raw energy data, performs transformations, and loads analytics-ready tables for reporting.

## Tools Used
Python, Pandas, SQL, PostgreSQL

## Architecture
```text
Data Source (Global Energy CSV)
  -> Extract Layer (Python + schema validation + metadata capture)
  -> Bronze Layer (raw immutable CSV)
  -> Transformation Layer (cleaning, casting, business rules, feature derivation)
  -> Silver Layer (standardized cleaned dataset in Parquet/CSV)
  -> Gold Layer (country summary + yearly KPIs)
  -> Data Warehouse (PostgreSQL tables)
  -> Analytics Layer (SQL / BI dashboards)
```

## Folder Structure
```text
etl-energy-project/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── curated/
│   └── metadata/
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── quality_checks.py
├── sql/
│   ├── schema.sql
│   └── queries.sql
├── .env.example
├── run_pipeline.py
├── requirements.txt
└── README.md
```

## ETL Flow
1. Extract
- Reads `global_energy_consumption.csv`
- Validates expected schema
- Copies unchanged raw file to `data/raw/global_energy_consumption_raw.csv`

2. Transform
- Cleans nulls and duplicates
- Casts numeric datatypes
- Renames columns to snake_case
- Derives `total_energy_consumption_kwh`
- Produces Silver outputs in `data/processed/`

3. Load
- Loads curated Gold tables into PostgreSQL:
  - `energy_fact`
  - `country_energy_summary`
  - `yearly_consumption`
- Performs incremental loading using `last_processed_year` in `data/metadata/pipeline_state.json`

## Data Quality Checks
The pipeline validates:
- Null percentages by column
- Negative energy values
- Duplicate country-year rows
- Schema consistency
- Row count before vs after transform

Quality and run metadata are stored at:
- `data/metadata/last_run_metadata.json`

## PostgreSQL Configure
1. Copy `.env.example` to `.env`.
2. Update `DATABASE_URL` in `.env`.

Example:
```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/energy_warehouse
```

If `.env` is missing, pipeline uses default:
`postgresql+psycopg2://postgres:postgres@localhost:5432/energy_warehouse`

## Run Instructions
1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Run pipeline:
```bash
python run_pipeline.py
```

## Resume Line
Implemented a batch ETL pipeline using Python and SQL to process global energy consumption data, including raw data ingestion, transformation, incremental loading, and analytics-ready table creation.
