from __future__ import annotations

from pathlib import Path
from typing import Any

from src.common import SCHEMA_VERSION, ContractError, load_json, read_csv, read_jsonl, relpath, repo_path, require_keys

MODALITIES = {"SEM", "PL", "etch", "optical", "wafer_map", "synthetic", "other"}
LICENSE_STATUSES = {"verified", "restricted", "unknown"}
SPLITS = {"train", "validation", "test"}
LABELS = {"good", "anomaly"}
DECISIONS = {"PASS", "REVIEW", "HOLD"}
NOVELTY_STATUSES = {"not_evaluated", "known_like", "unknown_like"}

REGISTRY_FIELDS = [
    "schema_version",
    "source_image_id",
    "dataset_id",
    "wafer_id",
    "source_path",
    "modality",
    "source_label",
    "mask_source_path",
    "license_status",
    "license_reference",
    "demo_allowed",
    "notes",
]

SPLIT_FIELDS = [
    "tile_id",
    "source_image_id",
    "dataset_id",
    "category",
    "wafer_id",
    "modality",
    "split",
    "label",
    "image_path",
    "mask_path",
    "tile_x",
    "tile_y",
    "tile_size",
    "stride",
    "preprocess_id",
    "support_eligible",
    "demo_allowed",
]

PREDICTION_FIELDS = [
    "schema_version",
    "run_id",
    "tile_id",
    "raw_anomaly_score",
    "normalized_anomaly_score",
    "decision",
    "decision_reason",
    "anomalous_area_fraction",
    "region_count",
    "heatmap_path",
    "overlay_path",
    "semantic_hint",
    "semantic_similarity",
    "novelty_status",
]

RUN_MANIFEST_FIELDS = [
    "schema_version",
    "run_id",
    "status",
    "git_commit",
    "model_name",
    "model_source_commit",
    "dataset_split_path",
    "config_path",
    "support_set_path",
    "predictions_path",
    "calibration_method",
    "review_threshold",
    "hold_threshold",
    "hardware",
    "started_at",
    "completed_at",
]


def _path_exists_when_set(value: Any, context: str) -> None:
    if value in (None, ""):
        return
    if not repo_path(value).exists():
        raise ContractError(f"{context}: referenced path does not exist: {value}")


def validate_registry(path: str | Path) -> list[dict[str, Any]]:
    rows = read_jsonl(path)
    seen_ids: set[str] = set()
    for row in rows:
        context = f"{relpath(path)}:{row.get('_line_number', '?')}"
        require_keys(row, REGISTRY_FIELDS, context)
        if row["schema_version"] != SCHEMA_VERSION:
            raise ContractError(f"{context}: unsupported schema_version {row['schema_version']!r}")
        source_id = str(row["source_image_id"])
        if not source_id:
            raise ContractError(f"{context}: source_image_id must be non-empty")
        if source_id in seen_ids:
            raise ContractError(f"{context}: duplicate source_image_id {source_id!r}")
        seen_ids.add(source_id)
        if row["modality"] not in MODALITIES:
            raise ContractError(f"{context}: invalid modality {row['modality']!r}")
        if row["license_status"] not in LICENSE_STATUSES:
            raise ContractError(f"{context}: invalid license_status {row['license_status']!r}")
        if bool(row["demo_allowed"]) and row["license_status"] != "verified":
            raise ContractError(f"{context}: demo_allowed=true requires license_status=verified")
        _path_exists_when_set(row["source_path"], context)
        _path_exists_when_set(row["mask_source_path"], context)
    return rows


