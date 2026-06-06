from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

from src.common import repo_path
from src.contracts import validate_predictions, validate_run
from src.data.build import build_split
from src.evaluation.calibrate import calibrate_run
from src.evaluation.evaluate import evaluate_run
from src.models.run import run_model
from src.packaging.freeze import freeze_run
from src.rendering.render import render_run

_MODEL_CONFIG = "configs/models/pixel_pca.yaml"


def _normal(rng: np.random.Generator, size: int = 224) -> np.ndarray:
    base = np.tile(np.linspace(40, 200, size, dtype=np.float32), (size, 1))
    noisy = np.clip(base + rng.normal(0, 5, (size, size)), 0, 255).astype(np.uint8)
    return np.stack([noisy] * 3, axis=2)


def _save(path: Path, array: np.ndarray) -> None:
    Image.fromarray(array, mode="RGB").save(path)


def _registry_line(source_id: str, source_path: Path, label: str) -> str:
    return json.dumps(
        {
            "schema_version": "1.0",
            "source_image_id": source_id,
            "dataset_id": "e2e",
            "wafer_id": None,
            "source_path": str(source_path),
            "modality": "SEM",
            "source_label": label,
            "mask_source_path": None,
            "license_status": "verified",
            "license_reference": "",
            "demo_allowed": True,
            "notes": "",
        }
    )


def _data_config(tmp_path: Path, registry: Path, split: Path) -> Path:
    config = tmp_path / "data.yaml"
    config.write_text(
        "\n".join(
            [
                'schema_version: "1.0"',
                "dataset_id: e2e",
                f"registry_path: {registry}",
                f"split_path: {split}",
                f"workbench_root: {tmp_path / 'workbench'}",
                "category: demo",
                "tile_size: 224",
                "stride: 224",
                "preprocess_id: rgb_repeat_v1",
                "allow_empty: false",
                "allow_placeholder_tiles: false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return config


def test_pipeline_end_to_end_real_model(tmp_path: Path) -> None:
    rng = np.random.default_rng(7)
    raw = tmp_path / "raw"
    raw.mkdir()
    lines = []
    for index in range(3):
        path = raw / f"normal_{index}.png"
        _save(path, _normal(rng))
        lines.append(_registry_line(f"normal_{index}", path, "normal"))
    defect = _normal(rng)
    defect[80:150, 80:150] = 250
    defect_path = raw / "defect.png"
    _save(defect_path, defect)
    lines.append(_registry_line("defect", defect_path, "anomaly"))

    registry = tmp_path / "sources.jsonl"
    registry.write_text("\n".join(lines) + "\n", encoding="utf-8")
    split = tmp_path / "split.csv"
    build_split(_data_config(tmp_path, registry, split))

    run_dir: Path | None = None
    try:
        run_rel = run_model(_MODEL_CONFIG, split, shots=2, seed=17)
        run_dir = repo_path(run_rel)
        calibrate_run(run_dir)
        evaluate_run(run_dir)
        render_run(run_dir)
        freeze_run(run_dir)

        manifest = validate_run(run_dir, require_frozen=True)
        predictions = validate_predictions(manifest["predictions_path"], require_rendered_paths=True)
        by_tile = {row["tile_id"]: row for row in predictions}
        defect_row = next(row for tile_id, row in by_tile.items() if tile_id.startswith("defect"))
        normal_rows = [row for tile_id, row in by_tile.items() if not tile_id.startswith("defect")]

        # The real model ranks the injected-defect tile above every normal tile.
        assert defect_row["raw_anomaly_score"] == max(row["raw_anomaly_score"] for row in predictions)
        assert defect_row["raw_anomaly_score"] > max(row["raw_anomaly_score"] for row in normal_rows)
        assert defect_row["normalized_anomaly_score"] is not None

        # Rendered artifacts are real PNGs at the contract paths.
        for row in predictions:
            for key in ("heatmap_path", "overlay_path"):
                with Image.open(repo_path(row[key])) as image:
                    assert image.format == "PNG"
                    assert image.size == (448, 448)
    finally:
        if run_dir is not None and run_dir.exists():
            shutil.rmtree(run_dir)
