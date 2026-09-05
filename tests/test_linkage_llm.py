import pandas as pd

from linkage_lab import linkage_llm, llm_assist


def test_select_gray_zone_pairs_filters_on_probability_band():
    predictions = pd.DataFrame({"predicted_proba": [0.01, 0.5, 0.9, 0.4]})
    gray_zone = linkage_llm.select_gray_zone_pairs(predictions, low=0.35, high=0.65)
    assert sorted(gray_zone["predicted_proba"].tolist()) == [0.4, 0.5]


def test_row_to_census_and_parish_record_map_expected_fields():
    row = pd.Series(
        {
            "census_given_name": "Jens",
            "census_surname": "Hansen",
            "census_age": 40,
            "census_year": 1850,
            "census_birth_place": "Odense",
            "parish_given_name": "Jens",
            "parish_surname": "Hansen",
            "parish_birth_year": 1810,
            "parish_birth_place": "Odense",
        }
    )
    census_record = linkage_llm.row_to_census_record(row)
    parish_record = linkage_llm.row_to_parish_record(row)
    assert census_record["fornavn"] == "Jens"
    assert census_record["folketaellingsaar"] == 1850
    assert parish_record["foedselsaar"] == 1810


def test_classify_gray_zone_pairs_records_error_reason_when_ollama_unavailable(monkeypatch):
    def fake_classify_pair(record_a, record_b, model, url):
        return llm_assist.LlmError("ollama_unavailable", "no server")

    monkeypatch.setattr(llm_assist, "classify_pair", fake_classify_pair)

    gray_zone = pd.DataFrame(
        [
            {
                "census_given_name": "Jens", "census_surname": "Hansen", "census_age": 40,
                "census_year": 1850, "census_birth_place": "Odense",
                "parish_given_name": "Jens", "parish_surname": "Hansen",
                "parish_birth_year": 1810, "parish_birth_place": "Odense",
            }
        ]
    )
    result = linkage_llm.classify_gray_zone_pairs(gray_zone)
    assert result.loc[0, "llm_same_person"] is None
    assert result.loc[0, "llm_error_reason"] == "ollama_unavailable"


def test_classify_gray_zone_pairs_records_verdict_on_success(monkeypatch):
    def fake_classify_pair(record_a, record_b, model, url):
        return llm_assist.LlmVerdict(True, 0.8, "Samme navn.", "{}")

    monkeypatch.setattr(llm_assist, "classify_pair", fake_classify_pair)

    gray_zone = pd.DataFrame(
        [
            {
                "census_given_name": "Jens", "census_surname": "Hansen", "census_age": 40,
                "census_year": 1850, "census_birth_place": "Odense",
                "parish_given_name": "Jens", "parish_surname": "Hansen",
                "parish_birth_year": 1810, "parish_birth_place": "Odense",
            }
        ]
    )
    result = linkage_llm.classify_gray_zone_pairs(gray_zone)
    assert result.loc[0, "llm_same_person"] == True
    assert result.loc[0, "llm_confidence"] == 0.8
    assert result.loc[0, "llm_error_reason"] is None
