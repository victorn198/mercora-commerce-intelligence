from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable

import duckdb
import pandas as pd


@dataclass(frozen=True)
class FilterState:
    as_of: date
    window_days: int = 30
    categories: tuple[str, ...] = ()
    customer_states: tuple[str, ...] = ()
    seller_states: tuple[str, ...] = ()
    payment_types: tuple[str, ...] = ()
    statuses: tuple[str, ...] = ()

    @property
    def start_date(self) -> date:
        return self.as_of - timedelta(days=self.window_days - 1)

    @property
    def previous_end(self) -> date:
        return self.start_date - timedelta(days=1)

    @property
    def previous_start(self) -> date:
        return self.previous_end - timedelta(days=self.window_days - 1)


class AnalyticsRepository:
    def __init__(self, database_path: Path):
        self.database_path = database_path

    def _connect(self):
        return duckdb.connect(str(self.database_path), read_only=True)

    @staticmethod
    def _in_filter(column: str, values: Iterable[str], params: list) -> str:
        values = tuple(values)
        if not values:
            return ""
        params.extend(values)
        return f" and {column} in ({', '.join('?' for _ in values)})"

    def _cte(self, state: FilterState, start: date, end: date) -> tuple[str, list]:
        params: list = [start, end]
        conditions = "l.purchase_date between ? and ?"
        conditions += self._in_filter("l.category_pt", state.categories, params)
        conditions += self._in_filter("l.customer_state", state.customer_states, params)
        conditions += self._in_filter("l.seller_state", state.seller_states, params)
        conditions += self._in_filter("l.order_status", state.statuses, params)
        if state.payment_types:
            params.extend(state.payment_types)
            placeholders = ", ".join("?" for _ in state.payment_types)
            conditions += (
                " and exists (select 1 from fact_payments fp "
                "where fp.order_id = l.order_id "
                f"and fp.payment_type in ({placeholders}))"
            )
        sql = f"""
        with selected_lines as (
            select l.*
            from mart_sales_lines l
            where {conditions}
        ),
        selected_orders as (
            select
                l.order_id,
                any_value(l.customer_key) as customer_key,
                any_value(l.customer_state) as customer_state,
                any_value(l.customer_city) as customer_city,
                any_value(l.order_status) as order_status,
                any_value(l.purchase_date) as purchase_date,
                any_value(l.is_delivered) as is_delivered,
                any_value(l.is_cancelled) as is_cancelled,
                any_value(l.is_on_time) as is_on_time,
                any_value(l.delivery_days) as delivery_days,
                any_value(l.review_score) as review_score,
                sum(l.item_revenue) as revenue,
                sum(l.freight_value) as freight
            from selected_lines l
            group by l.order_id
        )
        """
        return sql, params

    def metadata(self) -> dict:
        with self._connect() as connection:
            row = connection.execute("select * from build_metadata").fetchdf().iloc[0]
            return row.to_dict()

    def filter_options(self) -> dict[str, list[str]]:
        with self._connect() as connection:
            return {
                "categories": connection.execute(
                    "select distinct category_pt from fact_order_items where category_pt is not null order by 1"
                ).fetchnumpy()["category_pt"].tolist(),
                "customer_states": connection.execute(
                    "select distinct customer_state from fact_orders where customer_state is not null order by 1"
                ).fetchnumpy()["customer_state"].tolist(),
                "seller_states": connection.execute(
                    "select distinct seller_state from fact_order_items where seller_state is not null order by 1"
                ).fetchnumpy()["seller_state"].tolist(),
                "payment_types": connection.execute(
                    "select distinct payment_type from fact_payments where payment_type is not null order by 1"
                ).fetchnumpy()["payment_type"].tolist(),
                "statuses": connection.execute(
                    "select distinct order_status from fact_orders where order_status is not null order by 1"
                ).fetchnumpy()["order_status"].tolist(),
            }

    def category_translations(self) -> dict[str, str]:
        with self._connect() as connection:
            rows = connection.execute(
                "select distinct category_pt, category_en from dim_products where category_pt is not null and category_en is not null"
            ).fetchall()
        return {category_pt: category_en.replace("_", " ").title() for category_pt, category_en in rows}

    def kpis(self, state: FilterState, start: date | None = None, end: date | None = None) -> dict:
        start = start or state.start_date
        end = end or state.as_of
        cte, params = self._cte(state, start, end)
        params.append(start)
        query = cte + """
        select
            coalesce(sum(o.revenue), 0) as revenue,
            count(*) as orders,
            count(distinct o.customer_key) as active_customers,
            coalesce(sum(o.revenue) / nullif(count(*), 0), 0) as average_ticket,
            coalesce(
                count(distinct case when c.first_purchase_date < ? then o.customer_key end)::double
                / nullif(count(distinct o.customer_key), 0), 0
            ) as repeat_share,
            coalesce(avg(case when o.is_on_time then 1.0 when o.is_on_time is false then 0.0 end), 0) as on_time_rate,
            coalesce(avg(case when o.is_cancelled then 1.0 else 0.0 end), 0) as cancellation_rate,
            coalesce(avg(o.review_score), 0) as review_score
        from selected_orders o
        left join mart_customers c using(customer_key)
        """
        with self._connect() as connection:
            return connection.execute(query, params).fetchdf().iloc[0].to_dict()

    def current_and_previous_kpis(self, state: FilterState) -> tuple[dict, dict]:
        return (
            self.kpis(state),
            self.kpis(state, state.previous_start, state.previous_end),
        )

    def trend(self, state: FilterState) -> pd.DataFrame:
        cte, params = self._cte(state, state.start_date, state.as_of)
        query = cte + """
        select
            purchase_date,
            sum(revenue) as revenue,
            count(*) as orders,
            count(distinct customer_key) as customers
        from selected_orders
        group by purchase_date
        order by purchase_date
        """
        with self._connect() as connection:
            return connection.execute(query, params).fetchdf()

    def breakdown(self, state: FilterState, dimension: str, limit: int = 12) -> pd.DataFrame:
        allowed = {
            "category": "l.category_pt",
            "customer_state": "l.customer_state",
            "seller_state": "l.seller_state",
        }
        column = allowed[dimension]
        cte, params = self._cte(state, state.start_date, state.as_of)
        params.append(limit)
        query = cte + f"""
        select
            {column} as dimension,
            sum(l.item_revenue) as revenue,
            count(distinct l.order_id) as orders,
            count(distinct l.customer_key) as customers,
            avg(case when l.is_on_time then 1.0 when l.is_on_time is false then 0.0 end) as on_time_rate,
            avg(l.review_score) as review_score
        from selected_lines l
        group by {column}
        order by revenue desc
        limit ?
        """
        with self._connect() as connection:
            return connection.execute(query, params).fetchdf()

    def payment_mix(self, state: FilterState) -> pd.DataFrame:
        cte, params = self._cte(state, state.start_date, state.as_of)
        query = cte + """
        , order_scope as (select order_id from selected_orders)
        select p.payment_type as dimension, sum(p.payment_value) as value
        from fact_payments p
        join order_scope s using(order_id)
        group by p.payment_type
        order by value desc
        """
        with self._connect() as connection:
            return connection.execute(query, params).fetchdf()

    def product_breakdown(self, state: FilterState, category: str, limit: int = 12) -> pd.DataFrame:
        cte, params = self._cte(state, state.start_date, state.as_of)
        params.extend([category, limit])
        query = cte + """
        select
            'Produto ' || substr(l.product_id, 1, 8) as dimension,
            sum(l.item_revenue) as revenue,
            count(distinct l.order_id) as orders,
            count(distinct l.customer_key) as customers,
            avg(case when l.is_on_time then 1.0 when l.is_on_time is false then 0.0 end) as on_time_rate,
            avg(l.review_score) as review_score
        from selected_lines l
        where l.category_pt = ?
        group by l.product_id
        order by revenue desc
        limit ?
        """
        with self._connect() as connection:
            return connection.execute(query, params).fetchdf()

    def action_queue(self, state: FilterState) -> pd.DataFrame:
        category = self.breakdown(state, "category", limit=20)
        if category.empty:
            return category
        category = category.copy()
        category["priority"] = (
            category["revenue"].rank(pct=True, ascending=True) * 0.35
            + category["on_time_rate"].fillna(1).rank(pct=True, ascending=False) * 0.40
            + category["review_score"].fillna(5).rank(pct=True, ascending=False) * 0.25
        )
        category["signal"] = category.apply(
            lambda row: "Atraso" if row["on_time_rate"] < 0.85 else "Avaliação" if row["review_score"] < 4 else "Monitorar",
            axis=1,
        )
        return category.sort_values("priority", ascending=False).head(8)

    def cohort_matrix(self, as_of: date, cohorts: int = 12, months: int = 6) -> pd.DataFrame:
        with self._connect() as connection:
            return connection.execute(
                """
                select cohort_month, month_number, retention_rate
                from mart_cohorts
                where cohort_month <= date_trunc('month', ?::date)
                  and month_number between 0 and ?
                qualify dense_rank() over(order by cohort_month desc) <= ?
                order by cohort_month, month_number
                """,
                [as_of, months, cohorts],
            ).fetchdf()

    def rfm_segments(self, state: FilterState) -> pd.DataFrame:
        with self._connect() as connection:
            return connection.execute(
                """
                select rfm_segment as dimension, count(*) as customers, sum(lifetime_revenue) as revenue
                from mart_customers
                where last_purchase_date <= ?
                group by rfm_segment
                order by customers desc
                """,
                [state.as_of],
            ).fetchdf()

    def customer_table(self, state: FilterState, search: str = "", limit: int = 100) -> pd.DataFrame:
        search = search.strip().lower()
        with self._connect() as connection:
            return connection.execute(
                """
                select
                    customer_key,
                    customer_state,
                    customer_city,
                    rfm_segment,
                    lifetime_orders,
                    round(lifetime_revenue, 2) as lifetime_revenue,
                    recency_days,
                    days_to_second_purchase,
                    round(average_review, 2) as average_review
                from mart_customers
                where last_purchase_date <= ?
                  and (? = '' or lower(customer_key) like '%' || ? || '%')
                order by lifetime_revenue desc
                limit ?
                """,
                [state.as_of, search, search, limit],
            ).fetchdf()

    def customer_orders(self, customer_key: str) -> pd.DataFrame:
        if not customer_key:
            return pd.DataFrame()
        with self._connect() as connection:
            return connection.execute(
                """
                select purchase_date, order_id, item_revenue, freight_value, review_score, is_on_time
                from mart_customer_orders
                where customer_key = ?
                order by purchase_date desc
                """,
                [customer_key],
            ).fetchdf()

    def table_counts(self) -> pd.DataFrame:
        tables = [
            "fact_orders",
            "fact_order_items",
            "fact_payments",
            "fact_reviews",
            "mart_orders",
            "mart_sales_lines",
            "mart_customers",
            "mart_cohorts",
        ]
        with self._connect() as connection:
            return pd.DataFrame(
                [{"table": table, "rows": connection.execute(f"select count(*) from {table}").fetchone()[0]} for table in tables]
            )
