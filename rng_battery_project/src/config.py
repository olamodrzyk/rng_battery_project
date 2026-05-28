"""Project-wide configuration for the RNG statistical test battery."""

from pathlib import Path

ALPHA = 0.01
SEQUENCE_LENGTH = 200_000
BASE_SEED = 20260527

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
TABLES_DIR = RESULTS_DIR / "tables"
REPORTS_DIR = RESULTS_DIR / "reports"

for directory in (DATA_RAW_DIR, DATA_PROCESSED_DIR, FIGURES_DIR, TABLES_DIR, REPORTS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

