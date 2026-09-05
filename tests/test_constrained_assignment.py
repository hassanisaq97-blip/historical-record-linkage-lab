import pandas as pd

from linkage_lab import constrained_assignment as ca


def test_count_conflicts_detects_records_used_more_than_once():
    pairs = pd.DataFrame(
        {"id_a": ["c1", "c1", "c2"], "id_b": ["p1", "p2", "p3"]}
    )
    assert ca.count_conflicts(pairs, "id_a", "id_b") == 1  # only c1 is reused


def test_count_conflicts_is_zero_when_bipartite_and_disjoint():
    pairs = pd.DataFrame({"id_a": ["c1", "c2"], "id_b": ["p1", "p2"]})
    assert ca.count_conflicts(pairs, "id_a", "id_b") == 0


def test_solve_one_to_one_assignment_keeps_highest_scoring_edge_on_conflict():
    # c1 competes for p1 (score 0.9) and p2 (score 0.4); c2 only wants p2 (score 0.8).
    pairs = pd.DataFrame(
        {
            "id_a": ["c1", "c1", "c2"],
            "id_b": ["p1", "p2", "p2"],
            "score": [0.9, 0.4, 0.8],
        }
    )
    result = ca.solve_one_to_one_assignment(pairs, "id_a", "id_b", "score")
    pairs_set = set(zip(result["id_a"], result["id_b"]))
    # Best total-weight matching: (c1,p1)=0.9 + (c2,p2)=0.8 = 1.7, beats (c1,p2)=0.4 alone.
    assert ("c1", "p1") in pairs_set
    assert ("c2", "p2") in pairs_set
    assert ca.count_conflicts(result, "id_a", "id_b") == 0


def test_solve_one_to_one_assignment_handles_empty_input():
    empty = pd.DataFrame(columns=["id_a", "id_b", "score"])
    result = ca.solve_one_to_one_assignment(empty, "id_a", "id_b", "score")
    assert result.empty


def test_solve_one_to_one_assignment_works_on_non_bipartite_graph():
    # Within-source case (nyc_directories): ids overlap across both columns.
    pairs = pd.DataFrame(
        {
            "id_a": ["r1", "r1", "r3"],
            "id_b": ["r2", "r3", "r4"],
            "score": [0.5, 0.9, 0.3],
        }
    )
    result = ca.solve_one_to_one_assignment(pairs, "id_a", "id_b", "score")
    # r1-r3 (0.9) blocks r1-r2 and shares r3 with r3-r4; best matching picks
    # r1-r2 (0.5) + ... actually best total weight compares {r1-r3}=0.9 vs
    # {r1-r2, r3-r4}=0.5+0.3=0.8, so r1-r3 alone should win.
    pairs_set = set(zip(result["id_a"], result["id_b"]))
    assert pairs_set == {("r1", "r3")}
    assert ca.count_conflicts(result, "id_a", "id_b") == 0
