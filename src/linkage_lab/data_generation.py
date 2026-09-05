"""Synthetic-data generator.

Generates a hidden ground-truth population and two independently noised
"historical sources" (a census and a parish register) that overlap only
partially. This mimics, at toy scale, the structural problem in HisPeR's
own data: two heterogeneous transcribed sources describing overlapping but
not identical sets of individuals, each with source-specific transcription
noise.

All names, places and record values are fabricated for this project. No
real archival or personal data is used anywhere in this repository.
"""

from __future__ import annotations

import pandas as pd
import numpy as np

from . import config, reference_data as ref
from .noise_model import maybe_missing, noisy_integer, noisy_name

BIRTH_YEAR_RANGE = (1780, 1840)
CENSUS_YEAR = 1850

# Plausibility bounds used by life_course.py's sanity checks. Derived from
# the generation parameters above (age at census must be non-negative;
# a margin below the earliest birth year absorbs ordinary noise while still
# catching the rare large "blunder" errors injected by noise_model).
PLAUSIBLE_BIRTH_YEAR_MIN = BIRTH_YEAR_RANGE[0] - 10
PLAUSIBLE_BIRTH_YEAR_MAX = CENSUS_YEAR


def generate_population(n: int, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for i in range(n):
        gender = rng.choice(["M", "F"])
        given_name = rng.choice(
            ref.GIVEN_NAMES_MALE if gender == "M" else ref.GIVEN_NAMES_FEMALE
        )
        surname = rng.choice(ref.SURNAMES)
        birth_year = int(rng.integers(BIRTH_YEAR_RANGE[0], BIRTH_YEAR_RANGE[1] + 1))
        birth_place = rng.choice(ref.CANONICAL_PLACES)
        rows.append(
            {
                "person_id": f"P{i:05d}",
                "given_name": given_name,
                "surname": surname,
                "gender": gender,
                "birth_year": birth_year,
                "birth_place": birth_place,
            }
        )
    return pd.DataFrame(rows)


def generate_census(
    population: pd.DataFrame,
    rng: np.random.Generator,
    coverage: float,
    census_year: int = CENSUS_YEAR,
) -> pd.DataFrame:
    sample = population.sample(frac=coverage, random_state=int(rng.integers(0, 1_000_000)))
    rows = []
    for i, person in enumerate(sample.itertuples(index=False)):
        age = census_year - person.birth_year
        rows.append(
            {
                "census_record_id": f"C{i:05d}",
                "person_id": person.person_id,
                "given_name": noisy_name(person.given_name, rng),
                "surname": noisy_name(person.surname, rng, ref.SURNAME_VARIANTS),
                "age": noisy_integer(age, rng),
                "birth_place": maybe_missing(
                    noisy_name(person.birth_place, rng, ref.PLACE_VARIANTS), rng
                ),
                "residence_place": rng.choice(ref.CANONICAL_PLACES),
                "occupation": maybe_missing(rng.choice(ref.OCCUPATIONS), rng, p_missing=0.15),
                "census_year": census_year,
            }
        )
    return pd.DataFrame(rows)


def generate_parish_register(
    population: pd.DataFrame,
    rng: np.random.Generator,
    coverage: float,
) -> pd.DataFrame:
    sample = population.sample(frac=coverage, random_state=int(rng.integers(0, 1_000_000)))
    rows = []
    for i, person in enumerate(sample.itertuples(index=False)):
        rows.append(
            {
                "parish_record_id": f"R{i:05d}",
                "person_id": person.person_id,
                "given_name": noisy_name(person.given_name, rng),
                "surname": noisy_name(person.surname, rng, ref.SURNAME_VARIANTS),
                "birth_year": noisy_integer(person.birth_year, rng, sigma=1.0),
                "birth_place": maybe_missing(
                    noisy_name(person.birth_place, rng, ref.PLACE_VARIANTS), rng
                ),
                "parish": rng.choice(ref.CANONICAL_PLACES),
                "event_type": rng.choice(["daab", "foedsel"], p=[0.85, 0.15]),
            }
        )
    return pd.DataFrame(rows)


def generate_all(seed: int = config.RANDOM_SEED) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    population = generate_population(config.N_INDIVIDUALS, rng)
    census = generate_census(population, rng, config.CENSUS_COVERAGE)
    parish = generate_parish_register(population, rng, config.PARISH_COVERAGE)
    return {"population": population, "census": census, "parish_register": parish}


def save_all(seed: int = config.RANDOM_SEED) -> None:
    datasets = generate_all(seed)
    datasets["population"].to_csv(config.DATA_RAW_DIR / "ground_truth_population.csv", index=False)
    datasets["census"].to_csv(config.DATA_RAW_DIR / "census.csv", index=False)
    datasets["parish_register"].to_csv(config.DATA_RAW_DIR / "parish_register.csv", index=False)


if __name__ == "__main__":
    save_all()
