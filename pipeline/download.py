from __future__ import annotations

import shutil
import zipfile

import requests

from .config import Settings


DATASET_URL = "https://www.kaggle.com/api/v1/datasets/download/olistbr/brazilian-ecommerce"
EXPECTED_FILE = "olist_orders_dataset.csv"


def download_dataset(settings: Settings, force: bool = False) -> None:
    expected = settings.raw_dir / EXPECTED_FILE
    if expected.exists() and not force:
        print(f"Dataset already available: {expected}")
        return

    archive = settings.raw_dir / "olist.zip"
    partial = settings.raw_dir / "olist.zip.part"
    with requests.get(DATASET_URL, stream=True, timeout=120) as response:
        response.raise_for_status()
        with partial.open("wb") as handle:
            shutil.copyfileobj(response.raw, handle)
    partial.replace(archive)

    with zipfile.ZipFile(archive) as bundle:
        bundle.extractall(settings.raw_dir)
    if not expected.exists():
        raise RuntimeError(f"Dataset archive did not contain {EXPECTED_FILE}")
    print(f"Downloaded and extracted Olist dataset to {settings.raw_dir}")

