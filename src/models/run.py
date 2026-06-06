from __future__ import annotations

import argparse
from pathlib import Path

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

    predictions = []
    for row in split_rows:
        score = round(stable_unit_interval(f"{seed}:{row['tile_id']}:{model_name}") * 100.0, 6)
        area = round(stable_unit_interval(f"{row['tile_id']}:area") * 0.2, 6)
        tile_slug = _safe_filename(row["tile_id"])
        predictions.append(
            {
                "schema_version": SCHEMA_VERSION,
                "run_id": run_id,
                "tile_id": row["tile_id"],
                "raw_anomaly_score": score,
                "normalized_anomaly_score": None,
                "decision": "PASS",
                "decision_reason": "uncalibrated_placeholder",
                "anomalous_area_fraction": area,
                "region_count": int(area > 0.05),
                "heatmap_path": f"runs/{run_id}/heatmaps/{tile_slug}.svg",
                "overlay_path": f"runs/{run_id}/overlays/{tile_slug}.svg",
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
            "scaffold_warning": "Deterministic placeholder scores; not model evidence.",
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
            "model_source_commit": config.get("upstream_commit"),
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


def _safe_filename(value: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in value)


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Create a run artifact directory from a split manifest.")
    parser.add_argument("--config", required=True, help="Model YAML config.")
    parser.add_argument("--split", required=True, help="Split CSV path.")
    parser.add_argument("--shots", required=True, type=int, help="Normal support examples to record.")
    parser.add_argument("--seed", required=True, type=int, help="Support-set seed.")
    add_common_flags(parser)
    run_cli(parser, lambda args: run_model(args.config, args.split, args.shots, args.seed), argv)


if __name__ == "__main__":
    main()
