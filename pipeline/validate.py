from __future__ import annotations

import json
from datetime import datetime, timezone

import duckdb

from .config import Settings


CHECKS = {
    "orders_unique": "select count(*) = count(distinct order_id) from fact_orders",
    "items_unique": "select count(*) = count(distinct order_id || ':' || order_item_id) from fact_order_items",
    "payments_unique": "select count(*) = count(distinct order_id || ':' || payment_sequential) from fact_payments",
    "items_have_orders": "select count(*) = 0 from fact_order_items i anti join fact_orders o using(order_id)",
    "payments_have_orders": "select count(*) = 0 from fact_payments p anti join fact_orders o using(order_id)",
    "order_mart_unique": "select count(*) = count(distinct order_id) from mart_orders",
    "item_revenue_reconciles": "select abs((select sum(price) from fact_order_items) - (select sum(item_revenue) from mart_orders)) < 0.01",
    "nonnegative_revenue": "select count(*) = 0 from mart_orders where item_revenue < 0 or payment_value < 0",
    "valid_analysis_dates": "select max(purchase_date) >= date '2018-08-31' and min(purchase_date) >= date '2016-01-01' from fact_orders",
    "customer_hash_present": "select count(*) = 0 from fact_orders where customer_key is null",
    "customer_hash_unique": "select count(*) = count(distinct customer_key) from dim_customers",
    "historical_dates_bounded": "select min(purchase_date) >= date '2016-01-01' and max(purchase_date) <= date '2018-12-31' from fact_orders",
    "critical_fields_present": "select count(*) = 0 from fact_order_items where order_id is null or product_id is null or seller_id is null",
    "no_sensitive_columns": "select count(*) = 0 from information_schema.columns where lower(column_name) similar to '%(email|phone|telefone|cpf|customer_id|customer_unique_id)%'",
}


def run_validation(settings: Settings, fail_on_error: bool = True) -> dict:
    if not settings.duckdb_path.exists():
        raise FileNotFoundError(f"Build the database first: {settings.duckdb_path}")

    with duckdb.connect(str(settings.duckdb_path), read_only=True) as connection:
        checks = {
            name: bool(connection.execute(query).fetchone()[0])
            for name, query in CHECKS.items()
        }
        metrics = connection.execute(
            """
            select
                count(*) as orders,
                count(distinct customer_key) as customers,
                round(sum(item_revenue), 2) as item_revenue,
                round(sum(payment_value), 2) as payments,
                round(sum(freight_value), 2) as freight
            from mart_orders
            """
        ).fetchdf().to_dict("records")[0]

    report = {
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "metrics": metrics,
    }
    (settings.processed_dir / "quality_report.json").write_text(
        json.dumps(report, indent=2, default=str), encoding="utf-8"
    )
    print(json.dumps(report, indent=2, default=str))
    if fail_on_error and report["status"] != "passed":
        raise RuntimeError("One or more data quality checks failed")
    return report
