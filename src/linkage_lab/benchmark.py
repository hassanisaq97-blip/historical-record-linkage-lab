"""Gold-standard labelling and entity-level train/test split.

This is the only module allowed to read the synthetic ground-truth
`person_id`. It is used exclusively to (a) label a candidate pair as a true
match/non-match and (b) assign records to train/test so that no single
individual's records leak across the split.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config


def assign_entity_split(
    person_ids: pd.Series,
    rng: np.random.Generator,
    train_fraction: float = config.TRAIN_FRACTION,
) -> dict[str, str]:
    unique_ids = sorted(person_ids.unique())
    shuffled = list(unique_ids)
    rng.shuffle(shuffled)
    n_train = int(round(len(shuffled) * train_fraction))
    train_ids = set(shuffled[:n_train])
    return {pid: ("train" if pid in train_ids else "test") for pid in unique_ids}


def build_labeled_pairs(
    candidate_pairs: pd.DataFrame,
    census_raw: pd.DataFrame,
    parish_raw: pd.DataFrame,
    split_map: dict[str, str],
) -> pd.DataFrame:
    census_ids = census_raw.set_index("census_record_id")["person_id"]
    parish_ids = parish_raw.set_index("parish_record_id")["person_id"]

    out = candidate_pairs.copy()
    out["person_id_census"] = out["census_record_id"].map(census_ids)
    out["person_id_parish"] = out["parish_record_id"].map(parish_ids)
    out["is_true_match"] = (out["person_id_census"] == out["person_id_parish"]).astype(int)

    split_census = out["person_id_census"].map(split_map)
    split_parish = out["person_id_parish"].map(split_map)

    out["split"] = np.where(
        (split_census == "train") & (split_parish == "train"),
        "train",
        np.where(
            (split_census == "test") & (split_parish == "test"),
            "test",
            "excluded",
        ),
    )
    return out


def build_full_benchmark(
    candidate_pairs: pd.DataFrame,
    census_raw: pd.DataFrame,
    parish_raw: pd.DataFrame,
    seed: int = config.RANDOM_SEED,
) -> pd.DataFrame:
    all_person_ids = pd.concat([census_raw["person_id"], parish_raw["person_id"]])
    rng = np.random.default_rng(seed)
    split_map = assign_entity_split(all_person_ids, rng)
    return build_labeled_pairs(candidate_pairs, census_raw, parish_raw, split_map)
