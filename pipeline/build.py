from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import duckdb

from .config import Settings


PUBLISHED_TABLES = (
    "build_metadata",
    "dim_customers",
    "dim_date",
    "dim_geography",
    "dim_products",
    "dim_sellers",
    "fact_order_items",
    "fact_orders",
    "fact_payments",
    "fact_reviews",
    "mart_cohorts",
    "mart_customer_orders",
    "mart_customers",
    "mart_orders",
    "mart_sales_lines",
)


def _sql(path: Path, settings: Settings) -> str:
    raw_dir = settings.raw_dir.as_posix().replace("'", "''")
    return path.read_text(encoding="utf-8").replace("{{RAW_DIR}}", raw_dir)


def build_database(settings: Settings) -> None:
    sql_dir = settings.root / "sql"
    if settings.build_duckdb_path.exists():
        settings.build_duckdb_path.unlink()
    with duckdb.connect(str(settings.build_duckdb_path)) as connection:
        connection.execute("PRAGMA threads=4")
        connection.execute(_sql(sql_dir / "01_model.sql", settings))
        connection.execute(_sql(sql_dir / "02_marts.sql", settings))
        connection.execute(
            """
            create or replace table build_metadata as
            select
                ?::timestamp as built_at_utc,
                date '2016-09-04' as source_start_date,
                date '2018-08-31' as analysis_end_date,
                'Olist Brazilian E-Commerce Public Dataset' as source_name,
                'CC BY-NC-SA 4.0' as source_license
            """,
            [datetime.now(timezone.utc).replace(tzinfo=None)],
        )
        counts = {
            name: connection.execute(f"select count(*) from {name}").fetchone()[0]
            for name in (
                "fact_orders",
                "fact_order_items",
                "fact_payments",
                "mart_orders",
                "mart_sales_lines",
                "mart_customers",
                "mart_cohorts",
            )
        }

        for table in ("mart_orders", "mart_sales_lines", "mart_customers", "mart_cohorts"):
            target = (settings.processed_dir / f"{table}.parquet").as_posix().replace("'", "''")
            connection.execute(
                f"copy {table} to '{target}' (format parquet, compression zstd, overwrite true)"
            )

    if settings.duckdb_path.exists():
        settings.duckdb_path.unlink()
    with duckdb.connect(str(settings.duckdb_path)) as published:
        source = settings.build_duckdb_path.as_posix().replace("'", "''")
        published.execute(f"attach '{source}' as source (read_only)")
        for table in PUBLISHED_TABLES:
            published.execute(f"create table {table} as select * from source.{table}")
        published.execute("detach source")
        published.execute("checkpoint")

    manifest = {
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "build_database": str(settings.build_duckdb_path),
        "published_database": str(settings.duckdb_path),
        "tables": counts,
    }
    (settings.processed_dir / "build_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))
