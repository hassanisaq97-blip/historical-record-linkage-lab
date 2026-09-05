"""Deterministic rule-based linkage for city-directory candidate pairs."""

from __future__ import annotations

import pandas as pd

GIVEN_NAME_JW_THRESHOLD = 0.90
OCCUPATION_OR_ADDRESS_JW_THRESHOLD = 0.90


def predict(features: pd.DataFrame) -> pd.Series:
    occupation_evidence = (features["occupation_jw"] >= OCCUPATION_OR_ADDRESS_JW_THRESHOLD) & (
        features["occupation_both_observed"] == 1
    )
    address_evidence = features["best_address_jw"] >= OCCUPATION_OR_ADDRESS_JW_THRESHOLD

    is_match = (features["given_name_jw"] >= GIVEN_NAME_JW_THRESHOLD) & (occupation_evidence | address_evidence)
    return is_match.astype(int)
