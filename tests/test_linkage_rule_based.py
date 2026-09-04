import pandas as pd

from linkage_lab import linkage_rule_based as rb


def test_predict_accepts_clear_match():
    features = pd.DataFrame(
        [
            {
                "given_name_jw": 0.95,
                "surname_jw": 0.97,
                "birth_year_diff": 1,
                "birth_place_match": 1,
                "birth_place_both_observed": 1,
            }
        ]
    )
    assert rb.predict(features).tolist() == [1]


def test_predict_rejects_low_similarity():
    features = pd.DataFrame(
        [
            {
                "given_name_jw": 0.40,
                "surname_jw": 0.50,
                "birth_year_diff": 10,
                "birth_place_match": 0,
                "birth_place_both_observed": 1,
            }
        ]
    )
    assert rb.predict(features).tolist() == [0]


def test_predict_missing_birth_place_does_not_block_a_match():
    features = pd.DataFrame(
        [
            {
                "given_name_jw": 0.95,
                "surname_jw": 0.97,
                "birth_year_diff": 0,
                "birth_place_match": 0,
                "birth_place_both_observed": 0,
            }
        ]
    )
    assert rb.predict(features).tolist() == [1]


def test_predict_rejects_large_birth_year_gap_even_with_good_names():
    features = pd.DataFrame(
        [
            {
                "given_name_jw": 1.0,
                "surname_jw": 1.0,
                "birth_year_diff": 5,
                "birth_place_match": 1,
                "birth_place_both_observed": 1,
            }
        ]
    )
    assert rb.predict(features).tolist() == [0]
