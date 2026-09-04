import pandas as pd

from linkage_lab import linkage_llm


def test_select_gray_zone_pairs_filters_on_probability_band():
    predictions = pd.DataFrame({"predicted_proba": [0.01, 0.5, 0.9, 0.4]})
    gray_zone = linkage_llm.select_gray_zone_pairs(predictions, low=0.35, high=0.65)
    assert sorted(gray_zone["predicted_proba"].tolist()) == [0.4, 0.5]


def test_build_prompt_includes_all_fields():
    row = pd.Series(
        {
            "census_given_name": "Mette",
            "census_surname": "Petersen",
            "census_year": 1850,
            "census_age": 54,
            "census_birth_place": None,
            "parish_given_name": "Mette",
            "parish_surname": "Pedersen",
            "parish_birth_year": 1791,
            "parish_birth_place": "Slagelse",
        }
    )
    prompt = linkage_llm.build_prompt(row)
    assert "Mette" in prompt
    assert "Petersen" in prompt
    assert "Pedersen" in prompt
    assert "1791" in prompt


def test_parse_response_recognizes_match_and_no_match():
    assert linkage_llm.parse_response("MATCH\nSamme navn og alder.") == 1
    assert linkage_llm.parse_response("NO_MATCH\nForskellige foedesteder.") == 0


def test_parse_response_returns_none_for_unparseable_output():
    assert linkage_llm.parse_response("Jeg er usikker.") is None
    assert linkage_llm.parse_response("") is None


def test_classify_pair_with_llm_uses_injected_client():
    class FakeContentBlock:
        text = "MATCH\nBegrundelse."

    class FakeMessages:
        def create(self, **kwargs):
            class FakeResponse:
                content = [FakeContentBlock()]

            return FakeResponse()

    class FakeClient:
        messages = FakeMessages()

    result = linkage_llm.classify_pair_with_llm("some prompt", FakeClient())
    assert linkage_llm.parse_response(result) == 1
