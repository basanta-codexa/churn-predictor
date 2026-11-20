# Contributing

Contributions are welcome. Please keep changes small, focused, and verifiable.

## Development setup

```bash
python -m venv venv
venv\Scripts\activate        # macOS/Linux: source venv/bin/activate
pip install -r requirements-dev.txt
```

The runtime app only needs `requirements.txt`. `requirements-dev.txt` adds Playwright for screenshot capture.

## Workflow

1. Fork the repository and create a branch from `main`.
2. Make one logical change per branch or commit.
3. Run the checks below before opening a pull request.
4. Describe what changed and why. If the UI changed, include updated screenshots.

## Checks

```bash
python -m compileall -q app.py pages src tests scripts
pytest tests
streamlit run app.py
```

For screenshot updates, start the app and run:

```bash
python scripts/capture_screenshots.py http://127.0.0.1:8502
```

## Ground rules

- Do not retrain the model for documentation or styling changes.
- Do not change the model's feature order or preprocessing without a justified reason and updated tests.
- Do not invent metrics, customer records, or business statistics.
- Preserve the calibrated prediction pipeline.
- Keep the existing tests passing.
- Avoid adding dependencies that are not required by the runtime or the screenshot tooling.

## Pull requests

A good pull request includes:

- a clear title and short description;
- the files changed and why;
- test results;
- screenshots for any visible UI change;
- notes about any remaining limitations.
