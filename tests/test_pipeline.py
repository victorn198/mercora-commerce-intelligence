from __future__ import annotations

import duckdb

from pipeline.config import Settings
from pipeline.validate import run_validation


def test_quality_contract_passes():
    report = run_validation(Settings.load(), fail_on_error=False)
    assert report["status"] == "passed"
    assert all(report["checks"].values())


def test_revenue_is_not_multiplied_by_payments():
    settings = Settings.load()
    with duckdb.connect(str(settings.duckdb_path), read_only=True) as connection:
        item_total = connection.execute("select sum(price) from fact_order_items").fetchone()[0]
        mart_total = connection.execute("select sum(item_revenue) from mart_orders").fetchone()[0]
        line_total = connection.execute("select sum(item_revenue) from mart_sales_lines").fetchone()[0]
    assert abs(item_total - mart_total) < 0.01
    assert abs(item_total - line_total) < 0.01


def test_fact_keys_and_relationships_are_valid():
    settings = Settings.load()
    with duckdb.connect(str(settings.duckdb_path), read_only=True) as connection:
        duplicate_orders = connection.execute(
            "select count(*) - count(distinct order_id) from fact_orders"
        ).fetchone()[0]
        orphan_items = connection.execute(
            "select count(*) from fact_order_items i anti join fact_orders o using(order_id)"
        ).fetchone()[0]
        orphan_payments = connection.execute(
            "select count(*) from fact_payments p anti join fact_orders o using(order_id)"
        ).fetchone()[0]
    assert duplicate_orders == 0
    assert orphan_items == 0
    assert orphan_payments == 0
