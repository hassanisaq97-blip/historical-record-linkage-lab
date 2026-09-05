import pandas as pd

from linkage_lab import features


def test_build_candidate_features_computes_expected_similarity_values():
    census_std = pd.DataFrame(
        {
            "census_record_id": ["C1"],
            "given_name_std": ["jens"],
            "surname_std": ["hansen"],
            "birth_place_std": ["odense"],
            "age": [30],
            "census_year": [1850],
        }
    )
    parish_std = pd.DataFrame(
        {
            "parish_record_id": ["R1"],
            "given_name_std": ["jens"],
            "surname_std": ["hansen"],
            "birth_place_std": ["odense"],
            "birth_year": [1820],
        }
    )
    pairs = pd.DataFrame({"census_record_id": ["C1"], "parish_record_id": ["R1"]})

    result = features.build_candidate_features(pairs, census_std, parish_std).iloc[0]

    assert result["given_name_jw"] == 1.0
    assert result["surname_jw"] == 1.0
    assert result["given_name_exact"] == 1
    assert result["surname_exact"] == 1
    assert result["birth_year_diff"] == 0
    assert result["birth_place_match"] == 1
    assert result["birth_place_both_observed"] == 1


def test_missing_birth_place_is_not_counted_as_a_mismatch():
    census_std = pd.DataFrame(
        {
            "census_record_id": ["C1"],
            "given_name_std": ["jens"],
            "surname_std": ["hansen"],
            "birth_place_std": [None],
            "age": [30],
            "census_year": [1850],
        }
    )
    parish_std = pd.DataFrame(
        {
            "parish_record_id": ["R1"],
            "given_name_std": ["jens"],
            "surname_std": ["hansen"],
            "birth_place_std": ["odense"],
            "birth_year": [1820],
        }
    )
    pairs = pd.DataFrame({"census_record_id": ["C1"], "parish_record_id": ["R1"]})

    result = features.build_candidate_features(pairs, census_std, parish_std).iloc[0]

    assert result["birth_place_match"] == 0
    assert result["birth_place_both_observed"] == 0
