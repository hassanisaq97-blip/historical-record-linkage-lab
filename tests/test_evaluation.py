import pandas as pd

from linkage_lab import evaluation


def test_compute_metrics_matches_hand_counted_confusion_matrix():
    y_true = pd.Series([1, 1, 1, 0, 0, 0, 0])
    y_pred = pd.Series([1, 1, 0, 1, 0, 0, 0])
    # TP=2, FN=1, FP=1, TN=3
    metrics = evaluation.compute_metrics(y_true, y_pred)

    assert metrics["true_positives"] == 2
    assert metrics["false_negatives"] == 1
    assert metrics["false_positives"] == 1
    assert metrics["true_negatives"] == 3
    assert metrics["precision"] == 2 / 3
    assert metrics["recall"] == 2 / 3
    assert round(metrics["f1"], 6) == round(2 / 3, 6)


def test_compute_metrics_handles_no_positive_predictions():
    y_true = pd.Series([1, 0, 0])
    y_pred = pd.Series([0, 0, 0])
    metrics = evaluation.compute_metrics(y_true, y_pred)
    assert metrics["precision"] == 0
    assert metrics["recall"] == 0
    assert metrics["f1"] == 0


def test_build_comparison_table_indexes_by_method():
    table = evaluation.build_comparison_table(
        {
            "rule_based": {"precision": 0.9, "recall": 0.5},
            "ml": {"precision": 0.7, "recall": 0.9},
        }
    )
    assert list(table.index) == ["rule_based", "ml"]
    assert table.loc["ml", "recall"] == 0.9
