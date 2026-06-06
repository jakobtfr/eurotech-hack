from __future__ import annotations

import argparse
from pathlib import Path

from src.cli import add_common_flags, run_cli
from src.common import SCHEMA_VERSION, relpath, repo_path, save_json
from src.contracts import validate_predictions, validate_run, validate_split


def evaluate_run(run_path: str | Path) -> str:
    run_dir = repo_path(run_path)
    manifest = validate_run(run_dir, require_frozen=False)
    predictions = validate_predictions(manifest["predictions_path"])
    split_rows = (
        validate_split(manifest["dataset_split_path"]) if repo_path(manifest["dataset_split_path"]).exists() else []
    )
    split_by_tile = {row["tile_id"]: row for row in split_rows}
    labeled = [
        (
            float(row["normalized_anomaly_score"] or 0.0),
            1 if split_by_tile.get(row["tile_id"], {}).get("label") == "anomaly" else 0,
        )
        for row in predictions
        if split_by_tile.get(row["tile_id"], {}).get("split") == "test"
    ]
    positives = sum(label for _, label in labeled)
    negatives = len(labeled) - positives
    has_image_labels = positives > 0 and negatives > 0
    metrics = {
        "schema_version": SCHEMA_VERSION,
        "run_id": manifest["run_id"],
        "tile_count": len(predictions),
        "test_tile_count": len(labeled),
        "image_auroc": _auroc(labeled) if has_image_labels else None,
        "image_aupr": _aupr(labeled) if has_image_labels else None,
        "decision_counts": _decision_counts(predictions),
    }
    metrics_manifest = {
        "schema_version": SCHEMA_VERSION,
        "image_auroc": {
            "valid": has_image_labels,
            "reason": "test image labels available"
            if has_image_labels
            else "test split needs both good and anomaly labels",
        },
        "image_aupr": {
            "valid": has_image_labels,
            "reason": "test image labels available"
            if has_image_labels
            else "test split needs both good and anomaly labels",
        },
        "pixel_auroc": {"valid": False, "reason": "aligned masks unavailable"},
        "pro": {"valid": False, "reason": "aligned masks unavailable"},
    }
    failure_cases = {
        "schema_version": SCHEMA_VERSION,
        "run_id": manifest["run_id"],
        "false_positives": [],
        "false_negatives": [],
        "notes": "Failure cases require labeled test data and a calibrated threshold.",
    }
    save_json(run_dir / "metrics.json", metrics)
    save_json(run_dir / "metrics_manifest.json", metrics_manifest)
    save_json(run_dir / "failure_cases.json", failure_cases)
    return relpath(run_dir / "metrics.json")


def _decision_counts(rows: list[dict[str, object]]) -> dict[str, int]:
    counts = {"PASS": 0, "REVIEW": 0, "HOLD": 0}
    for row in rows:
        counts[str(row["decision"])] = counts.get(str(row["decision"]), 0) + 1
    return counts


def _auroc(rows: list[tuple[float, int]]) -> float:
    positives = [score for score, label in rows if label == 1]
    negatives = [score for score, label in rows if label == 0]
    wins = 0.0
    for positive in positives:
        for negative in negatives:
            if positive > negative:
                wins += 1.0
            elif positive == negative:
                wins += 0.5
    return round(wins / (len(positives) * len(negatives)), 6)


def _aupr(rows: list[tuple[float, int]]) -> float:
    ordered = sorted(rows, key=lambda row: row[0], reverse=True)
    positives = sum(label for _, label in rows)
    if positives == 0:
        return 0.0
    precision_recall_points = []
    true_positives = 0
    false_positives = 0
    for _, label in ordered:
        if label == 1:
            true_positives += 1
        else:
            false_positives += 1
        precision = true_positives / (true_positives + false_positives)
        recall = true_positives / positives
        precision_recall_points.append((recall, precision))
    area = 0.0
    previous_recall = 0.0
    for recall, precision in precision_recall_points:
        area += (recall - previous_recall) * precision
        previous_recall = recall
    return round(area, 6)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Compute metrics that are valid for the available evidence.")
    parser.add_argument("--run", required=True, help="Run directory.")
    add_common_flags(parser)
    run_cli(parser, lambda args: evaluate_run(args.run), argv)


if __name__ == "__main__":
    main()
