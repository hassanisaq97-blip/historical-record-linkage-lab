"""Shared paths and constants for the linkage_lab package."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_REPORTS_DIR = RESULTS_DIR / "reports"
RESULTS_FIGURES_DIR = RESULTS_DIR / "figures"

RANDOM_SEED = 42

# Population size for the synthetic ground-truth population.
N_INDIVIDUALS = 4000

# Probability that a given ground-truth individual appears in each source.
CENSUS_COVERAGE = 0.75
PARISH_COVERAGE = 0.75

# Entity-level train/test split (fraction of ground-truth individuals used for training).
TRAIN_FRACTION = 0.7

# Blocking: bucket width (years) used for the birth-year block key.
BLOCKING_YEAR_BUCKET = 5

# Life-course sanity checks. Absolute birth-year plausibility bounds are
# derived from the synthetic dataset's own generation parameters, see
# data_generation.PLAUSIBLE_BIRTH_YEAR_MIN / _MAX.
MAX_PLAUSIBLE_BIRTH_YEAR_SPREAD = 3

for _dir in (DATA_RAW_DIR, DATA_PROCESSED_DIR, RESULTS_REPORTS_DIR, RESULTS_FIGURES_DIR):
    _dir.mkdir(parents=True, exist_ok=True)
