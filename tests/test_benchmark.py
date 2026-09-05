import numpy as np
import pandas as pd

from linkage_lab import benchmark


def test_assign_entity_split_covers_all_ids_without_overlap():
    ids = pd.Series([f"P{i}" for i in range(100)])
    rng = np.random.default_rng(0)
    split_map = benchmark.assign_entity_split(ids, rng, train_fraction=0.7)

    assert set(split_map.keys()) == set(ids)
    values = list(split_map.values())
    assert values.count("train") == 70
    assert values.count("test") == 30


def test_build_labeled_pairs_labels_true_matches_correctly():
    candidate_pairs = pd.DataFrame(
        {"census_record_id": ["C1", "C2"], "parish_record_id": ["R1", "R2"]}
    )
    census_raw = pd.DataFrame({"census_record_id": ["C1", "C2"], "person_id": ["P1", "P2"]})
    parish_raw = pd.DataFrame({"parish_record_id": ["R1", "R2"], "person_id": ["P1", "P3"]})
    split_map = {"P1": "train", "P2": "train", "P3": "test"}

    labeled = benchmark.build_labeled_pairs(candidate_pairs, census_raw, parish_raw, split_map)

    row_c1 = labeled.set_index("census_record_id").loc["C1"]
    row_c2 = labeled.set_index("census_record_id").loc["C2"]

    assert row_c1["is_true_match"] == 1
    assert row_c1["split"] == "train"  # both P1 records are in "train"

    assert row_c2["is_true_match"] == 0
    assert row_c2["split"] == "excluded"  # P2 is "train", P3 is "test" -> no leakage allowed
