from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.common import ContractError
from src.contracts import SPLIT_FIELDS, validate_registry, validate_split


def test_registry_rejects_public_demo_without_verified_license(tmp_path: Path) -> None:
    image = tmp_path / "image.png"
    image.write_bytes(b"placeholder")
    registry = tmp_path / "sources.jsonl"
    registry.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "source_image_id": "example",
                "dataset_id": "stub",
                "wafer_id": None,
                "source_path": str(image),
                "modality": "SEM",
                "source_label": "normal",
                "mask_source_path": None,
                "license_status": "unknown",
                "license_reference": "",
                "demo_allowed": True,
                "notes": "",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ContractError, match="demo_allowed=true"):
        validate_registry(registry)


def test_split_rejects_source_leakage_across_splits(tmp_path: Path) -> None:
    split = tmp_path / "split.csv"
    split.write_text(
        ",".join(SPLIT_FIELDS)
        + "\n"
        + _row("tile_a", "source_a", "train")
        + "\n"
        + _row("tile_b", "source_a", "test")
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ContractError, match="crosses splits"):
        validate_split(split)


def _row(tile_id: str, source_id: str, split: str) -> str:
    values = {
        "tile_id": tile_id,
        "source_image_id": source_id,
        "dataset_id": "stub",
        "category": "scaffold",
        "wafer_id": "",
        "modality": "SEM",
        "split": split,
        "label": "good",
        "image_path": "",
        "mask_path": "",
        "tile_x": "0",
        "tile_y": "0",
        "tile_size": "448",
        "stride": "448",
        "preprocess_id": "rgb_repeat_v1",
        "support_eligible": "true" if split == "train" else "false",
        "demo_allowed": "true",
    }
    return ",".join(values[field] for field in SPLIT_FIELDS)
