"""Capture real application screenshots for the README.

Usage:
    python scripts/capture_screenshots.py [base_url]

Requires Playwright and a local Chrome installation. The Streamlit app must
already be running at ``base_url``.
"""
from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "images"
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8502"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

PAGES = [
    ("overview", ""),
    ("prediction", "Predict_Churn"),
    ("model_analytics", "Model_Analytics"),
]


def _wait_for_charts(page):
    page.wait_for_selector('[data-testid="stPlotlyChart"]', timeout=120_000)
    page.wait_for_function(
        "() => { const c = document.querySelector('.js-plotly-plot');"
        " return c && c.getBoundingClientRect().height > 150; }",
        timeout=120_000,
    )
    page.wait_for_timeout(2500)


def main():
    OUT_DIR.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        launch_options = {"headless": True}
        if CHROME.exists():
            launch_options["executable_path"] = str(CHROME)
        browser = playwright.chromium.launch(**launch_options)
        page = browser.new_page(
            viewport={"width": 1600, "height": 1000},
            device_scale_factor=1,
        )

        for name, path in PAGES:
            url = f"{BASE_URL.rstrip('/')}/{path}" if path else BASE_URL
            page.goto(url, wait_until="networkidle", timeout=180_000)
            page.wait_for_selector('[data-testid="stSidebar"]', timeout=120_000)
            _wait_for_charts(page)
            output = OUT_DIR / f"{name}.png"
            page.screenshot(path=str(output), full_page=True)
            print(f"saved {output}")

            if name == "prediction":
                chart = page.locator('[data-testid="stPlotlyChart"]').first
                shap_output = OUT_DIR / "shap_explanation.png"
                chart.screenshot(path=str(shap_output))
                print(f"saved {shap_output}")

        browser.close()


if __name__ == "__main__":
    main()
