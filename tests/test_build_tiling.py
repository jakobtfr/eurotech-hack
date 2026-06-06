from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

from src.contracts import validate_split
from src.data.build import build_split


def _registry_line(source_id: str, source_path: Path, label: str) -> str:
    return json.dumps(
        {
            "schema_version": "1.0",
            "source_image_id": source_id,
            "dataset_id": "tiletest",
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
                "dataset_id: tiletest",
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


def test_real_tiling_grids_one_source(tmp_path: Path) -> None:
    array = np.random.default_rng(1).integers(0, 255, size=(900, 900, 3), dtype=np.uint8)
    source_path = tmp_path / "wafer.png"
    Image.fromarray(array, mode="RGB").save(source_path)
    registry = tmp_path / "sources.jsonl"
    registry.write_text(_registry_line("wafer", source_path, "normal") + "\n", encoding="utf-8")
    split = tmp_path / "split.csv"

    build_split(_data_config(tmp_path, registry, split))
    rows = validate_split(split)

    # 900 with tile 448 stride 448 -> origins {0, 448} per axis -> 2x2 grid.
    assert len(rows) == 4
    origins = {(int(row["tile_x"]), int(row["tile_y"])) for row in rows}
    assert origins == {(0, 0), (448, 0), (0, 448), (448, 448)}
    assert all(row["split"] == "train" and row["label"] == "good" for row in rows)
