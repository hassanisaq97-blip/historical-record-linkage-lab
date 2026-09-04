"""Static result figures (no dashboard/frontend by design)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def plot_method_comparison(comparison: pd.DataFrame, out_path: Path) -> None:
    metrics = ["precision", "recall", "f1"]
    fig, ax = plt.subplots(figsize=(6, 4))
    comparison[metrics].plot(kind="bar", ax=ax, ylim=(0, 1))
    ax.set_ylabel("score")
    ax.set_title("Linkage-metoder: precision / recall / F1 (test-split)")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_feature_importance(importances: pd.Series, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    importances.sort_values().plot(kind="barh", ax=ax)
    ax.set_xlabel("feature importance (Random Forest)")
    ax.set_title("Vigtigste features i ML-linkage-modellen")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
