"""Loads the vendored raw OCR text (see data/raw/nyc_directories/PROVENANCE.md),
takes a manageable, reproducible slice, and parses it into structured
records using NYPL's own CRF-based entry parser (parsing.py).
"""

from __future__ import annotations

import pandas as pd

from .. import config
from . import parsing


def load_raw_lines(limit: int | None = config.NYC_DIR_SUBSET_N_LINES) -> list[str]:
    path = config.NYC_DIR_RAW_DIR / "nypl-1851-1852-entries-sample.txt"
    with open(path, encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f if line.strip()]
    return lines[:limit] if limit else lines


def build_parsed_dataset(limit: int | None = config.NYC_DIR_SUBSET_N_LINES) -> pd.DataFrame:
    labeled_csv = config.NYC_DIR_RAW_DIR / "nypl-labeled-70-training.csv"
    classifier = parsing.train_classifier(labeled_csv)

    lines = load_raw_lines(limit)
    parsed = parsing.parse_lines(classifier, lines)

    df = pd.DataFrame([vars(p) for p in parsed])
    df["year"] = config.NYC_DIR_YEAR
    df["source"] = config.NYC_DIR_SOURCE_NAME
    df["record_id"] = [f"{config.NYC_DIR_SOURCE_NAME}_{ln:06d}" for ln in df["line_number"]]

    # A line is flagged as a likely OCR/typesetting column-merge artefact
    # (two directory columns read as one line) when the parser finds more
    # distinct name/occupation/address components than a single entry
    # should have. We keep these records (never silently drop real data)
    # but flag them so downstream steps can treat them with caution.
    df["likely_multi_entry"] = (df["n_addresses_detected"] >= 3) | (
        df["occupation"].fillna("").str.count(";") >= 2
    )

    return df


def save_parsed_dataset(limit: int | None = config.NYC_DIR_SUBSET_N_LINES) -> pd.DataFrame:
    df = build_parsed_dataset(limit)
    out_path = config.NYC_DIR_PROCESSED_DIR / "parsed_entries.csv"
    df.to_csv(out_path, index=False)
    return df


if __name__ == "__main__":
    df = save_parsed_dataset()
    print(f"Parsed {len(df)} entries -> {config.NYC_DIR_PROCESSED_DIR / 'parsed_entries.csv'}")