def validate_split(path: str | Path) -> list[dict[str, str]]:
    rows = read_csv(path)
    with repo_path(path).open("r", encoding="utf-8", newline="") as handle:
        header = handle.readline().strip().split(",") if handle.tell() >= 0 else []
    if header != SPLIT_FIELDS:
        raise ContractError(f"{relpath(path)}: split header must be {', '.join(SPLIT_FIELDS)}")

    tile_ids: set[str] = set()
    source_groups: dict[str, str] = {}
    wafer_groups: dict[str, str] = {}
    for index, row in enumerate(rows, start=2):
        context = f"{relpath(path)}:{index}"
        require_keys(row, SPLIT_FIELDS, context)
        tile_id = row["tile_id"]
        if not tile_id:
            raise ContractError(f"{context}: tile_id must be non-empty")
        if tile_id in tile_ids:
            raise ContractError(f"{context}: duplicate tile_id {tile_id!r}")
        tile_ids.add(tile_id)
        if row["split"] not in SPLITS:
            raise ContractError(f"{context}: invalid split {row['split']!r}")
        if row["label"] not in LABELS:
            raise ContractError(f"{context}: invalid label {row['label']!r}")
        if row["modality"] not in MODALITIES:
            raise ContractError(f"{context}: invalid modality {row['modality']!r}")
        source_key = row["source_image_id"]
        previous_source_split = source_groups.setdefault(source_key, row["split"])
        if previous_source_split != row["split"]:
            raise ContractError(f"{context}: source_image_id {source_key!r} crosses splits")
        wafer_key = row["wafer_id"]
        if wafer_key:
            previous_wafer_split = wafer_groups.setdefault(wafer_key, row["split"])
            if previous_wafer_split != row["split"]:
                raise ContractError(f"{context}: wafer_id {wafer_key!r} crosses splits")
        if _as_bool(row["support_eligible"]) and (row["split"] != "train" or row["label"] != "good"):
            raise ContractError(f"{context}: support_eligible rows must be train/good")
        _path_exists_when_set(row["image_path"], context)
        _path_exists_when_set(row["mask_path"], context)
    return rows


def validate_predictions(path: str | Path, require_rendered_paths: bool = False) -> list[dict[str, Any]]:
    rows = read_jsonl(path)
    for row in rows:
        context = f"{relpath(path)}:{row.get('_line_number', '?')}"
        require_keys(row, PREDICTION_FIELDS, context)
        if row["schema_version"] != SCHEMA_VERSION:
            raise ContractError(f"{context}: unsupported schema_version {row['schema_version']!r}")
        if row["decision"] not in DECISIONS:
            raise ContractError(f"{context}: invalid decision {row['decision']!r}")
        if row["novelty_status"] not in NOVELTY_STATUSES:
            raise ContractError(f"{context}: invalid novelty_status {row['novelty_status']!r}")
        if require_rendered_paths:
            _path_exists_when_set(row["heatmap_path"], context)
            _path_exists_when_set(row["overlay_path"], context)
    return rows


def validate_run(run_path: str | Path, require_frozen: bool = True) -> dict[str, Any]:
    run_dir = repo_path(run_path)
    manifest_path = run_dir / "run_manifest.json"
    manifest = load_json(manifest_path)
    require_keys(manifest, RUN_MANIFEST_FIELDS, relpath(manifest_path))
    if manifest["schema_version"] != SCHEMA_VERSION:
        raise ContractError(f"{relpath(manifest_path)}: unsupported schema_version {manifest['schema_version']!r}")
    if require_frozen and manifest["status"] != "frozen":
        raise ContractError(f"{relpath(manifest_path)}: run status must be frozen")
    for key in ["config_path", "support_set_path", "predictions_path"]:
        _path_exists_when_set(manifest[key], relpath(manifest_path))
    if repo_path(manifest["dataset_split_path"]).exists():
        validate_split(manifest["dataset_split_path"])
    validate_predictions(manifest["predictions_path"], require_rendered_paths=manifest["status"] == "frozen")
    return manifest


def validate_demo(path: str | Path) -> dict[str, Any]:
    manifest = load_json(path)
    context = relpath(path)
    require_keys(manifest, ["schema_version", "demo_id", "status", "runs", "featured_examples"], context)
    if manifest["schema_version"] != SCHEMA_VERSION:
        raise ContractError(f"{context}: unsupported schema_version {manifest['schema_version']!r}")
    runs = manifest.get("runs") or []
    if not isinstance(runs, list):
        raise ContractError(f"{context}: runs must be a list")
    for run_entry in runs:
        if not isinstance(run_entry, dict) or "run_manifest_path" not in run_entry:
            raise ContractError(f"{context}: each run entry needs run_manifest_path")
        validate_run(Path(run_entry["run_manifest_path"]).parent, require_frozen=True)
    for example in manifest.get("featured_examples") or []:
        if not isinstance(example, dict):
            raise ContractError(f"{context}: featured_examples entries must be objects")
        if example.get("demo_allowed") is False:
            raise ContractError(
                f"{context}: featured example {example.get('tile_id', '<unknown>')} has demo_allowed=false"
            )
        for key in ["image_path", "heatmap_path", "overlay_path"]:
            _path_exists_when_set(example.get(key), context)
    return manifest


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}
