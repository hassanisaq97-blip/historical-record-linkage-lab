"""Candidate-pair generation (blocking).

Comparing every census record to every parish-register record would be
O(n * m). Instead we only compare records that share a Soundex code for
the (standardised) surname and have birth years within one bucket of each
other. Records with a completely missing surname cannot be blocked by this
method and are excluded - a documented limitation, not a silent drop.
"""

from __future__ import annotations

import jellyfish
import pandas as pd

from . import config


def _soundex(value: str | None) -> str | None:
    if not value:
        return None
    return jellyfish.soundex(value)


def add_blocking_keys_census(df: pd.DataFrame, bucket_width: int = config.BLOCKING_YEAR_BUCKET) -> pd.DataFrame:
    out = df.copy()
    out["surname_soundex"] = out["surname_std"].map(_soundex)
    implied_birth_year = out["census_year"] - out["age"]
    out["birth_year_bucket"] = (implied_birth_year // bucket_width).astype("Int64")
    return out


def add_blocking_keys_parish(df: pd.DataFrame, bucket_width: int = config.BLOCKING_YEAR_BUCKET) -> pd.DataFrame:
    out = df.copy()
    out["surname_soundex"] = out["surname_std"].map(_soundex)
    out["birth_year_bucket"] = (out["birth_year"] // bucket_width).astype("Int64")
    return out


def generate_candidate_pairs(census_blocked: pd.DataFrame, parish_blocked: pd.DataFrame) -> pd.DataFrame:
    census_keyed = census_blocked.dropna(subset=["surname_soundex", "birth_year_bucket"])
    parish_keyed = parish_blocked.dropna(subset=["surname_soundex", "birth_year_bucket"])

    merged = census_keyed[["census_record_id", "surname_soundex", "birth_year_bucket"]].merge(
        parish_keyed[["parish_record_id", "surname_soundex", "birth_year_bucket"]],
        on="surname_soundex",
        suffixes=("_census", "_parish"),
    )
    merged = merged[
        (merged["birth_year_bucket_census"] - merged["birth_year_bucket_parish"]).abs() <= 1
    ]
    return merged[["census_record_id", "parish_record_id"]].drop_duplicates().reset_index(drop=True)
