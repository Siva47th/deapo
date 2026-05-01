from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def fetch_and_print(conn, table: str, limit: int = 5) -> None:
    count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()
    print(f"\n[{table}] total_rows={count}")
    rows = conn.execute(text(f"SELECT * FROM {table} LIMIT :limit"), {"limit": limit}).fetchall()
    for row in rows:
        print(dict(row._mapping))


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    load_dotenv(base_dir / ".env")
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is missing. Set it in .env")

    engine = create_engine(database_url)
    with engine.connect() as conn:
        for table in ["energy_fact", "country_energy_summary", "yearly_consumption"]:
            fetch_and_print(conn, table)


if __name__ == "__main__":
    main()
