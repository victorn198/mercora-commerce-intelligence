from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    root: Path
    data_dir: Path
    raw_dir: Path
    processed_dir: Path
    build_duckdb_path: Path
    duckdb_path: Path

    @classmethod
    def load(cls) -> "Settings":
        data_dir = Path(os.getenv("DATA_DIR", ROOT / "data")).resolve()
        duckdb_path = Path(
            os.getenv("DUCKDB_PATH", data_dir / "processed" / "commerce_app.duckdb")
        ).resolve()
        settings = cls(
            root=ROOT,
            data_dir=data_dir,
            raw_dir=data_dir / "raw",
            processed_dir=data_dir / "processed",
            build_duckdb_path=data_dir / "processed" / "commerce.duckdb",
            duckdb_path=duckdb_path,
        )
        for path in (settings.raw_dir, settings.processed_dir):
            path.mkdir(parents=True, exist_ok=True)
        return settings
