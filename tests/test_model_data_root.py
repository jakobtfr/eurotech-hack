from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
from PIL import Image

from src.common import load_json, repo_path, write_csv
from src.contracts import SPLIT_FIELDS, validate_split
from src.models.run import run_model


def test_run_model_resolves_relative_split_paths_against_data_root(tmp_path: Path) -> None:
    data_root = tmp_path / "dataset_asset"
    data_root.mkdir()
    image_path = data_root / "normal.png"
    Image.fromarray(np.full((224, 224, 3), 120, dtype=np.uint8), mode="RGB").save(image_path)
    split_path = tmp_path / "split.csv"
    write_csv(split_path, [_row("normal_tile", "normal_source", "normal.png")], SPLIT_FIELDS)

    run_dir: Path | None = None
    try:
        run_rel = run_model("configs/models/pixel_pca.yaml", split_path, shots=1, seed=17, data_root=data_root)
        run_dir = repo_path(run_rel)
        manifest = load_json(run_dir / "run_manifest.json")
        resolved_rows = validate_split(manifest["dataset_split_path"])

        assert resolved_rows[0]["image_path"] == str(image_path)
        assert load_json(run_dir / "config.resolved.json")["input_split_path"] == str(split_path)
    finally:
        if run_dir is not None and run_dir.exists():
            shutil.rmtree(run_dir)


def _row(tile_id: str, source_id: str, image_path: str) -> dict[str, object]:
    return {
        "tile_id": tile_id,
        "source_image_id": source_id,
        "dataset_id": "asset",
        "category": "demo",
        "wafer_id": "",
        "modality": "SEM",
        "split": "train",
        "label": "good",
        "image_path": image_path,
        "mask_path": "",
        "tile_x": 0,
        "tile_y": 0,
        "tile_size": 224,
        "stride": 224,
        "preprocess_id": "rgb_repeat_v1",
        "support_eligible": True,
        "demo_allowed": False,
    }
