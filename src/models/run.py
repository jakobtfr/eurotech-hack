from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

from src.cli import add_common_flags, run_cli
from src.common import (
    SCHEMA_VERSION,
    ContractError,
    environment_snapshot,
    git_commit,
    iso_now,
    load_yaml,
    relpath,
    repo_path,
    save_json,
    stable_unit_interval,
    write_csv,
    write_jsonl,
)
from src.contracts import SPLIT_FIELDS, validate_split
from src.models.adapters import get_adapter


def run_model(config_path: str | Path, split_path: str | Path, shots: int, seed: int) -> str:
    config = load_yaml(config_path)
    split_rows = validate_split(split_path)
    started_at = iso_now()
    model_name = config["model_name"]
    run_id = f"{started_at.replace(':', '').replace('-', '')}_{model_name}_k{shots}_seed{seed}"
    run_dir = repo_path("runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    support_candidates = [
        row
        for row in split_rows
        if row["split"] == "train" and row["label"] == "good" and _as_bool(row["support_eligible"])
    ]
    support_set = sorted(support_candidates, key=lambda row: stable_unit_interval(f"{seed}:{row['tile_id']}"))[:shots]
    if split_rows and len(support_set) < shots:
        raise ContractError(f"requested {shots} support tile(s), found {len(support_set)} train/good eligible tile(s)")
    write_csv(run_dir / "support_set.csv", support_set, SPLIT_FIELDS)

    # Empty smoke path: no tiles -> no model is loaded, no predictions emitted.
    fit_info = None
    patch_index: dict[str, Any] = {}
    if split_rows:
        adapter = get_adapter(config)
        fit_info = adapter.fit([_tile_ref(row) for row in support_set])
        patch_dir = run_dir / "patch_scores"
        patch_dir.mkdir(parents=True, exist_ok=True)
        all_scores: list[np.ndarray] = []
        scored_by_tile: dict[str, Any] = {}
        for row in split_rows:
            scored = adapter.score(_tile_ref(row))
            tile_slug = _safe_filename(row["tile_id"])
            npy_path = patch_dir / f"{tile_slug}.npy"
            np.save(npy_path, scored.patch_scores)
            scored_by_tile[row["tile_id"]] = scored
            all_scores.append(scored.patch_scores.ravel())
            patch_index[row["tile_id"]] = {
                "npy_path": relpath(npy_path),
                "patch_grid": list(scored.patch_scores.shape),
            }
        stacked = np.concatenate(all_scores) if all_scores else np.zeros(1, dtype=np.float32)
        save_json(
            patch_dir / "index.json",
            {
                "schema_version": SCHEMA_VERSION,
                "run_id": run_id,
                "score_min": round(float(stacked.min()), 6),
                "score_max": round(float(stacked.max()), 6),
                "tiles": patch_index,
            },
        )

    predictions = []
    for row in split_rows:
        scored = scored_by_tile[row["tile_id"]]
        tile_slug = _safe_filename(row["tile_id"])
        predictions.append(
            {
                "schema_version": SCHEMA_VERSION,
                "run_id": run_id,
                "tile_id": row["tile_id"],
                "raw_anomaly_score": round(float(scored.raw_anomaly_score), 6),
                "normalized_anomaly_score": None,
                "decision": "PASS",
                "decision_reason": "uncalibrated",
                "anomalous_area_fraction": round(float(scored.anomalous_area_fraction), 6),
                "region_count": int(scored.region_count),
                "heatmap_path": f"runs/{run_id}/heatmaps/{tile_slug}.png",
                "overlay_path": f"runs/{run_id}/overlays/{tile_slug}.png",
                "semantic_hint": None,
                "semantic_similarity": None,
                "novelty_status": "not_evaluated",
            }
        )
    write_jsonl(run_dir / "predictions.jsonl", predictions)

    save_json(
        run_dir / "config.resolved.json",
        {
            "schema_version": SCHEMA_VERSION,
            "config_path": relpath(config_path),
            "model_config": config,
            "split_path": relpath(split_path),
            "shots": shots,
            "seed": seed,
            "model_evidence": asdict(fit_info) if fit_info is not None else None,
            "patch_scores_index": relpath(run_dir / "patch_scores" / "index.json") if split_rows else None,
        },
    )
    (run_dir / "environment.txt").write_text(environment_snapshot(), encoding="utf-8")
    save_json(
        run_dir / "run_manifest.json",
        {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_id,
            "status": "open",
            "git_commit": git_commit(),
            "model_name": model_name,
            "model_source_commit": config.get("model_source_commit") or config.get("inspiration_commit"),
            "dataset_split_path": relpath(split_path),
            "config_path": relpath(run_dir / "config.resolved.json"),
            "support_set_path": relpath(run_dir / "support_set.csv"),
            "predictions_path": relpath(run_dir / "predictions.jsonl"),
            "calibration_method": "not_calibrated",
            "review_threshold": config.get("review_threshold", 0.99),
            "hold_threshold": config.get("hold_threshold", 0.999),
            "hardware": "recorded in environment.txt",
            "started_at": started_at,
            "completed_at": None,
        },
    )
    return relpath(run_dir)


def _tile_ref(row: dict[str, Any]) -> dict[str, Any]:
    """Resolve a split row into the geometry an adapter needs to load the tile."""

    return {
        "image_path": str(repo_path(row["image_path"])),
        "tile_x": row.get("tile_x", 0),
        "tile_y": row.get("tile_y", 0),
        "tile_size": row.get("tile_size", 0),
        "preprocess_id": row.get("preprocess_id"),
    }


def _safe_filename(value: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in value)


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Fit on a support set and score a split into a run artifact.")
    parser.add_argument("--config", required=True, help="Model YAML config.")
    parser.add_argument("--split", required=True, help="Split CSV path.")
    parser.add_argument("--shots", required=True, type=int, help="Normal support examples to record.")
    parser.add_argument("--seed", required=True, type=int, help="Support-set seed.")
    add_common_flags(parser)
    run_cli(parser, lambda args: run_model(args.config, args.split, args.shots, args.seed), argv)


if __name__ == "__main__":
    main()
