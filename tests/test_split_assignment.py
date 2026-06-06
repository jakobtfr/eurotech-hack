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
            "dataset_id": "splittest",
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
                "dataset_id: splittest",
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


def test_normals_split_into_train_validation_test(tmp_path: Path) -> None:
    rng = np.random.default_rng(3)
    lines = []
    for index in range(8):
        path = tmp_path / f"normal_{index}.png"
        Image.fromarray(rng.integers(0, 255, (448, 448, 3), dtype=np.uint8), mode="RGB").save(path)
        lines.append(_registry_line(f"normal_{index}", path, "normal"))
    for index in range(2):
        path = tmp_path / f"defect_{index}.png"
        Image.fromarray(rng.integers(0, 255, (448, 448, 3), dtype=np.uint8), mode="RGB").save(path)
        lines.append(_registry_line(f"defect_{index}", path, "anomaly"))
    registry = tmp_path / "sources.jsonl"
    registry.write_text("\n".join(lines) + "\n", encoding="utf-8")
    split = tmp_path / "split.csv"

    build_split(_data_config(tmp_path, registry, split))
    rows = validate_split(split)

    splits = {row["split"] for row in rows}
    assert {"train", "validation", "test"} <= splits  # held-out normals exist for calibration

    # Every source stays in exactly one split (leakage-safe).
    per_source = {}
    for row in rows:
        per_source.setdefault(row["source_image_id"], set()).add(row["split"])
    assert all(len(s) == 1 for s in per_source.values())

    # Only train/good normals are support-eligible; anomalies land in test.
    for row in rows:
        if row["source_image_id"].startswith("defect"):
            assert row["split"] == "test" and row["label"] == "anomaly"
        if str(row["support_eligible"]).lower() in {"true", "1"}:
            assert row["split"] == "train" and row["label"] == "good"
