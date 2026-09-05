"""Standardisation for the NYC city directory case study.

Deliberately conservative: we fix specific, well-understood OCR/typesetting
artefacts (a stray space splitting the first letter of a name from the
rest, as in "J ames" -> "James") rather than applying blanket regex
cleanup that could destroy genuine information (e.g. real middle initials,
real abbreviations like "Jno." for John are left as-is, not expanded,
since expansion could be wrong and the similarity-based linkage step is
meant to handle this variation, not standardisation).
"""

from __future__ import annotations

import json
import re

import jellyfish
import pandas as pd

from .. import config

_SPLIT_LETTER_RE = re.compile(r"^([A-Za-z]) ([a-z]{2,})$")

_DIACRITICS = {"æ": "ae", "ø": "oe", "å": "aa"}


def normalize_text(value: str | None) -> str | None:
    """Lowercase, fold diacritics, replace punctuation with spaces and
    collapse whitespace - but, unlike `linkage_lab.standardization.normalize_text`
    (built for single-token synthetic surnames/places), this KEEPS digits
    and word boundaries. City directory fields are often multi-token
    ("Geo W", "331 & 455 Av. 3") where collapsing spaces or dropping
    digits would destroy information the similarity step needs.
    """
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().lower()
    for source, target in _DIACRITICS.items():
        text = text.replace(source, target)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def fix_split_first_letter(name: str | None) -> str | None:
    """"J ames" -> "James", "J ohn" -> "John". A common OCR/typesetting
    artefact in this source where the first letter of a name is separated
    from the rest by a spurious space.
    """
    if not isinstance(name, str):
        return name
    match = _SPLIT_LETTER_RE.match(name.strip())
    if match:
        return match.group(1) + match.group(2)
    return name


def standardize_person_name(name: str | None) -> str | None:
    fixed = fix_split_first_letter(name)
    return normalize_text(fixed)


def load_occupation_vocabulary() -> list[str]:
    path = config.NYC_DIR_RAW_DIR / "nypl_occupations_vocab.json"
    with open(path, encoding="utf-8") as f:
        entries = json.load(f)
    return sorted({normalize_text(e["value"]) for e in entries if e.get("value")})


def build_occupation_canonicalization_map(
    raw_occupations: list[str],
    vocabulary: list[str],
    similarity_threshold: float = 0.95,
    common_prefix_len: int = 3,
) -> dict[str, str | None]:
    """For each distinct normalised occupation string observed in the data,
    find the closest match in the IPUMS-derived historical occupation
    vocabulary (Jaro-Winkler similarity). Below the threshold, or when the
    candidate does not share the observed string's first few characters,
    we keep the observed string as its own canonical form rather than
    forcing a possibly-wrong match.

    The shared-prefix guard exists because Jaro-Winkler alone accepts
    semantically wrong matches at high thresholds - e.g. "widow" (a marital
    status sometimes recorded in the occupation slot) against "window"
    scores 0.956, above a naive 0.90 threshold, despite meaning something
    completely different. Requiring a shared prefix rejects that pair
    ("wid" vs "win") while still keeping genuine matches like
    "tailor"/"tailors". This is a documented, imperfect heuristic, not a
    guarantee - see docs/limitations.md.
    """
    mapping: dict[str, str | None] = {}
    for occ in raw_occupations:
        if not occ:
            mapping[occ] = occ
            continue
        best_match, best_score = None, 0.0
        for vocab_term in vocabulary:
            if vocab_term[:common_prefix_len] != occ[:common_prefix_len]:
                continue
            score = jellyfish.jaro_winkler_similarity(occ, vocab_term)
            if score > best_score:
                best_match, best_score = vocab_term, score
        mapping[occ] = best_match if best_score >= similarity_threshold else occ
    return mapping


def standardize_entries(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["surname_std"] = out["surname"].map(standardize_person_name)
    out["given_name_std"] = out["given_name"].map(standardize_person_name)
    out["occupation_std"] = out["occupation"].map(normalize_text)

    vocabulary = load_occupation_vocabulary()
    unique_occupations = [o for o in out["occupation_std"].dropna().unique()]
    occ_map = build_occupation_canonicalization_map(unique_occupations, vocabulary)
    out["occupation_canonical"] = out["occupation_std"].map(occ_map)

    out["address_business_std"] = out["address_business"].map(normalize_text)
    out["address_home_std"] = out["address_home"].map(normalize_text)
    return out
