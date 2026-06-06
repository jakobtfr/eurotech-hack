from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

from src.common import load_json, repo_path
from src.data.build import build_split
from src.evaluation.calibrate import calibrate_run
from src.evaluation.evaluate import evaluate_run
from src.models.run import run_model

_MODEL_CONFIG = "configs/models/pixel_pca.yaml"


def _normal(rng: np.random.Generator, size: int = 448) -> np.ndarray:
    base = np.tile(np.linspace(40, 200, size, dtype=np.float32), (size, 1))
    return np.clip(base + rng.normal(0, 6, (size, size)), 0, 255).astype(np.uint8)


def _save_gray(path: Path, array: np.ndarray) -> None:
    Image.fromarray(np.stack([array] * 3, axis=2), mode="RGB").save(path)


def _registry_line(source_id: str, source_path: Path, label: str, mask_path: Path | None) -> str:
    return json.dumps(
        {
            "schema_version": "1.0",
            "source_image_id": source_id,
            "dataset_id": "pix",
            "wafer_id": None,
            "source_path": str(source_path),
            "modality": "SEM",
            "source_label": label,
            "mask_source_path": str(mask_path) if mask_path else None,
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
                "dataset_id: pix",
                f"registry_path: {registry}",
                f"split_path: {split}",
                f"workbench_root: {tmp_path / 'workbench'}",
                "category: demo",
                "tile_size: 448",
                "stride: 448",
                "preprocess_id: rgb_repeat_v1",
                "allow_empty: false",
                "allow_placeholder_tiles: false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return config


def test_pixel_auroc_from_masks(tmp_path: Path) -> None:
    rng = np.random.default_rng(11)
    lines = []
    for index in range(6):
        path = tmp_path / f"normal_{index}.png"
        _save_gray(path, _normal(rng))
        lines.append(_registry_line(f"normal_{index}", path, "normal", None))
    for index in range(2):
        img = _normal(rng)
        mask = np.zeros((448, 448), dtype=np.uint8)
        # Bright, textured defect block — high residual across the whole region.
        img[140:300, 140:300] = rng.integers(200, 256, (160, 160), dtype=np.uint16).astype(np.uint8)
        mask[140:300, 140:300] = 255
        img_path = tmp_path / f"defect_{index}.png"
        mask_path = tmp_path / f"defect_{index}_mask.png"
        _save_gray(img_path, img)
        Image.fromarray(mask, mode="L").save(mask_path)
        lines.append(_registry_line(f"defect_{index}", img_path, "anomaly", mask_path))

    registry = tmp_path / "sources.jsonl"
    registry.write_text("\n".join(lines) + "\n", encoding="utf-8")
    split = tmp_path / "split.csv"
    build_split(_data_config(tmp_path, registry, split))

    run_dir: Path | None = None
    try:
        run_dir = repo_path(run_model(_MODEL_CONFIG, split, shots=2, seed=17))
        calibrate_run(run_dir)
        evaluate_run(run_dir)
        metrics = load_json(run_dir / "metrics.json")
        manifest = load_json(run_dir / "metrics_manifest.json")

        assert metrics["pixel_auroc"] is not None
        assert manifest["pixel_auroc"]["valid"] is True
        # The heatmap aligns with the defect mask, so pixel AUROC is well above chance.
        assert metrics["pixel_auroc"] > 0.6
    finally:
        if run_dir is not None and run_dir.exists():
            shutil.rmtree(run_dir)
