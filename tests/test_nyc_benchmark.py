import pandas as pd
import pytest

from linkage_lab.nyc_directories import benchmark


def test_build_labeled_features_merges_and_splits():
    features = pd.DataFrame(
        {
            "record_id_a": [f"a{i}" for i in range(10)],
            "record_id_b": [f"b{i}" for i in range(10)],
            "given_name_jw": [0.5] * 10,
        }
    )
    labels = pd.DataFrame(
        {
            "record_id_a": [f"a{i}" for i in range(10)],
            "record_id_b": [f"b{i}" for i in range(10)],
            "is_match": [1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        }
    )
    labeled = benchmark.build_labeled_features(features, labels, train_fraction=0.6)
    assert len(labeled) == 10
    assert set(labeled["split"]) <= {"train", "test"}
    # Stratified: both classes should appear in both splits when possible.
    for split in ("train", "test"):
        subset = labeled[labeled["split"] == split]
        assert subset["is_match"].nunique() >= 1


def test_build_labeled_features_raises_on_unmatched_labels():
    features = pd.DataFrame({"record_id_a": ["a0"], "record_id_b": ["b0"], "x": [1]})
    labels = pd.DataFrame({"record_id_a": ["a0", "a1"], "record_id_b": ["b0", "b1"], "is_match": [1, 0]})
    with pytest.raises(ValueError):
        benchmark.build_labeled_features(features, labels)
