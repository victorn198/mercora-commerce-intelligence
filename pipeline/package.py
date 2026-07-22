from __future__ import annotations

import shutil
from pathlib import Path

from .config import Settings


ROOT_FILES = (
    "app.py",
    "application.py",
    "factory.py",
    "Procfile",
    "requirements.txt",
    "wsgi.py",
)
SOURCE_DIRS = ("app", "assets")


def build_deploy_package(settings: Settings) -> Path:
    deploy_dir = settings.root / "deploy"
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir(parents=True)

    for filename in ROOT_FILES:
        shutil.copy2(settings.root / filename, deploy_dir / filename)

    for dirname in SOURCE_DIRS:
        shutil.copytree(
            settings.root / dirname,
            deploy_dir / dirname,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
        )

    pipeline_dir = deploy_dir / "pipeline"
    pipeline_dir.mkdir()
    for filename in ("__init__.py", "config.py"):
        shutil.copy2(settings.root / "pipeline" / filename, pipeline_dir / filename)

    processed_dir = deploy_dir / "data" / "processed"
    processed_dir.mkdir(parents=True)
    for filename in ("commerce_app.duckdb", "quality_report.json"):
        shutil.copy2(settings.processed_dir / filename, processed_dir / filename)

    shutil.copy2(settings.root / "app" / "plotly-cloud.toml", deploy_dir / "plotly-cloud.toml")
    print(f"Deployment package created: {deploy_dir}")
    return deploy_dir
