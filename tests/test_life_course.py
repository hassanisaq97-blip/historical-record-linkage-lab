import pandas as pd

from linkage_lab import life_course
from linkage_lab.data_generation import PLAUSIBLE_BIRTH_YEAR_MIN
from linkage_lab.config import MAX_PLAUSIBLE_BIRTH_YEAR_SPREAD


def make_census_raw():
    return pd.DataFrame(
        {
            "census_record_id": ["C1", "C2", "C3"],
            "age": [30, 30, 30],
            "census_year": [1850, 1850, 1850],
        }
    )


def make_parish_raw():
    return pd.DataFrame(
        {
            "parish_record_id": ["R1", "R2", "R3"],
            "birth_year": [
                1820,
                1820 + MAX_PLAUSIBLE_BIRTH_YEAR_SPREAD + 5,
                PLAUSIBLE_BIRTH_YEAR_MIN - 5,
            ],
        }
    )


def test_clean_one_to_one_link_is_not_flagged():
    pairs = pd.DataFrame({"census_record_id": ["C1"], "parish_record_id": ["R1"]})
    graph = life_course.build_link_graph(pairs, make_census_raw(), make_parish_raw())
    checks = life_course.run_sanity_checks(graph)
    assert len(checks) == 1
    assert bool(checks.iloc[0]["flagged"]) is False


def test_one_census_record_linked_to_two_parish_records_is_flagged_multi_match():
    pairs = pd.DataFrame(
        {"census_record_id": ["C1", "C1"], "parish_record_id": ["R1", "R2"]}
    )
    graph = life_course.build_link_graph(pairs, make_census_raw(), make_parish_raw())
    checks = life_course.run_sanity_checks(graph)
    assert len(checks) == 1
    assert "multi_match" in checks.iloc[0]["issues"]


def test_large_birth_year_gap_is_flagged_conflict():
    pairs = pd.DataFrame({"census_record_id": ["C2"], "parish_record_id": ["R2"]})
    graph = life_course.build_link_graph(pairs, make_census_raw(), make_parish_raw())
    checks = life_course.run_sanity_checks(graph)
    assert "birth_year_conflict" in checks.iloc[0]["issues"]


def test_implausible_birth_year_is_flagged():
    pairs = pd.DataFrame({"census_record_id": ["C3"], "parish_record_id": ["R3"]})
    graph = life_course.build_link_graph(pairs, make_census_raw(), make_parish_raw())
    checks = life_course.run_sanity_checks(graph)
    assert "implausible_birth_year" in checks.iloc[0]["issues"]
