from linkage_lab import standardization as std


def test_normalize_text_lowercases_and_strips_diacritics():
    assert std.normalize_text("Kjøbenhavn") == "kjoebenhavn"
    assert std.normalize_text(" Århus ") == "aarhus"


def test_normalize_text_handles_missing_values():
    assert std.normalize_text(None) is None
    assert std.normalize_text(float("nan")) is None
    assert std.normalize_text("") is None


def test_standardize_place_resolves_known_variant_to_canonical():
    assert std.standardize_place("Kjøbenhavn") == std.standardize_place("Koebenhavn")
    assert std.standardize_place("Århus") == std.standardize_place("Aarhus")


def test_standardize_place_passes_through_unknown_place():
    assert std.standardize_place("Nykoebing") == "nykoebing"
