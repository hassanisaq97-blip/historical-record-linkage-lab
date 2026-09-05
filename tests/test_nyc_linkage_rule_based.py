import pandas as pd

from linkage_lab.nyc_directories import linkage_rule_based as rb


def test_predict_accepts_strong_name_and_occupation_match():
    features = pd.DataFrame(
        [{"given_name_jw": 0.95, "occupation_jw": 0.95, "occupation_both_observed": 1, "best_address_jw": 0.0}]
    )
    assert rb.predict(features).tolist() == [1]


def test_predict_accepts_strong_name_and_address_match_without_occupation():
    features = pd.DataFrame(
        [{"given_name_jw": 0.95, "occupation_jw": 0.0, "occupation_both_observed": 0, "best_address_jw": 0.95}]
    )
    assert rb.predict(features).tolist() == [1]


def test_predict_rejects_weak_name_similarity_even_with_matches_elsewhere():
    features = pd.DataFrame(
        [{"given_name_jw": 0.5, "occupation_jw": 1.0, "occupation_both_observed": 1, "best_address_jw": 1.0}]
    )
    assert rb.predict(features).tolist() == [0]


def test_predict_rejects_when_no_corroborating_evidence_at_all():
    features = pd.DataFrame(
        [{"given_name_jw": 1.0, "occupation_jw": 0.1, "occupation_both_observed": 1, "best_address_jw": 0.1}]
    )
    assert rb.predict(features).tolist() == [0]
