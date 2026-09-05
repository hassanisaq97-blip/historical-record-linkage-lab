"""ML linkage for city-directory candidate pairs.

Same Random Forest choice as the synthetic pipeline, kept for consistency
and because nothing in this much smaller, more imbalanced benchmark gave
a reason to prefer a different model class.
"""

from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from .. import config

FEATURE_COLUMNS = [
    "given_name_jw",
    "given_name_exact",
    "occupation_jw",
    "occupation_exact",
    "occupation_both_observed",
    "address_business_jw",
    "address_business_both_observed",
    "address_home_jw",
    "address_home_both_observed",
    "best_address_jw",
]


def train_model(train_df: pd.DataFrame, seed: int = config.RANDOM_SEED) -> RandomForestClassifier:
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=5,
        class_weight="balanced",
        random_state=seed,
    )
    model.fit(train_df[FEATURE_COLUMNS], train_df["is_match"])
    return model


def predict(model: RandomForestClassifier, df: pd.DataFrame) -> pd.Series:
    return pd.Series(model.predict(df[FEATURE_COLUMNS]), index=df.index)


def predict_proba(model: RandomForestClassifier, df: pd.DataFrame) -> pd.Series:
    return pd.Series(model.predict_proba(df[FEATURE_COLUMNS])[:, 1], index=df.index)
