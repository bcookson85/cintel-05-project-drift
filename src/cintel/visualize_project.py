"""Visualize project response-time drift detection results.

Author: Brian Cookson
Date: 2026-11

Compare historical and current project response performance
using a two-panel chart of response times and overdue rates.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import polars as pl

ROOT_DIR = Path.cwd()
INPUT_FILE = ROOT_DIR / "artifacts" / "project_drift_summary.csv"
OUTPUT_DIR = ROOT_DIR / "docs" / "images"
OUTPUT_FILE = OUTPUT_DIR / "project_drift_chart.png"


def main() -> None:
    """Generate a chart comparing historical and current performance."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pl.read_csv(INPUT_FILE)
    results = df.to_dicts()[0]

    periods = ["Historical Baseline", "Current Period"]

    response_values = [
        results["reference_avg_response_days"],
        results["current_avg_response_days"],
    ]

    overdue_values = [
        results["reference_overdue_rate_pct"],
        results["current_overdue_rate_pct"],
    ]

    response_limit = (
        results["reference_avg_response_days"]
        + results["response_drift_threshold_days"]
    )

    overdue_limit = (
        results["reference_overdue_rate_pct"]
        + results["overdue_drift_threshold_pct_points"]
    )

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    colors = ["steelblue", "darkorange"]

    axes[0].bar(periods, response_values, color=colors)
    axes[0].axhline(
        response_limit,
        color="red",
        linestyle="--",
        label="Baseline + drift threshold",
    )
    axes[0].set_title("Average Project Response Time")
    axes[0].set_ylabel("Average response time (days)")
    axes[0].set_ylim(0, max(response_values) * 1.3)
    axes[0].legend()

    for index, value in enumerate(response_values):
        axes[0].text(
            index,
            value + 0.15,
            f"{value:.2f} days",
            ha="center",
            fontweight="bold",
        )

    axes[1].bar(periods, overdue_values, color=colors)
    axes[1].axhline(
        overdue_limit,
        color="red",
        linestyle="--",
        label="Baseline + drift threshold",
    )
    axes[1].set_title("Overdue Project Requests")
    axes[1].set_ylabel("Requests overdue (%)")
    axes[1].set_ylim(0, 100)
    axes[1].legend()

    for index, value in enumerate(overdue_values):
        axes[1].text(
            index,
            value + 2,
            f"{value:.2f}%",
            ha="center",
            fontweight="bold",
        )

    fig.suptitle(
        "Project Response-Time Drift Detection",
        fontsize=16,
        fontweight="bold",
    )

    fig.text(
        0.5,
        0.01,
        "Synthetic project data | Overdue = response time > 7 days",
        ha="center",
        fontsize=10,
    )

    fig.tight_layout(rect=(0, 0.04, 1, 0.95))

    fig.savefig(OUTPUT_FILE, dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"Chart saved successfully: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
