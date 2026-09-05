"""Blocking for within-source entity resolution in the city directory.

Unlike the synthetic pipeline (which blocks two separate tables against
each other), this is a single source: candidate pairs are combinations of
records that share a block key, not a cross-join of two tables. The block
key is the classical genealogical pairing of Soundex(surname) + first
initial of the given name - a well-established blocking key in the record
linkage literature, chosen here because no birth year is available to
narrow candidates the way the synthetic pipeline does.
"""

from __future__ import annotations

from itertools import combinations

import jellyfish
import pandas as pd


def _soundex(value) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return jellyfish.soundex(value)


def _first_initial(value) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return value.strip()[0]


def add_blocking_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["surname_soundex"] = out["surname_std"].map(_soundex)
    out["given_name_initial"] = out["given_name_std"].map(_first_initial)
    return out


def generate_candidate_pairs(blocked: pd.DataFrame) -> pd.DataFrame:
    """All within-block combinations of record_id, as an (id_a, id_b) table
    with id_a < id_b (no self-pairs, no reversed duplicates).
    """
    keyed = blocked.dropna(subset=["surname_soundex", "given_name_initial"])
    pairs: list[tuple[str, str]] = []
    for _, group in keyed.groupby(["surname_soundex", "given_name_initial"]):
        ids = sorted(group["record_id"].tolist())
        if len(ids) < 2:
            continue
        pairs.extend(combinations(ids, 2))
    return pd.DataFrame(pairs, columns=["record_id_a", "record_id_b"]).drop_duplicates().reset_index(drop=True)


def compute_reduction_stats(n_records: int, n_candidate_pairs: int) -> dict:
    all_pairs = n_records * (n_records - 1) // 2
    return {
        "n_records": n_records,
        "all_possible_pairs": all_pairs,
        "candidate_pairs": n_candidate_pairs,
        "reduction_ratio": 1 - (n_candidate_pairs / all_pairs) if all_pairs else 0.0,
    }
