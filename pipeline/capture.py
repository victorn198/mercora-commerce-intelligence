from __future__ import annotations

import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from .config import Settings


PAGES = ("command", "revenue", "retention", "customers", "trust")


def capture_screenshots(settings: Settings, base_url: str = "http://127.0.0.1:8050/") -> Path:
    output_dir = settings.root / "docs" / "images"
    browser = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
    if not browser.exists():
        raise FileNotFoundError(f"Microsoft Edge not found: {browser}")

    for lang in ("pt", "en"):
        language_dir = output_dir / lang
        language_dir.mkdir(parents=True, exist_ok=True)
        for page in PAGES:
            profile_dir = Path(tempfile.mkdtemp(prefix="mercora-capture-"))
            target = language_dir / f"{page}.png"
            target.unlink(missing_ok=True)
            url = f"{base_url.rstrip('/')}/?page={page}&lang={lang}"
            try:
                process = subprocess.Popen(
                    [
                        str(browser),
                        "--headless=new",
                        "--disable-gpu",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--no-first-run",
                        "--disable-background-networking",
                        "--disable-sync",
                        "--hide-scrollbars",
                        "--virtual-time-budget=7000",
                        "--window-size=1440,1350",
                        f"--user-data-dir={profile_dir}",
                        f"--screenshot={target}",
                        url,
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                deadline = time.monotonic() + 45
                while time.monotonic() < deadline:
                    if target.exists() and target.stat().st_size >= 20_000:
                        break
                    if process.poll() is not None:
                        break
                    time.sleep(0.25)
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                if not target.exists() or target.stat().st_size < 20_000:
                    raise RuntimeError(f"Screenshot was not rendered correctly: {target}")
            finally:
                shutil.rmtree(profile_dir, ignore_errors=True)

    print(f"Screenshots captured: {output_dir}")
    return output_dir
