"""Utilities for project response-time drift detection.

Author: Brian Cookson
Date: 2026-11

Compare synthetic historical and current project request data
to identify changes in response times and overdue rates.
"""

from pathlib import Path

import polars as pl


def load_project_data(data_file: Path) -> pl.DataFrame:
    """Load and validate project request response data."""
    df = pl.read_csv(data_file)

    required_columns = {"request_id", "project_phase", "response_days"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    if df.height == 0:
        raise ValueError("Project dataset cannot be empty.")

    if df["response_days"].null_count() > 0:
        raise ValueError("Response days cannot contain missing values.")

    if (df["response_days"] < 0).any():
        raise ValueError("Response days cannot be negative.")

    return df


def compute_project_drift(
    reference_df: pl.DataFrame,
    current_df: pl.DataFrame,
    response_threshold_days: float = 2.0,
    overdue_threshold_days: int = 7,
    overdue_rate_threshold_pct: float = 20.0,
) -> pl.DataFrame:
    """Compare project response times between two periods.

    Drift is flagged when the absolute change in average
    response days or overdue percentage exceeds its threshold.
    """
    if response_threshold_days < 0 or overdue_rate_threshold_pct < 0:
        raise ValueError("Drift thresholds cannot be negative.")

    if overdue_threshold_days < 0:
        raise ValueError("Overdue threshold cannot be negative.")

    reference_avg = float(reference_df["response_days"].mean())
    current_avg = float(current_df["response_days"].mean())

    reference_overdue_pct = (
        reference_df.filter(pl.col("response_days") > overdue_threshold_days).height
        / reference_df.height
        * 100
    )
    current_overdue_pct = (
        current_df.filter(pl.col("response_days") > overdue_threshold_days).height
        / current_df.height
        * 100
    )

    response_difference = current_avg - reference_avg
    overdue_difference = current_overdue_pct - reference_overdue_pct

    return pl.DataFrame(
        {
            "reference_count": [reference_df.height],
            "current_count": [current_df.height],
            "reference_avg_response_days": [round(reference_avg, 2)],
            "current_avg_response_days": [round(current_avg, 2)],
            "response_mean_difference_days": [round(response_difference, 2)],
            "response_drift_threshold_days": [response_threshold_days],
            "response_is_drifting": [
                abs(response_difference) > response_threshold_days
            ],
            "reference_overdue_rate_pct": [round(reference_overdue_pct, 2)],
            "current_overdue_rate_pct": [round(current_overdue_pct, 2)],
            "overdue_rate_difference_pct_points": [round(overdue_difference, 2)],
            "overdue_drift_threshold_pct_points": [overdue_rate_threshold_pct],
            "overdue_rate_is_drifting": [
                abs(overdue_difference) > overdue_rate_threshold_pct
            ],
        }
    )
