from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from src.cli import add_common_flags, run_cli
from src.common import SCHEMA_VERSION, load_json, relpath, repo_path, save_json
from src.contracts import validate_predictions, validate_run, validate_split

_PIXEL_EVAL_SIZE = 256


def evaluate_run(run_path: str | Path) -> str:
    run_dir = repo_path(run_path)
    manifest = validate_run(run_dir, require_frozen=False)
    predictions = validate_predictions(manifest["predictions_path"])
    split_rows = (
        validate_split(manifest["dataset_split_path"]) if repo_path(manifest["dataset_split_path"]).exists() else []
    )
    split_by_tile = {row["tile_id"]: row for row in split_rows}
    # Image-level scoring aggregates tiles to their source image (max over tiles),
    # then labels per source. Scoring per tile would mislabel the normal-looking
    # tiles of a localized-defect image as anomalies (tiling bias).
    labeled = _source_level_scores(predictions, split_by_tile)
    positives = sum(label for _, label in labeled)
    negatives = len(labeled) - positives
    has_image_labels = positives > 0 and negatives > 0
    pixel_auroc, pixel_reason = _pixel_auroc(run_dir, predictions, split_by_tile)
    test_tiles = sum(1 for row in predictions if split_by_tile.get(row["tile_id"], {}).get("split") == "test")
    metrics = {
        "schema_version": SCHEMA_VERSION,
        "run_id": manifest["run_id"],
        "tile_count": len(predictions),
        "test_tile_count": test_tiles,
        "test_image_count": len(labeled),
        "image_auroc": _auroc(labeled) if has_image_labels else None,
        "image_aupr": _aupr(labeled) if has_image_labels else None,
        "pixel_auroc": pixel_auroc,
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
        "pixel_auroc": {"valid": pixel_auroc is not None, "reason": pixel_reason},
        "pro": {"valid": False, "reason": "PRO requires region-level mask evaluation (not implemented)"},
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


def _source_level_scores(
    predictions: list[dict[str, Any]], split_by_tile: dict[str, dict[str, Any]]
) -> list[tuple[float, int]]:
    """Aggregate test tiles to one (score, label) per source image (max over tiles)."""

    by_source: dict[str, tuple[float, int]] = {}
    for row in predictions:
        split_row = split_by_tile.get(row["tile_id"])
        if not split_row or split_row.get("split") != "test":
            continue
        source_id = split_row["source_image_id"]
        score = float(row["normalized_anomaly_score"] or 0.0)
        label = 1 if split_row.get("label") == "anomaly" else 0
        current = by_source.get(source_id)
        if current is None or score > current[0]:
            by_source[source_id] = (score, label)
    return list(by_source.values())


def _pixel_auroc(
    run_dir: Path, predictions: list[dict[str, Any]], split_by_tile: dict[str, dict[str, Any]]
) -> tuple[float | None, str]:
    """Pixel AUROC of the patch heatmaps against aligned ground-truth masks."""

    index_path = run_dir / "patch_scores" / "index.json"
    if not index_path.exists():
        return None, "patch score maps unavailable"
    tiles = load_json(index_path).get("tiles", {})
    score_chunks: list[np.ndarray] = []
    label_chunks: list[np.ndarray] = []
    saw_mask = False
    for row in predictions:
        split_row = split_by_tile.get(row["tile_id"])
        if not split_row or split_row.get("split") != "test":
            continue
        entry = tiles.get(row["tile_id"])
        if not entry or not repo_path(entry["npy_path"]).exists():
            continue
        score_map = _resize_float(np.load(repo_path(entry["npy_path"])).astype(np.float32), _PIXEL_EVAL_SIZE)
        mask_path = split_row.get("mask_path")
        if mask_path and repo_path(mask_path).exists():
            saw_mask = True
            mask = _load_mask(mask_path, split_row, _PIXEL_EVAL_SIZE)
        else:
            mask = np.zeros((_PIXEL_EVAL_SIZE, _PIXEL_EVAL_SIZE), dtype=np.uint8)
        score_chunks.append(score_map.ravel())
        label_chunks.append((mask > 0).astype(np.uint8).ravel())
    if not saw_mask:
        return None, "aligned masks unavailable"
    scores = np.concatenate(score_chunks)
    labels = np.concatenate(label_chunks)
    positives = int(labels.sum())
    if positives == 0 or positives == labels.size:
        return None, "test pixels need both anomalous and normal regions"
    return round(_auroc_fast(scores, labels), 6), "aligned masks available"


def _resize_float(array: np.ndarray, size: int) -> np.ndarray:
    return np.asarray(
        Image.fromarray(array, mode="F").resize((size, size), Image.Resampling.BILINEAR), dtype=np.float32
    )


def _load_mask(mask_path: str, split_row: dict[str, Any], size: int) -> np.ndarray:
    tile_size = int(split_row.get("tile_size") or 0)
    with Image.open(repo_path(mask_path)) as mask_image:
        mask_image = mask_image.convert("L")
        if tile_size > 0:
            width, height = mask_image.size
            x = max(0, min(int(split_row.get("tile_x") or 0), max(0, width - tile_size)))
            y = max(0, min(int(split_row.get("tile_y") or 0), max(0, height - tile_size)))
            mask_image = mask_image.crop((x, y, x + tile_size, y + tile_size))
        mask_image = mask_image.resize((size, size), Image.Resampling.NEAREST)
        return np.asarray(mask_image, dtype=np.uint8)


def _auroc_fast(scores: np.ndarray, labels: np.ndarray) -> float:
    """Mann-Whitney AUROC with tie-averaged ranks (O(n log n)), for pixel-scale inputs."""

    order = np.argsort(scores, kind="mergesort")
    sorted_scores = scores[order]
    _, starts, counts = np.unique(sorted_scores, return_index=True, return_counts=True)
    average_ranks = starts + (counts - 1) / 2.0 + 1.0
    sorted_ranks = np.repeat(average_ranks, counts)
    ranks = np.empty(scores.size, dtype=np.float64)
    ranks[order] = sorted_ranks
    positive_mask = labels == 1
    n_positive = int(positive_mask.sum())
    n_negative = labels.size - n_positive
    return float((ranks[positive_mask].sum() - n_positive * (n_positive + 1) / 2.0) / (n_positive * n_negative))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Compute metrics that are valid for the available evidence.")
    parser.add_argument("--run", required=True, help="Run directory.")
    add_common_flags(parser)
    run_cli(parser, lambda args: evaluate_run(args.run), argv)


if __name__ == "__main__":
    main()
