"""Customer intelligence placeholder (Phase 5)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from page_shell import placeholder  # noqa: E402

placeholder(
    page_title="Customer Intelligence",
    eyebrow="Customer Intelligence",
    title="Customer intelligence",
    subtitle="Explore customers, segments, and batch predictions.",
    phase="Phase 5",
    description="Customer directory, search, filtering, and batch prediction are planned.",
    items=[
        "Customer directory with search and filters",
        "Risk category and contract-type filtering",
        "Probability sorting and customer ranking",
        "Batch CSV prediction with downloadable results",
    ],
    footer_items=[("Application", "Retention Intelligence")],
)
