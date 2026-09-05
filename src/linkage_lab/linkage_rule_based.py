"""Deterministic rule-based linkage: a fixed set of similarity thresholds,
no training data required. This is the baseline the ML model is compared
against.
"""

from __future__ import annotations

import pandas as pd

GIVEN_NAME_JW_THRESHOLD = 0.85
SURNAME_JW_THRESHOLD = 0.90
MAX_BIRTH_YEAR_DIFF = 2


def predict(features: pd.DataFrame) -> pd.Series:
    place_ok = (features["birth_place_match"] == 1) | (features["birth_place_both_observed"] == 0)
    is_match = (
        (features["given_name_jw"] >= GIVEN_NAME_JW_THRESHOLD)
        & (features["surname_jw"] >= SURNAME_JW_THRESHOLD)
        & (features["birth_year_diff"] <= MAX_BIRTH_YEAR_DIFF)
        & place_ok
    )
    return is_match.astype(int)
