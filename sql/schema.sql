CREATE TABLE IF NOT EXISTS energy_fact (
    country TEXT NOT NULL,
    year INTEGER NOT NULL,
    total_energy_consumption_twh REAL,
    per_capita_energy_use_kwh REAL,
    renewable_energy_share_pct REAL,
    fossil_fuel_dependency_pct REAL,
    industrial_energy_use_pct REAL,
    household_energy_use_pct REAL,
    carbon_emissions_million_tons REAL,
    energy_price_index_usd_per_kwh REAL,
    total_energy_consumption_kwh REAL
);

CREATE TABLE IF NOT EXISTS country_energy_summary (
    country TEXT NOT NULL,
    latest_year INTEGER,
    total_energy_consumption_twh REAL,
    avg_per_capita_energy_use_kwh REAL,
    avg_renewable_energy_share_pct REAL,
    total_carbon_emissions_million_tons REAL
);

CREATE TABLE IF NOT EXISTS yearly_consumption (
    year INTEGER NOT NULL,
    total_energy_consumption_twh REAL,
    avg_per_capita_energy_use_kwh REAL,
    total_carbon_emissions_million_tons REAL,
    avg_renewable_energy_share_pct REAL
);
