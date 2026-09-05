"""Error inspection for the NYC-directories linkage benchmark.
Precision/recall/F1/confusion-matrix computation itself is schema-agnostic
and reused directly from `linkage_lab.evaluation.compute_metrics`.
"""

from __future__ import annotations

import pandas as pd


def attach_raw_fields(df: pd.DataFrame, entries: pd.DataFrame) -> pd.DataFrame:
    cols = ["record_id", "raw_line", "surname", "given_name", "occupation", "address_business", "address_home"]
    indexed = entries[cols].set_index("record_id")
    a_cols = indexed.add_prefix("a_")
    b_cols = indexed.add_prefix("b_")
    return df.join(a_cols, on="record_id_a").join(b_cols, on="record_id_b")


def get_error_examples(
    labeled_df: pd.DataFrame,
    y_pred: pd.Series,
    entries: pd.DataFrame,
    n: int = 10,
) -> dict[str, pd.DataFrame]:
    df = labeled_df.copy()
    df["predicted_match"] = y_pred.values

    false_positives = df[(df["predicted_match"] == 1) & (df["is_match"] == 0)]
    false_negatives = df[(df["predicted_match"] == 0) & (df["is_match"] == 1)]

    display_cols = [
        "record_id_a", "record_id_b",
        "a_given_name", "a_occupation", "a_address_business", "a_address_home",
        "b_given_name", "b_occupation", "b_address_business", "b_address_home",
    ]
    fp_display = attach_raw_fields(false_positives, entries)[display_cols].head(n)
    fn_display = attach_raw_fields(false_negatives, entries)[display_cols].head(n)
    return {"false_positives": fp_display, "false_negatives": fn_display}
