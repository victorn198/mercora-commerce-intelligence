from __future__ import annotations

from datetime import date

import duckdb

from app.repository import AnalyticsRepository, FilterState
from pipeline.config import Settings


def _repository() -> AnalyticsRepository:
    return AnalyticsRepository(Settings.load().duckdb_path)


def test_window_boundaries_are_contiguous():
    state = FilterState(as_of=date(2018, 8, 31), window_days=30)
    assert state.start_date == date(2018, 8, 2)
    assert state.previous_end == date(2018, 8, 1)
    assert state.previous_start == date(2018, 7, 3)


def test_kpi_formulas_reconcile():
    state = FilterState(as_of=date(2018, 8, 31), window_days=30)
    kpis = _repository().kpis(state)
    assert kpis["orders"] > 0
    assert kpis["active_customers"] <= kpis["orders"]
    assert abs(kpis["average_ticket"] - kpis["revenue"] / kpis["orders"]) < 0.01
    assert 0 <= kpis["repeat_share"] <= 1
    assert 0 <= kpis["on_time_rate"] <= 1


def test_cohort_and_second_purchase_rules():
    settings = Settings.load()
    with duckdb.connect(str(settings.duckdb_path), read_only=True) as connection:
        invalid_month_zero = connection.execute(
            "select count(*) from mart_cohorts where month_number = 0 and abs(retention_rate - 1) > 0.000001"
        ).fetchone()[0]
        negative_second_purchase = connection.execute(
            "select count(*) from mart_customers where days_to_second_purchase < 0"
        ).fetchone()[0]
    assert invalid_month_zero == 0
    assert negative_second_purchase == 0


def test_action_queue_prioritizes_auditable_risk_score():
    state = FilterState(as_of=date(2018, 8, 31), window_days=30)
    queue = _repository().action_queue(state)
    assert not queue.empty
    assert queue["priority"].is_monotonic_decreasing
    assert set(queue["signal"]).issubset({"Atraso", "Avaliação", "Monitorar"})


def test_category_drill_returns_products_inside_selected_category():
    state = FilterState(as_of=date(2018, 8, 31), window_days=30)
    repository = _repository()
    categories = repository.breakdown(state, "category", 1)
    assert not categories.empty
    category = categories.iloc[0]["dimension"]
    products = repository.product_breakdown(state, category, 10)
    assert not products.empty
    assert len(products) <= 10
    assert products["dimension"].str.startswith("Produto ").all()
    assert products["revenue"].gt(0).all()
