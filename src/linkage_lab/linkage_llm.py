"""Optional, experimental LLM-assisted linkage supplement.

Scope, deliberately narrow: this module does NOT replace the rule-based or
ML linkage methods. It only adjudicates the "gray zone" of candidate pairs
where the ML model's predicted probability is close to the decision
boundary (default 0.35-0.65), i.e. cases the tabular classifier itself is
least confident about.

This module requires network access and the caller's own Anthropic API key
(ANTHROPIC_API_KEY) and is therefore never part of the default pipeline
(`workflow/Snakefile`'s `all` rule) and never contributes to the headline
precision/recall/F1 numbers in the README - those must stay reproducible
by anyone cloning the repository without any paid API access. See
docs/limitations.md for the full rationale.
"""

from __future__ import annotations

import re

import pandas as pd

GRAY_ZONE_LOW = 0.35
GRAY_ZONE_HIGH = 0.65

PROMPT_TEMPLATE = """Du undersøger, om to transskriberede historiske kilde-poster beskriver samme person.

Post A (folketælling):
- Fornavn: {census_given_name}
- Efternavn: {census_surname}
- Alder ved folketælling ({census_year}): {census_age}
- Fødested: {census_birth_place}

Post B (kirkebog):
- Fornavn: {parish_given_name}
- Efternavn: {parish_surname}
- Fødselsår: {parish_birth_year}
- Fødested: {parish_birth_place}

Historiske kilder indeholder ofte stavevarianter og transskriptionsfejl. \
Svar med præcis ét ord på første linje: MATCH eller NO_MATCH. \
Giv derefter en kort begrundelse (maks. 2 sætninger)."""


def select_gray_zone_pairs(
    predictions: pd.DataFrame,
    low: float = GRAY_ZONE_LOW,
    high: float = GRAY_ZONE_HIGH,
) -> pd.DataFrame:
    mask = predictions["predicted_proba"].between(low, high)
    return predictions[mask].copy()


def build_prompt(row: pd.Series) -> str:
    return PROMPT_TEMPLATE.format(
        census_given_name=row["census_given_name"],
        census_surname=row["census_surname"],
        census_year=row["census_year"],
        census_age=row["census_age"],
        census_birth_place=row["census_birth_place"],
        parish_given_name=row["parish_given_name"],
        parish_surname=row["parish_surname"],
        parish_birth_year=row["parish_birth_year"],
        parish_birth_place=row["parish_birth_place"],
    )


def parse_response(text: str) -> int | None:
    """Return 1 for MATCH, 0 for NO_MATCH, or None if the response could
    not be parsed (treated as "no verdict", never silently coerced to a
    match or non-match).
    """
    first_line = text.strip().splitlines()[0].strip().upper() if text.strip() else ""
    if re.fullmatch(r"MATCH", first_line):
        return 1
    if re.fullmatch(r"NO_MATCH", first_line):
        return 0
    return None


def classify_pair_with_llm(prompt: str, client) -> str:
    """`client` must expose an Anthropic-SDK-style
    `.messages.create(model=..., max_tokens=..., messages=[...])` call.
    Kept as an injected dependency so the rest of the module is testable
    without any network access or API key.
    """
    response = client.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text
