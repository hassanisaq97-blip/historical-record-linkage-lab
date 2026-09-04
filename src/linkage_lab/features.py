"""Pairwise similarity features computed for each candidate pair.

Only standardised, source-observed fields are used here. The ground-truth
`person_id` is never touched in this module - it belongs exclusively to
`benchmark.py`, which is the one place allowed to look at it (for labelling
and evaluation, never for linkage itself).
"""

from __future__ import annotations

import jellyfish
import pandas as pd


def _jaro_winkler(a: str | None, b: str | None) -> float:
    if not a or not b:
        return 0.0
    return jellyfish.jaro_winkler_similarity(a, b)


def _exact_match(a: str | None, b: str | None) -> int:
    if not a or not b:
        return 0
    return int(a == b)


def _place_match(a: str | None, b: str | None) -> tuple[int, int]:
    """Returns (match, both_observed). If either side is missing, match=0
    and both_observed=0, so the ML model can distinguish "disagreed" from
    "unknown" instead of silently treating missing data as a mismatch.
    """
    if not a or not b:
        return 0, 0
    return int(a == b), 1


def build_candidate_features(
    pairs: pd.DataFrame,
    census_std: pd.DataFrame,
    parish_std: pd.DataFrame,
) -> pd.DataFrame:
    census_indexed = census_std.set_index("census_record_id")
    parish_indexed = parish_std.set_index("parish_record_id")

    rows = []
    for pair in pairs.itertuples(index=False):
        c = census_indexed.loc[pair.census_record_id]
        p = parish_indexed.loc[pair.parish_record_id]

        implied_birth_year_census = int(c["census_year"] - c["age"])
        birth_year_diff = abs(implied_birth_year_census - int(p["birth_year"]))

        place_match, place_both_observed = _place_match(c["birth_place_std"], p["birth_place_std"])

        rows.append(
            {
                "census_record_id": pair.census_record_id,
                "parish_record_id": pair.parish_record_id,
                "given_name_jw": _jaro_winkler(c["given_name_std"], p["given_name_std"]),
                "surname_jw": _jaro_winkler(c["surname_std"], p["surname_std"]),
                "given_name_exact": _exact_match(c["given_name_std"], p["given_name_std"]),
                "surname_exact": _exact_match(c["surname_std"], p["surname_std"]),
                "birth_year_diff": birth_year_diff,
                "birth_place_match": place_match,
                "birth_place_both_observed": place_both_observed,
            }
        )
    return pd.DataFrame(rows)
