"""Retention insights placeholder (Phase 4)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from page_shell import placeholder  # noqa: E402

placeholder(
    page_title="Retention Insights",
    eyebrow="Retention Insights",
    title="Retention insights",
    subtitle="Risk drivers and retention strategies.",
    phase="Phase 4",
    description="Aggregated drivers and recommended actions are planned.",
    items=[
        "Aggregated SHAP drivers by segment",
        "Customer-level retention recommendations",
        "Causal validation of proposed actions",
    ],
    footer_items=[("Application", "Retention Intelligence")],
)
