from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from src.cli import add_common_flags, run_cli
from src.common import SCHEMA_VERSION, load_json, relpath, repo_path, save_json
from src.contracts import validate_predictions, validate_run, validate_split
from src.models.adapters.dinov2_pca import load_tile_rgb

_DISPLAY_SIZE = 448
# Colormap control points (low -> high): cool blue, warm yellow, hot red.
_CMAP_STOPS = np.array([0.0, 0.5, 1.0])
_CMAP_COLORS = np.array([[30, 40, 120], [240, 200, 40], [200, 30, 30]], dtype=np.float32)


def render_run(run_path: str | Path) -> str:
    run_dir = repo_path(run_path)
    manifest = validate_run(run_dir, require_frozen=False)
    predictions = validate_predictions(manifest["predictions_path"])
    split_by_tile = _split_by_tile(manifest)
    index = _load_patch_index(run_dir)
    score_min = float(index.get("score_min", 0.0)) if index else 0.0
    score_max = float(index.get("score_max", 1.0)) if index else 1.0

    for row in predictions:
        norm = _patch_norm(row, index, score_min, score_max)
        _write_heatmap(repo_path(row["heatmap_path"]), norm)
        base = _overlay_base(split_by_tile.get(row["tile_id"]))
        _write_overlay(repo_path(row["overlay_path"]), norm, base)

    risk_map_path = run_dir / "risk_maps" / "risk_map.json"
    save_json(risk_map_path, _risk_map(manifest["run_id"], predictions, split_by_tile))
    return relpath(risk_map_path)


# --------------------------------------------------------------------------- #
# Patch-score loading
# --------------------------------------------------------------------------- #
def _load_patch_index(run_dir: Path) -> dict[str, Any]:
    index_path = run_dir / "patch_scores" / "index.json"
    if not index_path.exists():
        return {}
    return load_json(index_path)


def _patch_norm(row: dict[str, Any], index: dict[str, Any], score_min: float, score_max: float) -> np.ndarray:
    """Return a ``(_DISPLAY_SIZE, _DISPLAY_SIZE)`` heat field in [0, 1]."""

    entry = (index.get("tiles") or {}).get(row["tile_id"]) if index else None
    if entry is not None and repo_path(entry["npy_path"]).exists():
        patch_scores = np.load(repo_path(entry["npy_path"])).astype(np.float32)
        span = score_max - score_min
        normalized = (patch_scores - score_min) / span if span > 0 else np.zeros_like(patch_scores)
        return _upsample(np.clip(normalized, 0.0, 1.0))
    # Fallback: flat field from the calibrated image score (no patch map on disk).
    flat = float(row.get("normalized_anomaly_score") or 0.0)
    return np.full((_DISPLAY_SIZE, _DISPLAY_SIZE), np.clip(flat, 0.0, 1.0), dtype=np.float32)


def _upsample(field: np.ndarray) -> np.ndarray:
    image = Image.fromarray((field * 255.0).astype(np.uint8), mode="L")
    resized = image.resize((_DISPLAY_SIZE, _DISPLAY_SIZE), Image.Resampling.BILINEAR)
    return np.asarray(resized, dtype=np.float32) / 255.0


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
def _colormap(field: np.ndarray) -> np.ndarray:
    flat = field.ravel()
    channels = [np.interp(flat, _CMAP_STOPS, _CMAP_COLORS[:, channel]) for channel in range(3)]
    rgb = np.stack(channels, axis=1).reshape(*field.shape, 3)
    return rgb.astype(np.uint8)


def _write_heatmap(path: Path, norm: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(_colormap(norm), mode="RGB").save(path, format="PNG")


def _overlay_base(split_row: dict[str, Any] | None) -> np.ndarray:
    if split_row and split_row.get("image_path"):
        try:
            ref = {
                "image_path": str(repo_path(split_row["image_path"])),
                "tile_x": split_row.get("tile_x", 0),
                "tile_y": split_row.get("tile_y", 0),
                "tile_size": split_row.get("tile_size", 0),
                "preprocess_id": split_row.get("preprocess_id"),
            }
            return load_tile_rgb(ref, _DISPLAY_SIZE)
        except Exception:  # noqa: BLE001 - rendering must not fail on an unreadable tile
            pass
    return np.full((_DISPLAY_SIZE, _DISPLAY_SIZE, 3), 64, dtype=np.uint8)


def _write_overlay(path: Path, norm: np.ndarray, base: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    heat = _colormap(norm).astype(np.float32)
    alpha = (norm * 0.6)[..., None]
    blended = base.astype(np.float32) * (1.0 - alpha) + heat * alpha
    Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8), mode="RGB").save(path, format="PNG")


# --------------------------------------------------------------------------- #
# Risk map
# --------------------------------------------------------------------------- #
def _split_by_tile(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    split_path = manifest["dataset_split_path"]
    if not repo_path(split_path).exists():
        return {}
    return {row["tile_id"]: row for row in validate_split(split_path)}


def _risk_map(
    run_id: str, predictions: list[dict[str, Any]], split_by_tile: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    tiles = []
    summary = {"PASS": 0, "REVIEW": 0, "HOLD": 0}
    for row in predictions:
        split_row = split_by_tile.get(row["tile_id"], {})
        decision = str(row["decision"])
        summary[decision] = summary.get(decision, 0) + 1
        tiles.append(
            {
                "tile_id": row["tile_id"],
                "source_image_id": split_row.get("source_image_id", ""),
                "tile_x": int(split_row.get("tile_x", 0) or 0),
                "tile_y": int(split_row.get("tile_y", 0) or 0),
                "normalized_anomaly_score": float(row.get("normalized_anomaly_score") or 0.0),
                "decision": decision,
            }
        )
    sources = {split_by_tile.get(row["tile_id"], {}).get("source_image_id") for row in predictions}
    sources.discard(None)
    provenance = "real spatial" if len(sources) <= 1 else "stitched field"
    scores = [float(row.get("normalized_anomaly_score") or 0.0) for row in predictions]
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "provenance": provenance,
        "tile_count": len(predictions),
        "risk_score": max(scores or [0.0]),
        "review_or_hold_count": summary["REVIEW"] + summary["HOLD"],
        "summary": summary,
        "tiles": tiles,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Render heatmap, overlay, and risk-map artifacts from a run.")
    parser.add_argument("--run", required=True, help="Run directory.")
    add_common_flags(parser)
    run_cli(parser, lambda args: render_run(args.run), argv)


if __name__ == "__main__":
    main()
