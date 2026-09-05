import pandas as pd

from linkage_lab import blocking


def make_census_std():
    return pd.DataFrame(
        {
            "census_record_id": ["C1", "C2"],
            "surname_std": ["jensen", "hansen"],
            "age": [30, 40],
            "census_year": [1850, 1850],
        }
    )


def make_parish_std():
    return pd.DataFrame(
        {
            "parish_record_id": ["R1", "R2", "R3"],
            "surname_std": ["jensen", "hansen", "olsen"],
            "birth_year": [1821, 1900, 1810],
        }
    )


def test_blocking_keys_use_soundex_and_year_bucket():
    census_blocked = blocking.add_blocking_keys_census(make_census_std())
    row = census_blocked.loc[census_blocked["census_record_id"] == "C1"].iloc[0]
    assert row["surname_soundex"] is not None
    assert row["birth_year_bucket"] == (1850 - 30) // blocking.config.BLOCKING_YEAR_BUCKET


def test_candidate_pairs_only_within_soundex_and_year_tolerance():
    census_blocked = blocking.add_blocking_keys_census(make_census_std())
    parish_blocked = blocking.add_blocking_keys_parish(make_parish_std())

    pairs = blocking.generate_candidate_pairs(census_blocked, parish_blocked)

    # C1 (Jensen, born ~1820) should candidate-match R1 (Jensen, 1821) but
    # not R2 (Hansen) or R3 (Olsen, different surname soundex).
    c1_matches = set(pairs.loc[pairs["census_record_id"] == "C1", "parish_record_id"])
    assert c1_matches == {"R1"}

    # C2 (Hansen, born ~1810) should not match R2 (Hansen, born 1900):
    # same surname soundex, but birth-year buckets are far apart.
    c2_matches = set(pairs.loc[pairs["census_record_id"] == "C2", "parish_record_id"])
    assert "R2" not in c2_matches


def test_candidate_pairs_have_no_duplicates():
    census_blocked = blocking.add_blocking_keys_census(make_census_std())
    parish_blocked = blocking.add_blocking_keys_parish(make_parish_std())
    pairs = blocking.generate_candidate_pairs(census_blocked, parish_blocked)
    assert not pairs.duplicated().any()
