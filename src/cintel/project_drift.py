"""Custom project response-time drift detection application.

Author: Brian Cookson
Date: 2026-11

Compare synthetic historical and current project request
data to detect changes in response times and overdue rates.
"""

import logging
from pathlib import Path
from typing import Final

from datafun_toolkit.logger import get_logger, log_header, log_path
import polars as pl

from cintel.utils_project import compute_project_drift, load_project_data

LOG: logging.Logger = get_logger("P5-PROJECT", level="DEBUG")

ROOT_DIR: Final[Path] = Path.cwd()
DATA_DIR: Final[Path] = ROOT_DIR / "data"
ARTIFACTS_DIR: Final[Path] = ROOT_DIR / "artifacts"

REFERENCE_FILE: Final[Path] = DATA_DIR / "project_reference_responses.csv"
CURRENT_FILE: Final[Path] = DATA_DIR / "project_current_responses.csv"
OUTPUT_FILE: Final[Path] = ARTIFACTS_DIR / "project_drift_summary.csv"

RESPONSE_DRIFT_THRESHOLD: Final[float] = 2.0
OVERDUE_THRESHOLD_DAYS: Final[int] = 7
OVERDUE_RATE_DRIFT_THRESHOLD: Final[float] = 20.0


def main() -> None:
    """Run the custom project response-time drift detection pipeline."""
    log_header(LOG, "PROJECT RESPONSE-TIME DRIFT DETECTION")

    log_path(LOG, "REFERENCE_FILE", REFERENCE_FILE)
    log_path(LOG, "CURRENT_FILE", CURRENT_FILE)
    log_path(LOG, "OUTPUT_FILE", OUTPUT_FILE)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    reference_df: pl.DataFrame = load_project_data(REFERENCE_FILE)
    current_df: pl.DataFrame = load_project_data(CURRENT_FILE)

    LOG.info(f"Loaded {reference_df.height} reference records")
    LOG.info(f"Loaded {current_df.height} current records")

    LOG.info(f"Response drift threshold: {RESPONSE_DRIFT_THRESHOLD} days")
    LOG.info(f"Overdue threshold: {OVERDUE_THRESHOLD_DAYS} days")
    LOG.info(
        f"Overdue-rate drift threshold: "
        f"{OVERDUE_RATE_DRIFT_THRESHOLD} percentage points"
    )

    drift_df: pl.DataFrame = compute_project_drift(
        reference_df,
        current_df,
        response_threshold_days=RESPONSE_DRIFT_THRESHOLD,
        overdue_threshold_days=OVERDUE_THRESHOLD_DAYS,
        overdue_rate_threshold_pct=OVERDUE_RATE_DRIFT_THRESHOLD,
    )

    drift_df.write_csv(OUTPUT_FILE)

    LOG.info("Custom drift comparison results:")
    for field_name, field_value in drift_df.to_dicts()[0].items():
        LOG.info(f"{field_name}: {field_value}")

    LOG.info(f"Saved project drift results: {OUTPUT_FILE}")
    LOG.info("Pipeline executed successfully!")


if __name__ == "__main__":
    main()
