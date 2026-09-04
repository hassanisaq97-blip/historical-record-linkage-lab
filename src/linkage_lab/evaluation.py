"""Precision/recall/F1 evaluation and human-readable error inspection."""

from __future__ import annotations

import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score


def compute_metrics(y_true: pd.Series, y_pred: pd.Series) -> dict:
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_negatives": int(tn),
    }


def build_comparison_table(method_metrics: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for method_name, metrics in method_metrics.items():
        row = {"method": method_name}
        row.update(metrics)
        rows.append(row)
    return pd.DataFrame(rows).set_index("method")


def attach_raw_fields(
    df: pd.DataFrame,
    census_raw: pd.DataFrame,
    parish_raw: pd.DataFrame,
) -> pd.DataFrame:
    census_cols = census_raw.set_index("census_record_id")[["given_name", "surname", "age", "birth_place"]]
    census_cols.columns = [f"census_{c}" for c in census_cols.columns]
    parish_cols = parish_raw.set_index("parish_record_id")[["given_name", "surname", "birth_year", "birth_place"]]
    parish_cols.columns = [f"parish_{c}" for c in parish_cols.columns]

    out = df.join(census_cols, on="census_record_id").join(parish_cols, on="parish_record_id")
    return out


def get_error_examples(
    labeled_df: pd.DataFrame,
    y_pred: pd.Series,
    census_raw: pd.DataFrame,
    parish_raw: pd.DataFrame,
    n: int = 8,
) -> dict[str, pd.DataFrame]:
    df = labeled_df.copy()
    df["predicted_match"] = y_pred.values

    false_positives = df[(df["predicted_match"] == 1) & (df["is_true_match"] == 0)]
    false_negatives = df[(df["predicted_match"] == 0) & (df["is_true_match"] == 1)]

    display_cols = [
        "census_record_id", "parish_record_id",
        "census_given_name", "census_surname", "census_age", "census_birth_place",
        "parish_given_name", "parish_surname", "parish_birth_year", "parish_birth_place",
    ]

    fp_display = attach_raw_fields(false_positives, census_raw, parish_raw)[display_cols].head(n)
    fn_display = attach_raw_fields(false_negatives, census_raw, parish_raw)[display_cols].head(n)
    return {"false_positives": fp_display, "false_negatives": fn_display}
