"""Capture a screenshot of the running Streamlit app for the README."""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8501"
OUT = ROOT / "images" / "app_screenshot.png"
WIDTH = int(sys.argv[2]) if len(sys.argv) > 2 else 1600
HEIGHT = int(sys.argv[3]) if len(sys.argv) > 3 else 1000


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT},
                                device_scale_factor=1)
        page.goto(URL, wait_until="networkidle", timeout=180_000)

        # wait for the app to finish its first run: the sidebar widgets and
        # the chart both have to be on screen before the shot looks right
        page.wait_for_selector('[data-testid="stSidebar"] [data-testid="stSelectbox"]',
                               timeout=120_000)
        page.wait_for_selector(".js-plotly-plot", timeout=120_000)
        page.wait_for_function(
            "() => { const c = document.querySelector('.js-plotly-plot');"
            " return c && c.getBoundingClientRect().height > 200; }",
            timeout=120_000)
        page.wait_for_timeout(3000)

        OUT.parent.mkdir(exist_ok=True)
        page.screenshot(path=str(OUT))
        browser.close()
    print(f"saved {OUT}")


if __name__ == "__main__":
    main()
