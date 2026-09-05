"""Deterministic standardisation of raw text fields.

Design choice (documented further in docs/limitations.md): place names are
standardised via a small known gazetteer/synonym table, matching how
Link-Lives itself describes "standardisation procedures and synonym
catalogues" for places. Personal names are only case/diacritic-normalised
here, not canonicalised against a known variant dictionary - resolving
name-spelling variation is left to the similarity-based linkage step,
since no such clean ground-truth name catalogue would exist for a real,
unlinked historical source.
"""

from __future__ import annotations

import re

import pandas as pd

from . import reference_data as ref

_DIACRITICS = {"æ": "ae", "ø": "oe", "å": "aa"}


def normalize_text(value) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip().lower()
    for source, target in _DIACRITICS.items():
        text = text.replace(source, target)
    text = re.sub(r"[^a-z]", "", text)
    return text or None


def _build_place_gazetteer() -> dict[str, str]:
    gazetteer: dict[str, str] = {}
    for canonical, variants in ref.PLACE_VARIANTS.items():
        canonical_norm = normalize_text(canonical)
        gazetteer[canonical_norm] = canonical_norm
        for variant in variants:
            gazetteer[normalize_text(variant)] = canonical_norm
    return gazetteer


PLACE_GAZETTEER = _build_place_gazetteer()


def standardize_place(value) -> str | None:
    normalized = normalize_text(value)
    if normalized is None:
        return None
    return PLACE_GAZETTEER.get(normalized, normalized)


def standardize_name(value) -> str | None:
    return normalize_text(value)


def standardize_census(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["given_name_std"] = out["given_name"].map(standardize_name)
    out["surname_std"] = out["surname"].map(standardize_name)
    out["birth_place_std"] = out["birth_place"].map(standardize_place)
    out["residence_place_std"] = out["residence_place"].map(standardize_place)
    return out


def standardize_parish(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["given_name_std"] = out["given_name"].map(standardize_name)
    out["surname_std"] = out["surname"].map(standardize_name)
    out["birth_place_std"] = out["birth_place"].map(standardize_place)
    out["parish_std"] = out["parish"].map(standardize_place)
    return out
