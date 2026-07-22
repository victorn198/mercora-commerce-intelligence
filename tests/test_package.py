from __future__ import annotations

from pipeline.config import Settings
from pipeline.package import build_deploy_package


def test_deploy_package_contains_current_app_without_cache():
    deploy_dir = build_deploy_package(Settings.load())
    assert (deploy_dir / "app" / "i18n.py").exists()
    assert (deploy_dir / "data" / "processed" / "commerce_app.duckdb").exists()
    assert (deploy_dir / "plotly-cloud.toml").exists()
    assert not list(deploy_dir.rglob("__pycache__"))
    assert not list(deploy_dir.rglob("*.pyc"))
