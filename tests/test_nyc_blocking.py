import pandas as pd

from linkage_lab.nyc_directories import blocking


def make_entries():
    return pd.DataFrame(
        {
            "record_id": ["r1", "r2", "r3", "r4"],
            "surname_std": ["cook", "cook", "cook", "clark"],
            "given_name_std": ["john", "john", "james", "john"],
        }
    )


def test_add_blocking_keys_computes_soundex_and_initial():
    blocked = blocking.add_blocking_keys(make_entries())
    assert blocked.loc[0, "surname_soundex"] == blocked.loc[1, "surname_soundex"]
    assert blocked.loc[0, "given_name_initial"] == "j"


def test_generate_candidate_pairs_only_within_same_block():
    blocked = blocking.add_blocking_keys(make_entries())
    pairs = blocking.generate_candidate_pairs(blocked)
    pair_set = {frozenset(p) for p in zip(pairs["record_id_a"], pairs["record_id_b"])}
    # r1 & r2 share surname soundex + initial "j" -> candidate pair.
    assert frozenset({"r1", "r2"}) in pair_set
    # r4 has a different surname ("clark" vs "cook") -> never blocked with r1/r2/r3.
    assert not any("r4" in p for p in pair_set)


def test_generate_candidate_pairs_has_no_self_pairs_or_duplicates():
    blocked = blocking.add_blocking_keys(make_entries())
    pairs = blocking.generate_candidate_pairs(blocked)
    assert (pairs["record_id_a"] != pairs["record_id_b"]).all()
    assert not pairs.duplicated().any()


def test_compute_reduction_stats_matches_combinatorics():
    stats = blocking.compute_reduction_stats(n_records=100, n_candidate_pairs=50)
    assert stats["all_possible_pairs"] == 100 * 99 // 2
    assert stats["reduction_ratio"] == 1 - (50 / (100 * 99 // 2))
