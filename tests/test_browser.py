from __future__ import annotations

import os
import pytest
import tempfile

from application import create_dashboard
from pipeline.config import Settings


@pytest.mark.browser
@pytest.mark.skipif(
    os.getenv("RUN_BROWSER_E2E") != "1",
    reason="Set RUN_BROWSER_E2E=1 on a host that permits headless Chrome sessions.",
)
def test_navigation_and_global_window_filter():
    from dash.testing.application_runners import ThreadedRunner
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as expected
    from selenium.webdriver.support.ui import WebDriverWait

    dashboard = create_dashboard()
    runner = ThreadedRunner()
    runner.start(dashboard)

    root = Settings.load().root
    service = Service(str(root / ".runtime" / "tools" / "chromedriver-win64" / "chromedriver.exe"))
    options = Options()
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    options.add_argument("--headless=new")
    options.add_argument("--remote-debugging-pipe")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--no-sandbox")
    options.add_argument("--no-first-run")
    options.add_argument(f"--user-data-dir={tempfile.mkdtemp(prefix='chrome-e2e-')}")
    options.add_argument("--window-size=1440,1200")
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)
    try:
        driver.get(runner.url)
        wait.until(expected.text_to_be_present_in_element((By.CSS_SELECTOR, "#page-content h2"), "Command Center"))
        for navigation_id, heading in (
            ("nav-revenue", "Revenue Explorer"),
            ("nav-retention", "Retenção"),
            ("nav-customers", "Customer Explorer"),
            ("nav-trust", "Data Trust"),
        ):
            driver.find_element(By.ID, navigation_id).click()
            wait.until(expected.text_to_be_present_in_element((By.CSS_SELECTOR, "#page-content h2"), heading))
        assert not [entry for entry in driver.get_log("browser") if entry["level"] == "SEVERE"]
    finally:
        driver.quit()
        runner.stop()
