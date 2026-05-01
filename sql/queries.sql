-- Top 10 countries by total energy consumption.
SELECT country, SUM(total_energy_consumption_twh) AS total_twh
FROM energy_fact
GROUP BY country
ORDER BY total_twh DESC
LIMIT 10;

-- Yearly global consumption and emissions trend.
SELECT year,
       total_energy_consumption_twh,
       total_carbon_emissions_million_tons,
       avg_renewable_energy_share_pct
FROM yearly_consumption
ORDER BY year;

-- Latest country-level KPI snapshot.
SELECT country,
       latest_year,
       total_energy_consumption_twh,
       avg_per_capita_energy_use_kwh,
       avg_renewable_energy_share_pct
FROM country_energy_summary
ORDER BY latest_year DESC, country;
