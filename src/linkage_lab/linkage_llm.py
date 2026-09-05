"""Optional, experimental LLM-assisted linkage supplement for the
synthetic pipeline. Adapts the generic Ollama client in `llm_assist.py`
to this pipeline's census/parish record schema.

Scope, deliberately narrow: this module does NOT replace the rule-based
or ML linkage methods. It only adjudicates the "gray zone" of candidate
pairs where the ML model's predicted probability is close to the decision
boundary (default 0.35-0.65), i.e. cases the tabular classifier itself is
least confident about.

Requires a local Ollama server (https://ollama.com) and is therefore
never part of the default pipeline (`workflow/Snakefile`'s `all` rule)
and never contributes to the headline precision/recall/F1 numbers in the
README - those must stay reproducible by anyone cloning the repository
without any extra runtime dependency. See docs/limitations.md.
"""

from __future__ import annotations

import pandas as pd

from . import llm_assist

GRAY_ZONE_LOW = 0.35
GRAY_ZONE_HIGH = 0.65


def select_gray_zone_pairs(
    predictions: pd.DataFrame,
    low: float = GRAY_ZONE_LOW,
    high: float = GRAY_ZONE_HIGH,
) -> pd.DataFrame:
    mask = predictions["predicted_proba"].between(low, high)
    return predictions[mask].copy()


def row_to_census_record(row: pd.Series) -> dict:
    return {
        "fornavn": row.get("census_given_name"),
        "efternavn": row.get("census_surname"),
        "alder_ved_folketaelling": row.get("census_age"),
        "folketaellingsaar": row.get("census_year"),
        "foedested": row.get("census_birth_place"),
    }


def row_to_parish_record(row: pd.Series) -> dict:
    return {
        "fornavn": row.get("parish_given_name"),
        "efternavn": row.get("parish_surname"),
        "foedselsaar": row.get("parish_birth_year"),
        "foedested": row.get("parish_birth_place"),
    }


def classify_gray_zone_pairs(
    gray_zone: pd.DataFrame,
    model: str = llm_assist.DEFAULT_MODEL,
    url: str = llm_assist.DEFAULT_OLLAMA_URL,
) -> pd.DataFrame:
    """Calls the local Ollama server once per gray-zone pair. Rows where
    the call fails (Ollama unavailable, timeout, malformed/invalid
    output) get `llm_same_person=None` and a populated `llm_error_reason`
    - never a guessed verdict.
    """
    verdicts, confidences, reasonings, errors = [], [], [], []
    for _, row in gray_zone.iterrows():
        result = llm_assist.classify_pair(row_to_census_record(row), row_to_parish_record(row), model=model, url=url)
        if isinstance(result, llm_assist.LlmVerdict):
            verdicts.append(result.same_person)
            confidences.append(result.confidence)
            reasonings.append(result.reasoning_summary)
            errors.append(None)
        else:
            verdicts.append(None)
            confidences.append(None)
            reasonings.append(None)
            errors.append(result.reason)

    out = gray_zone.copy()
    out["llm_same_person"] = verdicts
    out["llm_confidence"] = confidences
    out["llm_reasoning"] = reasonings
    out["llm_error_reason"] = errors
    return out
