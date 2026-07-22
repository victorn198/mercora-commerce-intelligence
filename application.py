from __future__ import annotations

from dash import Dash

from app.callbacks import register_callbacks
from app.layout import build_shell
from app.repository import AnalyticsRepository
from pipeline.config import Settings


def create_dashboard() -> Dash:
    settings = Settings.load()
    if not settings.duckdb_path.exists():
        raise RuntimeError("Analytics database not found. Run: run.cmd -m pipeline build")

    repository = AnalyticsRepository(settings.duckdb_path)
    metadata = repository.metadata()
    options = repository.filter_options()

    dashboard = Dash(
        __name__,
        title="Mercora | Commerce Intelligence",
        suppress_callback_exceptions=True,
        update_title="Mercora | Loading...",
    )
    dashboard.layout = build_shell(
        options,
        metadata["source_start_date"],
        metadata["analysis_end_date"],
    )
    register_callbacks(
        dashboard,
        repository,
        settings.root,
        metadata["analysis_end_date"],
    )

    @dashboard.server.get("/health")
    def health():
        return {
            "status": "ok",
            "source_end_date": str(metadata["analysis_end_date"]),
        }

    return dashboard


app = create_dashboard()
server = app.server
