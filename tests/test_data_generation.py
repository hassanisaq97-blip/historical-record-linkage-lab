import pandas as pd

from linkage_lab import data_generation as dg


def test_generate_all_is_reproducible_given_same_seed():
    first = dg.generate_all(seed=123)
    second = dg.generate_all(seed=123)
    for key in first:
        pd.testing.assert_frame_equal(first[key], second[key])


def test_generate_all_produces_different_data_for_different_seeds():
    first = dg.generate_all(seed=1)
    second = dg.generate_all(seed=2)
    assert not first["census"]["given_name"].equals(second["census"]["given_name"])


def test_population_has_expected_schema_and_no_duplicate_ids():
    population = dg.generate_all(seed=42)["population"]
    expected_columns = {"person_id", "given_name", "surname", "gender", "birth_year", "birth_place"}
    assert expected_columns <= set(population.columns)
    assert population["person_id"].is_unique


def test_census_and_parish_only_reference_known_person_ids():
    datasets = dg.generate_all(seed=42)
    known_ids = set(datasets["population"]["person_id"])
    assert set(datasets["census"]["person_id"]) <= known_ids
    assert set(datasets["parish_register"]["person_id"]) <= known_ids


def test_census_age_is_non_negative_for_most_records():
    census = dg.generate_all(seed=42)["census"]
    # A small fraction of records get a deliberate large "blunder" error
    # (see noise_model.noisy_integer), so we only require this to hold for
    # the large majority, not every single record.
    share_non_negative = (census["age"] >= 0).mean()
    assert share_non_negative > 0.9
