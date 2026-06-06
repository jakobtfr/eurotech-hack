from __future__ import annotations

import argparse
from pathlib import Path

from src.cli import add_common_flags, run_cli
from src.common import load_json, relpath, repo_path, save_json, write_jsonl
from src.contracts import validate_predictions, validate_run, validate_split


def calibrate_run(run_path: str | Path) -> str:
    run_dir = repo_path(run_path)
    manifest = validate_run(run_dir, require_frozen=False)
    predictions_path = manifest["predictions_path"]
    predictions = validate_predictions(predictions_path)
    split_rows = (
        validate_split(manifest["dataset_split_path"]) if repo_path(manifest["dataset_split_path"]).exists() else []
    )
    split_by_tile = {row["tile_id"]: row for row in split_rows}
    config = load_json(manifest["config_path"])
    model_config = config.get("model_config", {})
    review_threshold = float(model_config.get("review_threshold", manifest["review_threshold"]))
    hold_threshold = float(model_config.get("hold_threshold", manifest["hold_threshold"]))
    area_hold_threshold = float(model_config.get("area_hold_threshold", 0.15))

    normal_validation_scores = [
        float(row["raw_anomaly_score"])
        for row in predictions
        if split_by_tile.get(row["tile_id"], {}).get("split") == "validation"
        and split_by_tile.get(row["tile_id"], {}).get("label") == "good"
    ]
    reference_scores = normal_validation_scores or [
        float(row["raw_anomaly_score"])
        for row in predictions
        if split_by_tile.get(row["tile_id"], {}).get("label") == "good"
    ]
    reference_scores = sorted(reference_scores or [float(row["raw_anomaly_score"]) for row in predictions] or [0.0])

    for row in predictions:
        normalized = _empirical_cdf(float(row["raw_anomaly_score"]), reference_scores)
        row["normalized_anomaly_score"] = round(normalized, 6)
        row["decision"], row["decision_reason"] = _decision(
            normalized, float(row["anomalous_area_fraction"]), review_threshold, hold_threshold, area_hold_threshold
        )
    write_jsonl(predictions_path, predictions)

    manifest["calibration_method"] = (
        "normal_validation_quantiles" if normal_validation_scores else "available_normal_scores_quantiles"
    )
    manifest["review_threshold"] = review_threshold
    manifest["hold_threshold"] = hold_threshold
    save_json(run_dir / "run_manifest.json", manifest)
    return relpath(predictions_path)


def _empirical_cdf(score: float, reference_scores: list[float]) -> float:
    # Midrank (Hazen) plotting position: a reference value maps to its own rank
    # midpoint rather than 1.0, so a normal validation tile does not self-trip the
    # hold threshold. Scores strictly above the whole reference set still map to 1.0.
    n = len(reference_scores)
    if n == 0:
        return 0.0
    less = sum(1 for reference in reference_scores if reference < score)
    equal = sum(1 for reference in reference_scores if reference == score)
    return (less + 0.5 * equal) / n


def _decision(
    score: float, area: float, review_threshold: float, hold_threshold: float, area_hold_threshold: float
) -> tuple[str, str]:
    if score >= hold_threshold:
        return "HOLD", "score_above_hold_threshold"
    if area >= area_hold_threshold:
        return "HOLD", "area_above_hold_threshold"
    if score >= review_threshold:
        return "REVIEW", "score_above_review_threshold"
    return "PASS", "score_below_review_threshold"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Normalize raw anomaly scores and assign review decisions.")
    parser.add_argument("--run", required=True, help="Run directory.")
    add_common_flags(parser)
    run_cli(parser, lambda args: calibrate_run(args.run), argv)


if __name__ == "__main__":
    main()
