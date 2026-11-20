"""Global SHAP summaries built from the committed model and data."""
from __future__ import annotations

import numpy as np
import pandas as pd

from predictor import explain


def global_driver_summary(frame, meta, pipe, explainer, sample_size=300,
                          seed=42):
    """Average SHAP attribution per raw feature over a deterministic sample.

    The returned frame has ``positive`` and ``negative`` columns in log-odds,
    so a diverging bar chart can show which features push risk up or down.
    """
    sample = frame.sample(n=min(sample_size, len(frame)), random_state=seed)
    phi_rows = []
    for _, record in sample.iterrows():
        X_new = pd.DataFrame([record[meta["feature_order"]]])[
            meta["feature_order"]]
        phi_rows.append(explain(explainer, pipe, meta, X_new)["feature_phi"])

    mean_phi = np.vstack(phi_rows).mean(axis=0)
    summary = pd.DataFrame({
        "feature": list(meta["feature_order"]),
        "mean_phi": mean_phi,
    })
    summary["positive"] = summary["mean_phi"].clip(lower=0)
    summary["negative"] = summary["mean_phi"].clip(upper=0)
    summary["absolute"] = summary["mean_phi"].abs()
    return summary.sort_values("absolute", ascending=False).reset_index(drop=True)
