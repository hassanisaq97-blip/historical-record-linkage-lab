"""Pairwise similarity features for candidate pairs of city-directory
entries. Missing fields are tracked with explicit "both observed"
indicators rather than treated as mismatches, for the same reason as in
the synthetic pipeline: a directory entry with no listed home address is
not evidence against a match, it is simply missing information.
"""

from __future__ import annotations

import jellyfish
import pandas as pd


def _jaro_winkler(a, b) -> float:
    if not isinstance(a, str) or not isinstance(b, str) or not a or not b:
        return 0.0
    return jellyfish.jaro_winkler_similarity(a, b)


def _exact_match(a, b) -> int:
    if not isinstance(a, str) or not isinstance(b, str) or not a or not b:
        return 0
    return int(a == b)


def _both_observed(a, b) -> int:
    return int(isinstance(a, str) and bool(a) and isinstance(b, str) and bool(b))


def build_candidate_features(pairs: pd.DataFrame, entries: pd.DataFrame) -> pd.DataFrame:
    indexed = entries.set_index("record_id")

    rows = []
    for pair in pairs.itertuples(index=False):
        a = indexed.loc[pair.record_id_a]
        b = indexed.loc[pair.record_id_b]

        # Note: an "initials match" feature is deliberately omitted - blocking
        # already requires identical first initial, so within the candidate
        # set the feature would be constant and uninformative (the same
        # blocking-key-as-feature redundancy documented for surname_jw in
        # the synthetic pipeline's README).
        given_name_jw = _jaro_winkler(a["given_name_std"], b["given_name_std"])
        given_name_exact = _exact_match(a["given_name_std"], b["given_name_std"])

        occupation_jw = _jaro_winkler(a["occupation_canonical"], b["occupation_canonical"])
        occupation_exact = _exact_match(a["occupation_canonical"], b["occupation_canonical"])
        occupation_both_observed = _both_observed(a["occupation_canonical"], b["occupation_canonical"])

        address_business_jw = _jaro_winkler(a["address_business_std"], b["address_business_std"])
        address_business_both_observed = _both_observed(a["address_business_std"], b["address_business_std"])

        address_home_jw = _jaro_winkler(a["address_home_std"], b["address_home_std"])
        address_home_both_observed = _both_observed(a["address_home_std"], b["address_home_std"])

        # A business address on one record matching a home address on the
        # other is still positive evidence (business and residence are
        # often reported inconsistently across duplicate/near-duplicate
        # listings), so we also take the best cross-match.
        cross_jw = max(
            _jaro_winkler(a["address_business_std"], b["address_home_std"]),
            _jaro_winkler(a["address_home_std"], b["address_business_std"]),
        )
        best_address_jw = max(address_business_jw, address_home_jw, cross_jw)

        rows.append(
            {
                "record_id_a": pair.record_id_a,
                "record_id_b": pair.record_id_b,
                "given_name_jw": given_name_jw,
                "given_name_exact": given_name_exact,
                "occupation_jw": occupation_jw,
                "occupation_exact": occupation_exact,
                "occupation_both_observed": occupation_both_observed,
                "address_business_jw": address_business_jw,
                "address_business_both_observed": address_business_both_observed,
                "address_home_jw": address_home_jw,
                "address_home_both_observed": address_home_both_observed,
                "best_address_jw": best_address_jw,
            }
        )
    return pd.DataFrame(rows)
