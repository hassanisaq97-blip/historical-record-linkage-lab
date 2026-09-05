import pandas as pd

from linkage_lab.nyc_directories import entity_resolution as er


def make_entries():
    return pd.DataFrame(
        [
            {"record_id": "r1", "surname_std": "cook", "given_name_std": "john", "occupation_canonical": "laborers", "address_business_std": "32 cliff", "address_home_std": None},
            {"record_id": "r2", "surname_std": "cook", "given_name_std": "john", "occupation_canonical": "laborers", "address_business_std": "32 cliff", "address_home_std": None},
            {"record_id": "r3", "surname_std": "cook", "given_name_std": "john", "occupation_canonical": "tailors", "address_business_std": "99 grand", "address_home_std": None},
        ]
    )


def test_clean_pair_is_not_flagged():
    accepted = pd.DataFrame(
        [{"record_id_a": "r1", "record_id_b": "r2", "predicted_proba": 0.95, "occupation_jw": 1.0, "best_address_jw": 1.0}]
    )
    graph = er.build_link_graph(accepted, make_entries())
    checks = er.run_sanity_checks(graph)
    assert len(checks) == 1
    assert bool(checks.iloc[0]["flagged"]) is False


def test_one_record_linked_to_two_others_is_flagged_multi_match():
    accepted = pd.DataFrame(
        [
            {"record_id_a": "r1", "record_id_b": "r2", "predicted_proba": 0.9, "occupation_jw": 1.0, "best_address_jw": 1.0},
            {"record_id_a": "r1", "record_id_b": "r3", "predicted_proba": 0.6, "occupation_jw": 0.2, "best_address_jw": 0.1},
        ]
    )
    graph = er.build_link_graph(accepted, make_entries())
    checks = er.run_sanity_checks(graph)
    assert len(checks) == 1
    assert "multi_match" in checks.iloc[0]["issues"]


def test_strongly_conflicting_occupation_is_flagged():
    accepted = pd.DataFrame(
        [{"record_id_a": "r1", "record_id_b": "r3", "predicted_proba": 0.55, "occupation_jw": 0.1, "best_address_jw": 0.05}]
    )
    graph = er.build_link_graph(accepted, make_entries())
    checks = er.run_sanity_checks(graph)
    assert "conflicting_occupation" in checks.iloc[0]["issues"]
    assert "conflicting_address" in checks.iloc[0]["issues"]


def test_isolated_records_are_excluded_from_the_graph():
    accepted = pd.DataFrame(
        [{"record_id_a": "r1", "record_id_b": "r2", "predicted_proba": 0.9, "occupation_jw": 1.0, "best_address_jw": 1.0}]
    )
    graph = er.build_link_graph(accepted, make_entries())
    assert "r3" not in graph.nodes
