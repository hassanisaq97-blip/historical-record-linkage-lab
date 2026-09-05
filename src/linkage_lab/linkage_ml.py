"""Supervised ML linkage: a random-forest classifier trained on pairwise
similarity features from the entity-level training split.
"""

from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from . import config

FEATURE_COLUMNS = [
    "given_name_jw",
    "surname_jw",
    "given_name_exact",
    "surname_exact",
    "birth_year_diff",
    "birth_place_match",
    "birth_place_both_observed",
]


def train_model(train_df: pd.DataFrame, seed: int = config.RANDOM_SEED) -> RandomForestClassifier:
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        class_weight="balanced",
        random_state=seed,
    )
    model.fit(train_df[FEATURE_COLUMNS], train_df["is_true_match"])
    return model


def predict(model: RandomForestClassifier, df: pd.DataFrame) -> pd.Series:
    return pd.Series(model.predict(df[FEATURE_COLUMNS]), index=df.index)


def predict_proba(model: RandomForestClassifier, df: pd.DataFrame) -> pd.Series:
    return pd.Series(model.predict_proba(df[FEATURE_COLUMNS])[:, 1], index=df.index)


def feature_importances(model: RandomForestClassifier) -> pd.Series:
    return pd.Series(model.feature_importances_, index=FEATURE_COLUMNS).sort_values(ascending=False)
