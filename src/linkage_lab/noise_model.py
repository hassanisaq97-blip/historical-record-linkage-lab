"""Noise operators used to turn a clean ground-truth attribute into a
plausibly-transcribed, source-specific observation. Each function is a pure
function of (value, rng) so that the whole pipeline stays reproducible from
a single random seed.
"""

import string

import numpy as np

DANISH_ALPHABET = list(string.ascii_lowercase) + ["ae", "oe", "aa"]


def random_char_edit(text: str, rng: np.random.Generator) -> str:
    """Apply one random single-character transcription error."""
    if len(text) < 2:
        return text
    op = rng.choice(["delete", "duplicate", "swap", "substitute"])
    pos = int(rng.integers(0, len(text)))
    chars = list(text)
    if op == "delete":
        del chars[pos]
    elif op == "duplicate":
        chars.insert(pos, chars[pos])
    elif op == "swap" and pos < len(chars) - 1:
        chars[pos], chars[pos + 1] = chars[pos + 1], chars[pos]
    elif op == "substitute":
        chars[pos] = str(rng.choice(DANISH_ALPHABET))[0]
    return "".join(chars)


def noisy_name(
    name: str,
    rng: np.random.Generator,
    variants: dict[str, list[str]] | None = None,
    p_variant: float = 0.20,
    p_char_edit: float = 0.10,
) -> str:
    """Return a noised copy of `name`: with some probability swap in a
    known historical spelling variant, and independently with some
    probability apply a random single-character transcription error.
    """
    result = name
    if variants and name in variants and rng.random() < p_variant:
        result = str(rng.choice(variants[name]))
    if rng.random() < p_char_edit:
        result = random_char_edit(result, rng)
    return result


def maybe_missing(value, rng: np.random.Generator, p_missing: float = 0.08):
    if rng.random() < p_missing:
        return None
    return value


def noisy_integer(
    value: int,
    rng: np.random.Generator,
    sigma: float = 1.2,
    p_blunder: float = 0.02,
    blunder_range: tuple[int, int] = (5, 20),
) -> int:
    """Add small measurement noise (rounding/age misreporting), with a
    rare chance of a large transcription blunder to keep the sanity-check
    logic non-trivial to exercise.
    """
    if rng.random() < p_blunder:
        direction = rng.choice([-1, 1])
        return int(value + direction * rng.integers(*blunder_range))
    return int(round(value + rng.normal(0, sigma)))
