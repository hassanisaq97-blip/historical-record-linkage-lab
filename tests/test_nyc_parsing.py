import csv

import pytest

from linkage_lab.nyc_directories import parsing

# Minimal labeled examples in the same format as NYPL's own
# nypl-labeled-70-training.csv (id, token, label), just enough for the CRF
# to train without error - this test checks the parsing *pipeline*, not
# model quality (that's covered by parsing.cross_validate_parser on the
# real 70-example file, reported in results/reports/nyc_directories/).
LABELED_ROWS = [
    (1, "START", "START"),
    (1, "Cappelmann", "NC"), (1, "Otto", "NC"), (1, ",", "D"), (1, "grocer", "OC"),
    (1, ",", "D"), (1, "133", "AC"), (1, "Washington", "AC"),
    (1, "END", "END"),
    (2, "START", "START"),
    (2, "Smith", "NC"), (2, "John", "NC"), (2, ",", "D"), (2, "tailor", "OC"),
    (2, ",", "D"), (2, "45", "AC"), (2, "Broadway", "AC"),
    (2, "END", "END"),
]


@pytest.fixture
def labeled_csv(tmp_path):
    path = tmp_path / "labeled.csv"
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows(LABELED_ROWS)
    return path


def test_train_classifier_and_parse_line(labeled_csv):
    classifier = parsing.train_classifier(labeled_csv)
    result = parsing.parse_line(classifier, 1, "Cappelmann Otto, grocer, 133 Washington")
    assert result.surname == "Cappelmann"
    assert result.given_name == "Otto"
    assert result.parse_ok is True


def test_parse_lines_returns_one_entry_per_line(labeled_csv):
    classifier = parsing.train_classifier(labeled_csv)
    results = parsing.parse_lines(classifier, ["Smith John, tailor, 45 Broadway"] * 3, start_line=10)
    assert [r.line_number for r in results] == [10, 11, 12]
    assert all(r.raw_line == "Smith John, tailor, 45 Broadway" for r in results)


def test_parse_line_never_raises_on_empty_string(labeled_csv):
    classifier = parsing.train_classifier(labeled_csv)
    result = parsing.parse_line(classifier, 1, "")
    assert result.raw_line == ""
