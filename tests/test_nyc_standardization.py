import pandas as pd

from linkage_lab.nyc_directories import standardization as std


def test_fix_split_first_letter_repairs_known_ocr_artifact():
    assert std.fix_split_first_letter("J ames") == "James"
    assert std.fix_split_first_letter("J ohn") == "John"


def test_fix_split_first_letter_leaves_normal_names_untouched():
    assert std.fix_split_first_letter("James") == "James"
    assert std.fix_split_first_letter("Geo W") == "Geo W"


def test_normalize_text_keeps_digits_and_word_boundaries():
    assert std.normalize_text("331 & 455 Av. 3") == "331 455 av 3"
    assert std.normalize_text("Geo W") == "geo w"


def test_normalize_text_handles_missing_values():
    assert std.normalize_text(None) is None
    assert std.normalize_text("") is None
    assert std.normalize_text(float("nan")) is None


def test_standardize_person_name_combines_ocr_fix_and_normalization():
    assert std.standardize_person_name("J ames") == "james"


def test_occupation_canonicalization_rejects_similar_but_wrong_match():
    # "widow" vs "window": high Jaro-Winkler similarity but different first
    # letters after "wi", and different meaning entirely.
    vocab = ["window", "laborer"]
    mapping = std.build_occupation_canonicalization_map(["widow"], vocab, similarity_threshold=0.90)
    assert mapping["widow"] == "widow"  # kept as-is, not force-matched to "window"


def test_occupation_canonicalization_accepts_genuine_variant():
    vocab = ["laborers"]
    mapping = std.build_occupation_canonicalization_map(["laborer"], vocab, similarity_threshold=0.90)
    assert mapping["laborer"] == "laborers"


def test_standardize_entries_produces_expected_columns():
    df = pd.DataFrame(
        [
            {
                "surname": "Bussing", "given_name": "J ames", "occupation": "laborer",
                "address_business": "32 Cliff", "address_home": None,
            }
        ]
    )
    out = std.standardize_entries(df)
    assert out.loc[0, "given_name_std"] == "james"
    assert out.loc[0, "surname_std"] == "bussing"
    assert out.loc[0, "address_business_std"] == "32 cliff"
