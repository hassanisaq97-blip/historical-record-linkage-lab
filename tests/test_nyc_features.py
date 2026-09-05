import pandas as pd

from linkage_lab.nyc_directories import features


def make_entries():
    return pd.DataFrame(
        [
            {
                "record_id": "r1", "given_name_std": "john", "occupation_canonical": "laborers",
                "address_business_std": "32 cliff", "address_home_std": None,
            },
            {
                "record_id": "r2", "given_name_std": "john", "occupation_canonical": "laborers",
                "address_business_std": "32 cliff", "address_home_std": None,
            },
            {
                "record_id": "r3", "given_name_std": "john", "occupation_canonical": "tailors",
                "address_business_std": "99 grand", "address_home_std": None,
            },
        ]
    )


def test_identical_records_score_maximally_similar():
    pairs = pd.DataFrame({"record_id_a": ["r1"], "record_id_b": ["r2"]})
    feats = features.build_candidate_features(pairs, make_entries())
    row = feats.iloc[0]
    assert row["given_name_jw"] == 1.0
    assert row["occupation_exact"] == 1
    assert row["address_business_jw"] == 1.0


def test_different_occupation_and_address_score_low():
    pairs = pd.DataFrame({"record_id_a": ["r1"], "record_id_b": ["r3"]})
    feats = features.build_candidate_features(pairs, make_entries())
    row = feats.iloc[0]
    assert row["occupation_exact"] == 0
    assert row["address_business_jw"] < 0.7


def test_missing_field_is_not_counted_as_mismatch():
    entries = make_entries()
    pairs = pd.DataFrame({"record_id_a": ["r1"], "record_id_b": ["r2"]})
    feats = features.build_candidate_features(pairs, entries)
    row = feats.iloc[0]
    assert row["address_home_both_observed"] == 0
    assert row["address_home_jw"] == 0.0


def test_cross_match_between_business_and_home_address_is_detected():
    entries = pd.DataFrame(
        [
            {
                "record_id": "r1", "given_name_std": "john", "occupation_canonical": "laborers",
                "address_business_std": "32 cliff", "address_home_std": None,
            },
            {
                "record_id": "r4", "given_name_std": "john", "occupation_canonical": "laborers",
                "address_business_std": None, "address_home_std": "32 cliff",
            },
        ]
    )
    pairs = pd.DataFrame({"record_id_a": ["r1"], "record_id_b": ["r4"]})
    feats = features.build_candidate_features(pairs, entries)
    assert feats.iloc[0]["best_address_jw"] == 1.0
