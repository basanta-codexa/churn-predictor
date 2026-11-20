"""Model analytics placeholder (Phase 5)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from page_shell import placeholder  # noqa: E402

placeholder(
    page_title="Model Analytics",
    eyebrow="Model Analytics",
    title="Model analytics",
    subtitle="Performance and explainability at scale.",
    phase="Phase 5",
    description="Extended evaluation and monitoring are planned.",
    items=[
        "ROC and precision-recall curves",
        "Confusion matrix and threshold analysis",
        "Feature importance and calibration analysis",
        "Model monitoring and drift detection",
    ],
    footer_items=[("Application", "Retention Intelligence")],
)
