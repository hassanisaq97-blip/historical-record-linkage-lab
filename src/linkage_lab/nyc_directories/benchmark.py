"""Loads the manual benchmark (see data/raw/nyc_directories/MANUAL_BENCHMARK.md)
and attaches it to the candidate-pair feature table for evaluation.

Train/test split here is pair-level (not entity-level like the synthetic
benchmark) given the benchmark's small size (92 pairs) and the fact that,
unlike the synthetic ground truth, we do not have a clean underlying
entity id to split on for real records - only the pair judgement itself.
This is a documented difference from the synthetic pipeline's stricter
entity-level split, not an oversight; see docs/limitations.md.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .. import config


def load_manual_labels() -> pd.DataFrame:
    return pd.read_csv(config.NYC_DIR_RAW_DIR / "manual_benchmark_labels.csv")


def build_labeled_features(
    candidate_features: pd.DataFrame,
    manual_labels: pd.DataFrame,
    seed: int = config.RANDOM_SEED,
    train_fraction: float = 0.6,
) -> pd.DataFrame:
    labeled = manual_labels.merge(
        candidate_features, on=["record_id_a", "record_id_b"], how="inner"
    )
    if len(labeled) != len(manual_labels):
        missing = len(manual_labels) - len(labeled)
        raise ValueError(
            f"{missing} manually labelled pair(s) not found in candidate_features - "
            "benchmark and candidate pairs are out of sync."
        )

    # Stratified by is_match: with only 14 positives in 92 pairs, a plain
    # shuffle risks a train or test fold with almost no positives at all.
    rng = np.random.default_rng(seed)
    split = np.array(["test"] * len(labeled), dtype=object)
    for _, group in labeled.groupby("is_match"):
        idx = group.index.to_numpy().copy()
        rng.shuffle(idx)
        n_train = max(1, int(round(len(idx) * train_fraction)))
        split[idx[:n_train]] = "train"

    labeled = labeled.copy()
    labeled["split"] = split
    return labeled
